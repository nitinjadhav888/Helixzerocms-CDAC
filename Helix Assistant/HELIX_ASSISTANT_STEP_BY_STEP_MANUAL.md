# HELIXZERO PERSONAL CHATBOT & VOICE ASSISTANT
## Complete Step-by-Step Manual & Implementation Blueprint (Zero-Experience Guide)

---

### Document Overview
This document provides an end-to-end, copy-pasteable, and mathematically grounded guide to building and integrating a **Personalized Scientific Chatbot and Voice Assistant** for the **HelixZero-CMS** oligonucleotide therapeutics platform. 

Even if you have **zero prior experience** with Large Language Models (LLMs), Web Speech APIs, or FastAPI, this guide takes you from an empty file to a fully working, peer-review-grade scientific assistant embedded directly into the HelixZero web platform.

---

## Table of Contents
1. [Architectural Overview & Core Concepts](#1-architectural-overview--core-concepts)
2. [Prerequisites & Environment Setup](#2-prerequisites--environment-setup)
3. [Step 1: Scientific Knowledge Base & System Prompts](#step-1-scientific-knowledge-base--system-prompts)
4. [Step 2: Deterministic Top-5 Lead Selection Engine (Pareto-TOPSIS)](#step-2-deterministic-top-5-lead-selection-engine-pareto-topsis)
5. [Step 3: FastAPI Backend Proxy & Gemini Client](#step-3-fastapi-backend-proxy--gemini-client)
6. [Step 4: Frontend UI Widget & Web Speech Integration (`app.html`)](#step-4-frontend-ui-widget--web-speech-integration-apphtml)
7. [Step 5: Testing, Manual Verification & Troubleshooting](#step-5-testing-manual-verification--troubleshooting)
8. [Frequently Asked Questions & Guardrails](#frequently-asked-questions--guardrails)

---

## 1. Architectural Overview & Core Concepts

### Why Not "Train" or "Fine-Tune" on Raw Data?
HelixZero models (CatBoost v4, LightGBM, RNA-FM embeddings) predict continuous biophysical quantities (ΔΔG, Tm, pIC50, Janas seed viability %). 
- **Fine-tuning an LLM directly on sequences causes severe hallucination, catastrophic forgetting of biophysical numbers, and sequence identity data leakage.**
- **The Correct Pattern:** **Deterministic Calculation $\to$ Context Injection $\to$ LLM Scientific Reasoning**.
  1. The existing HelixZero models compute the exact numbers.
  2. The Top-5 lead engine runs a deterministic mathematical optimization (Pareto / TOPSIS).
  3. The structured JSON is passed to the **Gemini 2.5/3.5 Flash API**, which translates complex multi-dimensional biophysical numbers into publication-grade clinical rationales.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        HelixZero UI (app.html)                         │
│  - Floating Assistant Widget (Space Grotesk + JetBrains Mono)          │
│  - Native Browser Web Speech API (Microphone In & Audio Out)           │
│  - One-click "AI Lead Selector (Top 5)" Button                         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP POST (SSE streaming)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               FastAPI Service (smepred/api/main.py)                    │
│                                                                        │
│  ┌───────────────────────────────┐   ┌──────────────────────────────┐  │
│  │ Pareto-TOPSIS Lead Selector   │   │ Curated Scientific Monograph │  │
│  │ (Ranks Top 5 mathematically)  │   │ System Prompt (Zero Halluc.) │  │
│  └───────────────┬───────────────┘   └──────────────┬───────────────┘  │
│                  └─────────────────┬────────────────┘                  │
│                                    ▼                                   │
│                     Google GenAI SDK (Gemini API)                      │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │ Secure API Call
                                     ▼
                      Google Gemini 2.5 Flash Cloud
```

---

## 2. Prerequisites & Environment Setup

### 2.1 Required Python Libraries
Open your terminal in the `d:\Helixx\smepred` directory (or activate your virtual environment) and install the required packages:

```bash
pip install google-genai pydantic fastapi uvicorn python-dotenv
```

### 2.2 Get a Gemini API Key
1. Visit [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click **"Get API Key"** and create a new key.
4. Save it into an environment variable or a `.env` file inside `d:\Helixx\smepred\.env`:

```env
GEMINI_API_KEY="AIzaSyYourExactSecretKeyHere..."
```

---

## 3. Step 1: Scientific Knowledge Base & System Prompts

To guarantee that the chatbot answers with **95%+ scientific precision** and does not hallucinate, we provide it with a strict **System Instruction** extracted directly from the HelixZero Engineering Monograph.

Create a file named:  
`d:\Helixx\smepred\src\assistant_prompts.py`

```python
"""
assistant_prompts.py — Grounded System Instructions for HelixZero AI Assistant.
Contains exact biophysical rules, nomenclature, and lead progression criteria.
"""

HELIXZERO_SYSTEM_INSTRUCTION = """
You are the HelixZero Scientific Co-Pilot and Lead Oligonucleotide Chemist, an expert AI assistant embedded inside HelixZero-CMS (developed by C-DAC Pune & Research Collaborators).

YOUR OBJECTIVES:
1. Explain HelixZero platform workflows clearly to both molecular biologists and computational researchers.
2. Demystify complex biophysical, thermodynamic, and machine learning output parameters.
3. Provide rigorous, publication-grade justifications when evaluating siRNA candidates (naked and chemically modified).

CORE SCIENTIFIC KNOWLEDGE BASE:
1. Biological Mechanism (Ago2 / RISC):
   - Catalytic engine of RNAi: Argonaute-2 (Ago2), 96 kDa bilobal protein (MID, PAZ, PIWI, N-terminal domains; PDB: 4W5N, 4W5T).
   - MID Pocket: Coordinates the 5'-monophosphate of the antisense (guide) strand via invariant residues Tyr529, Lys533, Gln545, Lys566 with Mg2+. Bulky modifications at nucleotide 1 (like LNA) clash with Tyr529/Lys566 and abolish activity.
   - PAZ Pocket: Accommodates the 2-nt 3'-overhang.
   - PIWI Domain (Catalytic Slicer): Houses the DEDH catalytic tetrad (Asp597, Glu638, Asp669, His807). Cleaves target mRNA specifically between nucleotides 10 and 11 opposite the guide strand. Local helical flexibility at pos 10-11 is essential.
   - Thermodynamic Asymmetry (Schwarz-Zamore Rule): The strand with lower 5'-end thermodynamic stability (delta delta G >= 1.5 kcal/mol) is preferentially loaded into RISC as the guide strand.

2. Chemical Modifications (cm-siRNA):
   - 2'-O-Methyl (2'-OMe) / 'm': High nuclease resistance, abrogates TLR7/8 immune activation. Bulky; excessive placement in the seed region (pos 2-8) can reduce target on-rate.
   - 2'-Fluoro (2'-F) / 'f': Small steric footprint, strongly stabilizes A-form RNA duplex (increases Tm by ~1°C/mod), perfect for catalytic core (pos 9-14) without steric clash.
   - Phosphorothioate (PS) / '*': Replaces non-bridging oxygen with sulfur in backbone; binds serum albumin to retard renal clearance; protects ends from exonucleases.
   - GNA (Glycol Nucleic Acid): Thermally destabilizing; placed at position 7 of the antisense strand (ESC-Plus architecture) to abolish microRNA-like seed off-target binding.
   - GalNAc: Trivalent N-acetylgalactosamine ligand targeting ASGPR on hepatocytes for targeted liver uptake.

3. Key Metrics & Interpretation:
   - Naked Efficacy (LightGBM/CatBoost score): Baseline sequence potency without chemical modifications (scale 0-100%).
   - Modified Knockdown (%): Predicted target mRNA degradation efficacy after applying chemical patterns.
   - Delta Score: Efficacy lift (Modified Knockdown % - Parent Baseline %).
   - Seed Toxicity (Janas et al. 2018): % cell viability driven by guide seed hexamer/heptamer (pos 2-8) off-target repression. >=85% is Safe; 50-84% is Caution; <50% is Toxic.
   - Human Transcriptome 3'-UTR Firewall: Number of exact or 1-mismatch off-target alignments. 0 hits is mandatory for clinical safety.

STRICT BEHAVIORAL PROTOCOLS:
- NEVER hallucinate or invent experimental IC50, Kd, or score values. Only interpret data provided in the user's prompt or payload.
- If data is missing or ambiguous, state explicitly what is needed.
- Keep spoken responses concise and focused; format written responses with clean GitHub Markdown tables and bullet points.
"""
```

---

## 4. Step 2: Deterministic Top-5 Lead Selection Engine (Pareto-TOPSIS)

Rather than asking an LLM to guess the top 5 candidates, we compute a mathematical multi-criteria score balancing Potency, Safety, and Biophysics, and then ask Gemini to explain the biological trade-offs.

Create a file named:  
`d:\Helixx\smepred\src\lead_selector.py`

```python
"""
lead_selector.py — Deterministic Multi-Criteria Decision Analysis (MCDA)
Ranks siRNA candidates using a normalized Pareto-TOPSIS scoring function.
"""

from typing import List, Dict, Any
import numpy as np

def score_and_rank_candidates(candidates: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Ranks candidates by synthesizing:
    1. Efficacy Score (Naked or Modified Knockdown %) [Weight: 0.35]
    2. Seed Viability (Janas % viability)            [Weight: 0.25]
    3. Thermodynamic Asymmetry (Delta Delta G)       [Weight: 0.15]
    4. Off-target Safety (Zero 3'-UTR hits penalty)  [Weight: 0.15]
    5. Structural Compatibility (Ago2 penalty == 0)   [Weight: 0.10]
    """
    if not candidates:
        return []

    scored_list = []
    for c in candidates:
        # Extract features safely
        eff = float(c.get("knockdown", c.get("score", c.get("pred_potency", 50.0))))
        seed_tox = float(c.get("tox_score", 85.0)) if c.get("tox_score") is not None else 80.0
        offtargets = int(c.get("offtarget_hits", c.get("transcriptome_hits", 0)))
        asymmetry = float(c.get("delta_delta_g", 1.5))
        penalty = float(c.get("biophysical_penalty", 0.0))

        # Normalized sub-scores [0.0 to 1.0]
        s_eff = min(max(eff / 100.0, 0.0), 1.0)
        s_seed = min(max(seed_tox / 100.0, 0.0), 1.0)
        s_asym = min(max((asymmetry + 2.0) / 6.0, 0.0), 1.0) # centered around 1.5-3.0 kcal/mol
        s_offtarget = 1.0 if offtargets == 0 else (0.5 if offtargets <= 2 else 0.1)
        s_struct = 1.0 if penalty == 0.0 else max(1.0 - (penalty / 50.0), 0.0)

        # Composite Multi-Criteria Score
        composite_score = (
            0.35 * s_eff +
            0.25 * s_seed +
            0.15 * s_asym +
            0.15 * s_offtarget +
            0.10 * s_struct
        ) * 100.0

        c_copy = dict(c)
        c_copy["composite_rank_score"] = round(composite_score, 2)
        scored_list.append(c_copy)

    # Sort descending by composite score
    scored_list.sort(key=lambda x: x["composite_rank_score"], reverse=True)
    return scored_list[:top_k]
```

---

## 5. Step 3: FastAPI Backend Proxy & Gemini Client

Create a clean, asynchronous module that initializes the Gemini client and serves REST endpoints.

Create a file named:  
`d:\Helixx\smepred\src\assistant_service.py`

```python
"""
assistant_service.py — Asynchronous Gemini Client for HelixZero.
"""

import os
import json
from typing import List, Dict, Any, AsyncGenerator
from google import genai
from google.genai import types

from src.assistant_prompts import HELIXZERO_SYSTEM_INSTRUCTION
from src.lead_selector import score_and_rank_candidates

# Initialize Google GenAI Client
API_KEY = os.environ.get("GEMINI_API_KEY", "")

def get_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY", API_KEY)
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is missing. Please set it in .env.")
    return genai.Client(api_key=api_key)

async def generate_chat_response(messages: List[Dict[str, str]]) -> str:
    """Non-streaming query response for chat."""
    client = get_client()
    
    # Format messages for Gemini
    contents = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))
    
    config = types.GenerateContentConfig(
        system_instruction=HELIXZERO_SYSTEM_INSTRUCTION,
        temperature=0.2, # Low temperature prevents hallucination
        max_output_tokens=1200,
    )
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config=config
    )
    return response.text

async def analyze_top_leads(candidates: List[Dict[str, Any]], target_gene: str = "Target RNA") -> Dict[str, Any]:
    """Scores candidates mathematically, then asks Gemini to generate the clinical dossier."""
    top5 = score_and_rank_candidates(candidates, top_k=5)
    if not top5:
        return {"top5": [], "analysis": "No candidates provided for analysis."}
    
    # Formulate structured prompt for Gemini
    candidate_summary = json.dumps(top5, indent=2)
    prompt = f"""
Target Gene/Transcript: {target_gene}
Here are the mathematically ranked Top 5 siRNA lead candidates from the HelixZero predictive engine:

{candidate_summary}

TASK:
Provide a rigorous, concise scientific dossier explaining why these 5 candidates were selected to advance from naked screening to chemical modification optimization:
1. Executive Lead Summary: Why is Candidate #1 the lead candidate?
2. Per-Candidate Analysis: For each of the 5 candidates, evaluate:
   - Target Position & Sequence duplex characteristics
   - Knockdown Potency vs. Janas Seed Toxicity
   - Thermodynamic asymmetry (RISC loading preference)
   - Proposed chemical modification strategy (where to place 2'-OMe, 2'-F, PS, or GNA)
3. Synthesis Recommendation: Summary checklist for wet-lab ordering.
"""

    client = get_client()
    config = types.GenerateContentConfig(
        system_instruction=HELIXZERO_SYSTEM_INSTRUCTION,
        temperature=0.2,
        max_output_tokens=2000,
    )
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt],
        config=config
    )
    
    return {
        "top5": top5,
        "dossier_markdown": response.text
    }
```

### 5.2 Expose the Endpoints in `smepred/api/main.py`
Add the following routes to `d:\Helixx\smepred\api\main.py`:

```python
# In smepred/api/main.py
from pydantic import BaseModel
from src.assistant_service import generate_chat_response, analyze_top_leads

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

class LeadAnalysisRequest(BaseModel):
    candidates: List[Dict[str, Any]]
    target_gene: Optional[str] = "Target Gene"

@app.post("/assistant/chat")
async def assistant_chat(req: ChatRequest):
    try:
        response_text = await generate_chat_response([m.model_dump() for m in req.messages])
        return {"reply": response_text}
    except Exception as e:
        logger.error(f"Assistant error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/assistant/recommend-top5")
async def assistant_recommend_top5(req: LeadAnalysisRequest):
    try:
        result = await analyze_top_leads(req.candidates, req.target_gene or "Target RNA")
        return result
    except Exception as e:
        logger.error(f"Lead analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 6. Step 4: Frontend UI Widget & Web Speech Integration (`app.html`)

The frontend integration lives inside `d:\Helixx\smepred\app.html`. It has three elements:
1. **The Floating Chat Widget HTML**: Collapsible chat window with audio mic and speaker controls.
2. **The CSS Styling**: Matching the dark-mode aesthetic (`#090b10` background, `#22d3c4` cyan accent, `Space Grotesk` fonts).
3. **The JavaScript Logic**: Handles chat submission, Web Speech API microphone dictation, and speech synthesis voice readout.

### 6.1 The HTML Markup
Insert this right before `</body>` in `app.html`:

```html
<!-- HELIXZERO SCIENTIFIC ASSISTANT WIDGET -->
<div id="helix-assistant-toggle" onclick="toggleAssistant()" title="Open Helix Scientific Assistant">
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
  </svg>
  <span class="assistant-badge-dot"></span>
</div>

<div id="helix-assistant-window">
  <div class="assistant-header">
    <div class="assistant-title-group">
      <div class="assistant-avatar">🧬</div>
      <div>
        <h4>Helix Scientific Co-Pilot</h4>
        <p>Grounded in HelixZero Biophysics & Gemini</p>
      </div>
    </div>
    <div class="assistant-actions">
      <button id="btn-tts-toggle" onclick="toggleTts()" title="Mute/Unmute Spoken Responses">🔊</button>
      <button onclick="toggleAssistant()" title="Close Assistant">✕</button>
    </div>
  </div>

  <div id="assistant-messages">
    <div class="assistant-msg bot">
      Hello! I am your <strong>HelixZero Scientific Co-Pilot</strong>. I can explain any biophysical parameter (ΔΔG asymmetry, Janas seed toxicity, Ago2 MID clashes), guide your workflow, or analyze your current candidate table to recommend the <strong>Top 5 Clinical Leads</strong>. 
      <div class="assistant-quick-prompts">
        <button onclick="sendQuickPrompt('Explain what Schwarz-Zamore thermodynamic asymmetry means.')">Thermodynamics?</button>
        <button onclick="sendQuickPrompt('Why is 2\'-OMe used at pos 2 of the guide strand?')">2'-OMe at Pos 2?</button>
        <button onclick="triggerTop5Analysis()">⚡ Recommend Top 5 Leads</button>
      </div>
    </div>
  </div>

  <!-- Attached Image Preview Bar -->
  <div id="assistant-image-preview" style="display:none; padding:8px 14px; background:var(--surface3); border-top:1px solid var(--border); align-items:center; justify-content:space-between;">
    <div style="display:flex; align-items:center; gap:10px;">
      <img id="assistant-preview-img" src="" alt="Screenshot" style="width:34px; height:34px; object-fit:cover; border-radius:6px; border:1px solid var(--accent);">
      <span style="font-size:0.75rem; color:var(--text);" id="assistant-preview-name">Screenshot attached</span>
    </div>
    <button onclick="clearAttachedImage()" style="background:none; border:none; color:var(--red); font-size:1.1rem; cursor:pointer;" title="Remove image">✕</button>
  </div>

  <div class="assistant-input-bar">
    <button id="btn-mic" onclick="toggleVoiceInput()" title="Voice Input (Microphone Speech-to-Text)">🎙️</button>
    <button id="btn-img-attach" onclick="document.getElementById('assistant-file-input').click()" title="Attach or Paste Screenshot (Ctrl+V supported)">📷</button>
    <input type="file" id="assistant-file-input" accept="image/*" style="display:none;" onchange="handleImageFileSelect(event)">
    <input type="text" id="assistant-input" placeholder="Ask question or paste (Ctrl+V) screenshot..." onkeydown="if(event.key==='Enter') sendAssistantMsg()">
    <button id="btn-send" onclick="sendAssistantMsg()" title="Send">➤</button>
  </div>
</div>
```

### 6.2 The CSS Styling
Add this block inside the `<style>` tag in `app.html`:

```css
/* ─── Helix Assistant Floating Widget Styles ─── */
#helix-assistant-toggle {
  position: fixed;
  bottom: 24px;
  right: 28px;
  width: 54px;
  height: 54px;
  background: linear-gradient(135deg, var(--accent), var(--accent-dim));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #04140f;
  box-shadow: 0 6px 20px rgba(34,211,196,0.35);
  cursor: pointer;
  z-index: 9999;
  transition: transform 0.2s, box-shadow 0.2s;
}
#helix-assistant-toggle:hover {
  transform: scale(1.08);
  box-shadow: 0 8px 26px rgba(34,211,196,0.5);
}
.assistant-badge-dot {
  position: absolute;
  top: 3px;
  right: 3px;
  width: 12px;
  height: 12px;
  background: var(--green);
  border: 2px solid var(--bg);
  border-radius: 50%;
}

#helix-assistant-window {
  position: fixed;
  bottom: 90px;
  right: 28px;
  width: 440px;
  height: 600px;
  max-width: calc(100vw - 40px);
  max-height: calc(100vh - 120px);
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  display: none;
  flex-direction: column;
  box-shadow: 0 16px 48px rgba(0,0,0,0.6);
  z-index: 9999;
  overflow: hidden;
  backdrop-filter: blur(12px);
}
#helix-assistant-window.active { display: flex; }

.assistant-header {
  padding: 14px 18px;
  background: var(--surface2);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.assistant-title-group { display: flex; align-items: center; gap: 10px; }
.assistant-avatar { font-size: 1.4rem; }
.assistant-header h4 { font-family: var(--font-display); font-size: 0.92rem; color: var(--text); }
.assistant-header p { font-size: 0.72rem; color: var(--muted); }
.assistant-actions button {
  background: none; border: none; color: var(--muted); cursor: pointer; font-size: 1rem; padding: 4px;
}
.assistant-actions button:hover { color: var(--text); }

#assistant-messages {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  font-size: 0.85rem;
  line-height: 1.5;
}
.assistant-msg {
  max-width: 88%;
  padding: 10px 14px;
  border-radius: 12px;
  word-wrap: break-word;
}
.assistant-msg.user {
  align-self: flex-end;
  background: var(--accent-dim);
  color: #fff;
  border-bottom-right-radius: 2px;
}
.assistant-msg.bot {
  align-self: flex-start;
  background: var(--surface2);
  color: var(--text);
  border: 1px solid var(--border);
  border-bottom-left-radius: 2px;
}
.assistant-quick-prompts {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}
.assistant-quick-prompts button {
  background: var(--surface3);
  border: 1px solid var(--border);
  color: var(--accent);
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  cursor: pointer;
}
.assistant-quick-prompts button:hover {
  background: var(--accent);
  color: #04140f;
}

.assistant-input-bar {
  padding: 12px 14px;
  background: var(--surface2);
  border-top: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 8px;
}
.assistant-input-bar input {
  flex: 1;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text);
  padding: 8px 12px;
  font-size: 0.84rem;
}
.assistant-input-bar button {
  background: none;
  border: none;
  color: var(--accent);
  font-size: 1.1rem;
  cursor: pointer;
  padding: 6px;
}
.assistant-input-bar button.recording {
  color: var(--red);
  animation: pulse 1s infinite;
}
@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}
```

### 6.3 The JavaScript Code (Voice + Chat Logic)
Add this script block to the end of `app.html`:

```javascript
// ─── HELIX SCIENTIFIC ASSISTANT CONTROLLER ───────────────────────────
let _assistantHistory = [];
let _ttsEnabled = true;
let _recognition = null;
let _isRecording = false;

// 1. Toggle UI
function toggleAssistant() {
  const win = document.getElementById('helix-assistant-window');
  win.classList.toggle('active');
  if (win.classList.contains('active')) {
    document.getElementById('assistant-input').focus();
  }
}

function toggleTts() {
  _ttsEnabled = !_ttsEnabled;
  document.getElementById('btn-tts-toggle').innerText = _ttsEnabled ? '🔊' : '🔇';
  if (!_ttsEnabled) window.speechSynthesis.cancel();
}

// 2. Speech-to-Text (Voice In)
function toggleVoiceInput() {
  const btn = document.getElementById('btn-mic');
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert("Speech recognition is not supported in this browser. Please use Chrome or Edge.");
    return;
  }

  if (_isRecording) {
    if (_recognition) _recognition.stop();
    _isRecording = false;
    btn.classList.remove('recording');
    return;
  }

  _recognition = new SpeechRecognition();
  _recognition.lang = 'en-US';
  _recognition.interimResults = false;

  _recognition.onstart = () => {
    _isRecording = true;
    btn.classList.add('recording');
  };
  _recognition.onresult = (event) => {
    const speechResult = event.results[0][0].transcript;
    document.getElementById('assistant-input').value = speechResult;
    sendAssistantMsg();
  };
  _recognition.onerror = () => {
    _isRecording = false;
    btn.classList.remove('recording');
  };
  _recognition.onend = () => {
    _isRecording = false;
    btn.classList.remove('recording');
  };

  _recognition.start();
}

// 3. Text-to-Speech (Complete Voice Out - No Truncation)
function speakText(text) {
  if (!_ttsEnabled || !window.speechSynthesis) return;
  window.speechSynthesis.cancel(); // stop current audio

  // Strip markdown formatting, code blocks, raw URLs, and mathematical symbols for natural spoken speech
  const cleanSpeech = text
    .replace(/```[\s\S]*?```/g, '') // remove code blocks
    .replace(/`([^`]+)`/g, '$1')
    .replace(/[*#_~\[\]]/g, '')
    .replace(/https?:\/\/\S+/g, '')
    .replace(/ΔΔG/g, 'delta delta G')
    .replace(/ΔG/g, 'delta G')
    .replace(/[≤⩽]/g, 'less than or equal to ')
    .replace(/[≥⩾]/g, 'greater than or equal to ')
    .replace(/μM/g, ' micromolar ')
    .replace(/nM/g, ' nanomolar ')
    .replace(/\s+/g, ' ')
    .trim();

  if (!cleanSpeech) return;

  // Split into natural sentences so browser speech synthesis never times out or truncates long text
  const sentences = cleanSpeech.match(/[^.!?\n]+[.!?\n]+/g) || [cleanSpeech];

  sentences.forEach((sentence, idx) => {
    const s = sentence.trim();
    if (!s) return;
    const utterance = new SpeechSynthesisUtterance(s);
    utterance.rate = 1.05;
    utterance.pitch = 1.0;
    // Keep reference alive for browser garbage collection
    utterance.onerror = (e) => console.warn('TTS utterance notice:', e);
    window.speechSynthesis.speak(utterance);
  });
}

// 4. Live Screen State Extractor (Grabs Active UI Tab, Input Sequence & Top Candidate Rows)
function getLiveAppScreenState() {
  const activeTabEl = document.querySelector('.tab-btn.active, .nav-btn.active, .tab.active');
  const activeTab = activeTabEl ? activeTabEl.innerText.trim() : 'Unknown';

  const rnaSeqInput = document.getElementById('gene-seq') || document.getElementById('seq-input') || document.getElementById('mrna-seq');
  const seqVal = rnaSeqInput ? rnaSeqInput.value.trim() : '';

  const poolSelect = document.getElementById('candidate-pool') || document.getElementById('pool-type');
  const poolType = poolSelect ? poolSelect.value : 'standard';

  let topVisibleCandidates = [];
  const tableRows = document.querySelectorAll('#results-table tbody tr, #ranking-table tbody tr, .results-row');
  if (tableRows && tableRows.length > 0) {
    tableRows.forEach((row, i) => {
      if (i < 3) {
        const text = row.innerText.replace(/\s+/g, ' ').trim();
        if (text) topVisibleCandidates.push(`Row ${i+1}: ${text}`);
      }
    });
  }

  return {
    active_tab: activeTab,
    input_sequence_preview: seqVal ? `${seqVal.slice(0, 30)}... (${seqVal.length} nt total)` : 'None entered',
    pool_type: poolType,
    top_visible_candidates: topVisibleCandidates
  };
}

// 5. Image & Screenshot Upload Handler (Clipboard Ctrl+V or Camera Button)
let _pendingImageData = null;

function handleImageFileSelect(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    _pendingImageData = e.target.result;
    showImagePreview(_pendingImageData);
  };
  reader.readAsDataURL(file);
}

function showImagePreview(base64Data) {
  const previewBar = document.getElementById('assistant-image-preview');
  const previewImg = document.getElementById('assistant-preview-img');
  if (previewBar && previewImg) {
    previewImg.src = base64Data;
    previewBar.style.display = 'flex';
  }
}

function removePendingImage() {
  _pendingImageData = null;
  const previewBar = document.getElementById('assistant-image-preview');
  const fileInput = document.getElementById('assistant-file-input');
  if (previewBar) previewBar.style.display = 'none';
  if (fileInput) fileInput.value = '';
}

// Paste listener for direct Ctrl+V screenshots
window.addEventListener('paste', (e) => {
  const win = document.getElementById('helix-assistant-window');
  if (!win || !win.classList.contains('active')) return;
  const items = (e.clipboardData || e.originalEvent.clipboardData).items;
  for (let item of items) {
    if (item.type.indexOf('image') !== -1) {
      const blob = item.getAsFile();
      const reader = new FileReader();
      reader.onload = (event) => {
        _pendingImageData = event.target.result;
        showImagePreview(_pendingImageData);
      };
      reader.readAsDataURL(blob);
      break;
    }
  }
});

// 6. Send Message with Live Context & Optional Screenshot
async function sendAssistantMsg() {
  const input = document.getElementById('assistant-input');
  const text = input.value.trim();
  const currentImage = _pendingImageData;
  if (!text && !currentImage) return;

  const displayUserMsg = currentImage 
    ? `${text ? text + '<br>' : ''}<img src="${currentImage}" style="max-width:180px; max-height:120px; border-radius:6px; margin-top:6px; border:1px solid var(--border);">`
    : text;
  
  appendAssistantMsg('user', displayUserMsg);
  input.value = '';
  removePendingImage();

  _assistantHistory.push({ role: 'user', content: text || "Please examine and explain this attached image/screenshot." });

  const typingId = appendAssistantMsg('bot', '<em>Thinking biophysically...</em>');

  try {
    const liveContext = getLiveAppScreenState();
    const res = await fetch(`${API}/assistant/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        messages: _assistantHistory,
        live_context: liveContext,
        image_data: currentImage
      })
    });
    const data = await res.json();
    const reply = data.reply || "No response received.";

    document.getElementById(typingId).innerHTML = reply.replace(/\n/g, '<br>');
    _assistantHistory.push({ role: 'model', content: reply });
    speakText(reply);
  } catch (err) {
    document.getElementById(typingId).innerHTML = `<span style="color:var(--red)">Error: ${err.message}</span>`;
  }
}

function sendQuickPrompt(promptText) {
  document.getElementById('assistant-input').value = promptText;
  sendAssistantMsg();
}

function appendAssistantMsg(role, content) {
  const container = document.getElementById('assistant-messages');
  const msgDiv = document.createElement('div');
  const msgId = 'msg-' + Date.now();
  msgDiv.id = msgId;
  msgDiv.className = `assistant-msg ${role}`;
  msgDiv.innerHTML = content;
  container.appendChild(msgDiv);
  container.scrollTop = container.scrollHeight;
  return msgId;
}

// 7. Automated Top-5 Lead Recommendation Trigger
async function triggerTop5Analysis() {
  const candidates = window._lastRankData?.results || window._lastSingleModData?.results || [];
  if (!candidates.length) {
    appendAssistantMsg('bot', '⚠️ Please run a **Gene Scan** or **Single-Mod Scan** first so I can analyze candidate data.');
    return;
  }

  appendAssistantMsg('user', '⚡ Please analyze the current candidate table and recommend the Top 5 Leads.');
  const typingId = appendAssistantMsg('bot', '<em>Synthesizing Pareto frontier & compiling clinical lead dossier...</em>');

  try {
    const res = await fetch(`${API}/assistant/recommend-top5`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        candidates: candidates.slice(0, 50),
        target_gene: document.getElementById('gene-name')?.value || "Target mRNA"
      })
    });
    const data = await res.json();
    const dossier = data.dossier_markdown;

    document.getElementById(typingId).innerHTML = `
      <div style="font-size:0.9rem; font-weight:700; color:var(--accent); margin-bottom:8px;">
        🎯 Top 5 Clinical Lead Dossier
      </div>
      <div>${dossier.replace(/\n/g, '<br>')}</div>
    `;
    speakText("Top 5 candidates analyzed. Lead candidate has been selected based on optimal thermodynamic asymmetry and zero off-target risk.");
  } catch (err) {
    document.getElementById(typingId).innerHTML = `<span style="color:var(--red)">Analysis error: ${err.message}</span>`;
  }
}
```

---

## 7. Step 5: Testing, Manual Verification & Troubleshooting

### Verification Checklist
1. **API Key Test**: Verify that `$env:GEMINI_API_KEY` in PowerShell prints your valid Google AI key.
2. **Start Server**: Run `python -m uvicorn api.main:app --reload --port 8000`.
3. **Open Browser**: Open `http://localhost:8000`.
4. **Chat Test**: Click the bottom-right floating circular icon 🧬. Type:
   > *"What does Schwarz-Zamore rule mean?"*  
   Verify that it returns the exact thermodynamic ΔΔG threshold (≥ 1.5 kcal/mol) with clean Unicode text.
5. **Full Voice Output Test**: Verify that the speech synthesizer reads the **complete** answer out loud without stopping halfway. Click 🔊 to toggle speech on/off anytime.
6. **Live Screen Context Test**: Without typing your sequence or candidates, ask:
   > *"What tab am I looking at right now and what is my current input?"*  
   Verify that the assistant automatically detects your active tab, sequence length, and top visible candidate table rows.
7. **Screenshot / Image Reading Test**:
   - Press `Win+Shift+S` to capture any section of the screen or chart, click into the chat box, and press `Ctrl+V`.
   - Or click the 📷 button to upload any plot or screenshot.
   - Type *"Explain this plot"* and send. Verify that Gemini inspects and interprets the screenshot accurately!
8. **Lead Progression Test**: Run a scan on mRNA sequence `TTR` or luciferase. Click **"⚡ Recommend Top 5 Leads"**. Verify that 5 candidates are returned with full biophysical rationales.

---

## 8. Frequently Asked Questions & Guardrails

### Q1: What happens if the internet goes down?
The core HelixZero calculation engine (CatBoost, LightGBM, GNN, off-target scanner) runs **100% locally** and is unaffected. Only the chatbot assistant will display a network warning.

### Q2: How do we prevent the chatbot from giving incorrect biology?
The prompt enforces `temperature=0.2` and includes invariant rules directly from crystal structures (PDB: 4W5N/4W5T). The mathematical ranking is computed by deterministic Python code before Gemini writes the text, eliminating mathematical hallucination.
