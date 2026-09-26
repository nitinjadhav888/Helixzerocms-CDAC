"""
assistant_service.py — Service layer bridging HelixZero and Google Gemini API.
Includes deterministic Pareto-TOPSIS Top-5 selection and Gemini generative reasoning.
Supports both the official google-genai SDK and zero-dependency direct REST HTTP fallback.
"""

import os
import json
import time
import base64
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

import requests
from dotenv import load_dotenv

# Load .env from smepred directory or workspace root
_smepred_dir = Path(__file__).resolve().parent.parent
_env_path = _smepred_dir / ".env"
_root_env = _smepred_dir.parent / ".env"

if _env_path.exists():
    load_dotenv(_env_path)
elif _root_env.exists():
    load_dotenv(_root_env)
else:
    load_dotenv()

from src.assistant_prompts import HELIXZERO_SYSTEM_INSTRUCTION
from src.lead_selector import score_and_rank_candidates

logger = logging.getLogger("helixzero.assistant")

AVAILABLE_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-flash-latest",
    "gemini-3.1-flash-lite-preview",
    "gemini-3.8-flash",
]

def get_api_key() -> str:
    """Returns GEMINI_API_KEY or raises ValueError if missing."""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set. Please set the GEMINI_API_KEY environment variable "
            "or add it to smepred/.env to enable AI reasoning."
        )
    return api_key

def get_gemini_client():
    """
    Returns an authenticated Google GenAI client if google-genai is installed,
    or None if the library is not installed (direct REST fallback will be used).
    Raises ValueError if GEMINI_API_KEY is missing.
    """
    api_key = get_api_key()
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except ImportError:
        logger.info("google-genai SDK not installed; using direct REST engine.")
        return None

def _generate_via_rest(
    contents_payload: List[Dict[str, Any]],
    system_instruction: str = HELIXZERO_SYSTEM_INSTRUCTION,
    max_output_tokens: int = 1500,
    temperature: float = 0.2,
    max_retries: int = 2
) -> str:
    """
    Direct REST HTTP generation via Google Generative Language v1beta API.
    Zero external SDK dependencies — works seamlessly in all containerized environments.
    """
    api_key = get_api_key()
    url_base = "https://generativelanguage.googleapis.com/v1beta/models"

    body = {
        "contents": contents_payload,
        "systemInstruction": {
            "parts": [{"text": system_instruction}]
        },
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_output_tokens
        }
    }

    last_err = None
    for model_name in AVAILABLE_MODELS:
        url = f"{url_base}/{model_name}:generateContent?key={api_key}"
        for attempt in range(max_retries):
            try:
                resp = requests.post(
                    url,
                    json=body,
                    headers={"Content-Type": "application/json"},
                    timeout=40
                )
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        text_chunks = [p.get("text", "") for p in parts if "text" in p]
                        if text_chunks:
                            return "".join(text_chunks)
                    return "I processed your request, but received an empty response."

                # If 404 (model deprecated/unavailable) or 400, switch to next model immediately
                err_data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
                err_msg = err_data.get("error", {}).get("message", resp.text)
                last_err = RuntimeError(f"HTTP {resp.status_code}: {err_msg}")

                if resp.status_code in [400, 404]:
                    logger.warning(f"Model {model_name} unavailable ({resp.status_code}): {err_msg}. Switching to next candidate model...")
                    break

                if resp.status_code in [429, 500, 503]:
                    logger.warning(f"Transient error on {model_name} (HTTP {resp.status_code}), retrying...")
                    time.sleep(0.5 * (attempt + 1))
            except Exception as e:
                last_err = e
                logger.warning(f"Network error querying {model_name}: {e}. Retrying...")
                time.sleep(0.5 * (attempt + 1))

    if last_err:
        raise last_err
    raise RuntimeError("All available Gemini models failed to generate content.")

def _generate_with_retry(client, contents, config, max_retries: int = 2):
    """Executes generate_content across fallback models with backoff on transient errors."""
    last_err = None
    for model_name in AVAILABLE_MODELS:
        for attempt in range(max_retries):
            try:
                return client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config
                )
            except Exception as e:
                last_err = e
                err_str = str(e).lower()
                transient_keywords = [
                    "503", "unavailable", "429", "404", "disconnect", 
                    "connection", "timeout", "protocol", "reset", "closed", "eos"
                ]
                if any(k in err_str for k in transient_keywords):
                    logger.warning(f"Model {model_name} transient error (attempt {attempt+1}/{max_retries}): {e}. Retrying next option...")
                    time.sleep(0.5 * (attempt + 1))
                    break # try next model
                raise e
    raise last_err

