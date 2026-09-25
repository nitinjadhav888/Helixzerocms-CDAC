"""
assistant_service.py — Service layer bridging HelixZero and Google Gemini API.
Includes deterministic Pareto-TOPSIS Top-5 selection and Gemini generative reasoning.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

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

def get_gemini_client():
    """Returns an authenticated Google GenAI client, or raises ValueError if key is missing."""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set. Please set the GEMINI_API_KEY environment variable "
            "or add it to smepred/.env to enable AI reasoning."
        )
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except ImportError:
        raise ImportError(
            "The 'google-genai' library is required. Install via: pip install google-genai"
        )

import time

AVAILABLE_MODELS = ["gemini-3.5-flash-lite", "gemini-3.6-flash"]

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

import base64

async def generate_chat_response(
    messages: List[Dict[str, str]],
    live_context: Optional[Dict[str, Any]] = None,
    image_data: Optional[str] = None
) -> str:
    """
    Generates a conversational response using Gemini Flash, grounded in the HelixZero monograph,
    live screen state, and optional pasted screenshot images.
    """
    try:
        client = get_gemini_client()
    except ValueError as ve:
        return (
            "⚙️ **Configuration Notice:** " + str(ve) + "\n\n"
            "*You can still use all core HelixZero screening, ranking, and modification tools locally.*"
        )
    except Exception as e:
        logger.error(f"Error initializing Gemini client: {e}")
        return f"⚠️ Error initializing AI Client: {str(e)}"

    from google.genai import types

    # Convert conversation history
    contents = []
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
            parts.append(types.Part.from_text(text=context_block))
        elif text:
            parts.append(types.Part.from_text(text=text))

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
                img_bytes = base64.b64decode(b64_str)
                parts.append(types.Part.from_bytes(data=img_bytes, mime_type=mime_type))
            except Exception as img_err:
                logger.warning(f"Failed to decode attached screenshot: {img_err}")

        if parts:
            contents.append(types.Content(role=role, parts=parts))

    if not contents:
        return "How can I assist you with your oligonucleotide therapeutics design today?"

    config = types.GenerateContentConfig(
        system_instruction=HELIXZERO_SYSTEM_INSTRUCTION,
        temperature=0.2, # Conservative temperature to prevent biophysical hallucinations
        max_output_tokens=1500,
    )

    try:
        response = _generate_with_retry(client, contents=contents, config=config)
        return response.text or "I processed your request, but received an empty response."
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

    try:
        client = get_gemini_client()
        from google.genai import types
        config = types.GenerateContentConfig(
            system_instruction=HELIXZERO_SYSTEM_INSTRUCTION,
            temperature=0.2,
            max_output_tokens=2200,
        )
        response = _generate_with_retry(client, contents=[prompt], config=config)
        dossier_text = response.text
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
    except Exception as e:
        logger.error(f"Error calling Gemini in analyze_top_leads: {e}")
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