async def generate_chat_response(
    messages: List[Dict[str, str]],
    live_context: Optional[Dict[str, Any]] = None,
    image_data: Optional[str] = None
) -> str:
    """
    Generates a conversational response using Gemini Flash, grounded in the HelixZero monograph,
    live screen state, and optional pasted screenshot images.
    Works with both google-genai SDK and zero-dependency direct REST fallback.
    """
    try:
        client = get_gemini_client()
    except ValueError as ve:
        return (
            "⚙️ **Configuration Notice:** " + str(ve) + "\n\n"
            "*You can still use all core HelixZero screening, ranking, and modification tools locally.*"
        )
    except Exception as e:
        logger.error(f"Error checking Gemini configuration: {e}")
        return f"⚠️ Error initializing AI Client: {str(e)}"

    # Build REST-compatible contents payload
    rest_contents = []
    for i, msg in enumerate(messages):
        role = "user" if msg.get("role") == "user" else "model"
        text = msg.get("content", "").strip()
        parts = []

        # If this is the latest user query and live screen context is provided, enrich prompt
        if role == "user" and i == len(messages) - 1 and live_context:
            context_block = (
                f"\n[CURRENT LIVE HELIXZERO APPLICATION SCREEN STATE]:\n"
                f"- Active View/Tab: {live_context.get('active_tab', 'N/A')}\n"
                f"- Sequence Input: {live_context.get('current_input_sequence', 'N/A')}\n"
                f"- Table Type: {live_context.get('active_pool_type', 'N/A')} ({live_context.get('visible_candidates_count', 0)} candidates present)\n"
                f"- Visible Top Candidates: {json.dumps(live_context.get('top_candidates_preview', []))}\n"
                f"User Question: {text}"
            )
            parts.append({"text": context_block})
        elif text:
            parts.append({"text": text})

        # If an image was pasted/attached with the latest query
        if role == "user" and i == len(messages) - 1 and image_data:
            try:
                mime_type = "image/png"
                if "," in image_data:
                    header, b64_str = image_data.split(",", 1)
                    if "image/jpeg" in header or "image/jpg" in header:
                        mime_type = "image/jpeg"
                    elif "image/webp" in header:
                        mime_type = "image/webp"
                    elif "image/gif" in header:
                        mime_type = "image/gif"
                else:
                    b64_str = image_data
                parts.append({"inlineData": {"mimeType": mime_type, "data": b64_str}})
            except Exception as img_err:
                logger.warning(f"Failed to decode attached screenshot: {img_err}")

        if parts:
            rest_contents.append({"role": role, "parts": parts})

    if not rest_contents:
        return "How can I assist you with your oligonucleotide therapeutics design today?"

    # 1. If SDK is available, attempt SDK generation
    if client is not None:
        try:
            from google.genai import types
            sdk_contents = []
            for item in rest_contents:
                role = item["role"]
                parts = []
                for p in item["parts"]:
                    if "text" in p:
                        parts.append(types.Part.from_text(text=p["text"]))
                    elif "inlineData" in p:
                        raw_bytes = base64.b64decode(p["inlineData"]["data"])
                        parts.append(types.Part.from_bytes(data=raw_bytes, mime_type=p["inlineData"]["mimeType"]))
                if parts:
                    sdk_contents.append(types.Content(role=role, parts=parts))

            config = types.GenerateContentConfig(
                system_instruction=HELIXZERO_SYSTEM_INSTRUCTION,
                temperature=0.2,
                max_output_tokens=1500,
            )
            response = _generate_with_retry(client, contents=sdk_contents, config=config)
            return response.text or "I processed your request, but received an empty response."
        except Exception as sdk_e:
            logger.warning(f"SDK generation failed ({sdk_e}); falling back to zero-dependency REST engine...")

    # 2. Direct REST HTTP fallback (or primary if SDK is absent)
    try:
        return _generate_via_rest(
            contents_payload=rest_contents,
            system_instruction=HELIXZERO_SYSTEM_INSTRUCTION,
            max_output_tokens=1500,
            temperature=0.2
        )
    except Exception as e:
        logger.error(f"Gemini API generation error: {e}")
        err_str = str(e).lower()
        if any(k in err_str for k in ["503", "unavailable", "disconnect", "timeout", "connection", "protocol"]):
            return (
                "⚠️ **Google Cloud High Demand Notice:** Google's Gemini servers are momentarily congested or experienced a connection reset. "
                "Please click Send again in a few seconds. (All local HelixZero tools and calculations remain 100% active.)"
            )
        return f"⚠️ Gemini API Communication Error: {str(e)}"

async def analyze_top_leads(candidates: List[Dict[str, Any]], target_gene: str = "Target RNA") -> Dict[str, Any]:
    """
    Deterministically scores candidates and generates a peer-reviewed clinical lead dossier.
    Works with both google-genai SDK and zero-dependency direct REST fallback.
    """
    top5 = score_and_rank_candidates(candidates, top_k=5)
    if not top5:
        return {
            "top5": [],
            "dossier_markdown": "No candidates available in the current table for lead evaluation."
        }

    # Format simplified payload for the LLM
    clean_leads_for_prompt = []
    for lead in top5:
        clean_leads_for_prompt.append({
            "rank": lead.get("lead_rank"),
            "composite_score": lead.get("composite_rank_score"),
            "position": lead.get("position"),
            "sense_5to3": lead.get("sense", lead.get("modified_sense", "N/A")),
            "antisense_5to3": lead.get("antisense", lead.get("modified_antisense", "N/A")),
            "predicted_efficacy": lead.get("parsed_efficacy"),
            "seed_viability_pct": lead.get("parsed_seed_viability"),
            "asymmetry_ddg_kcal_mol": lead.get("parsed_asymmetry_ddg"),
            "offtarget_hits": lead.get("parsed_offtargets"),
            "biophysical_penalty": lead.get("parsed_penalty"),
            "modifications": lead.get("modifications_summary", lead.get("mod_symbol", "Naked Baseline"))
        })

    prompt_data = json.dumps(clean_leads_for_prompt, indent=2)

    prompt = f"""
TARGET GENE / TRANSCRIPT: {target_gene}

The deterministic Pareto-TOPSIS scoring engine has selected the following Top 5 Lead Candidates from the active candidate pool:

```json
{prompt_data}
```

TASK:
Provide a publication-grade, clinical lead progression dossier evaluating these 5 candidates:
1. Executive Lead Assessment: Formally justify why Lead #1 has been designated as the primary clinical candidate.
2. Per-Candidate Evaluation (Leads 1 to 5):
   - Sequence and target site accessibility
   - Efficacy vs. Janas seed toxicity safety margin (>=85% safe)
   - RISC loading preference based on thermodynamic asymmetry (Schwarz-Zamore delta delta G)
   - Chemical Modification Progression: Where should 2'-OMe, 2'-F, phosphorothioate (PS), or GNA (pos 7) be introduced to optimize stability and abolish off-target risks?
3. Wet-Lab Synthesis Recommendation Checklist: Concise operational recommendations before ordering solid-phase synthesis.
"""

    dossier_text = None

    # Check API key first
    try:
        client = get_gemini_client()
    except ValueError as ve:
        # Fallback if API key is not yet set
        dossier_text = (
            f"### ⚙️ Deterministic Multi-Criteria Top 5 Leads for {target_gene}\n\n"
            f"> *Note: Gemini API Key is not yet configured ({str(ve)}). Displaying deterministic Pareto ranking.* \n\n"
        )
        for lead in top5:
            dossier_text += (
                f"- **Lead #{lead.get('lead_rank')}** (Pos {lead.get('position', 'N/A')}): "
                f"Composite Score: **{lead.get('composite_rank_score')}** | "
                f"Potency: {lead.get('parsed_efficacy')}% | "
                f"Seed Viability: {lead.get('parsed_seed_viability')}% | "
                f"Asymmetry ΔΔG: {lead.get('parsed_asymmetry_ddg')} kcal/mol | "
                f"Off-targets: {lead.get('parsed_offtargets')}\n"
            )
        return {"top5": top5, "dossier_markdown": dossier_text}

    # 1. Try SDK if client is available
    if client is not None:
        try:
            from google.genai import types
            config = types.GenerateContentConfig(
                system_instruction=HELIXZERO_SYSTEM_INSTRUCTION,
                temperature=0.2,
                max_output_tokens=2200,
            )
            response = _generate_with_retry(client, contents=[prompt], config=config)
            dossier_text = response.text
        except Exception as sdk_err:
            logger.warning(f"SDK analyze_top_leads failed ({sdk_err}); trying REST engine...")

    # 2. Try REST engine if SDK was not used or failed
    if not dossier_text:
        try:
            rest_contents = [{"role": "user", "parts": [{"text": prompt}]}]
            dossier_text = _generate_via_rest(
                contents_payload=rest_contents,
                system_instruction=HELIXZERO_SYSTEM_INSTRUCTION,
                max_output_tokens=2200,
                temperature=0.2
            )
        except Exception as e:
            logger.error(f"Error calling Gemini REST in analyze_top_leads: {e}")
            dossier_text = (
                f"### 🎯 Top 5 Lead Recommendations for {target_gene}\n\n"
                f"> *The Pareto-TOPSIS scoring completed successfully. Google AI servers are momentarily experiencing high demand for narrative generation.* \n\n"
            )
            for lead in top5:
                dossier_text += (
                    f"- **Lead #{lead.get('lead_rank')}** (Position {lead.get('position', '—')}): "
                    f"Composite Score: **{lead.get('composite_rank_score')}** | "
                    f"Knockdown: **{lead.get('parsed_efficacy')}%** | "
                    f"Seed Viability: **{lead.get('parsed_seed_viability')}%** | "
                    f"Asymmetry ΔΔG: **{lead.get('parsed_asymmetry_ddg')} kcal/mol** | "
                    f"Off-targets: **{lead.get('parsed_offtargets')}**\n"
                )

    return {
        "top5": top5,
        "dossier_markdown": dossier_text
    }
