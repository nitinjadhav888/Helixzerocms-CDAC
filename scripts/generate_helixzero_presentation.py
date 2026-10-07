"""
generate_helixzero_presentation.py
----------------------------------
Builds a publication-grade, technically deep HTML presentation for Helix-Zero
from the IT / Data Science / Software Engineering perspective.
Emits the generated presentation to:
  1) d:/Helixx/Paper/HelixZero_Software_Presentation.html
  2) d:/Helixx/HelixZero_Software_Architecture_Presentation.html
"""
import sys
import json
from pathlib import Path

# Add scripts directory to sys.path
SCRIPTS_DIR = Path(__file__).parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from presentation_slides_part1 import SLIDES_PART1
from presentation_slides_part2 import SLIDES_PART2
from presentation_deep_dives import DEEP_DIVES

ALL_SLIDES = SLIDES_PART1 + SLIDES_PART2

CSS_STYLES = """
:root {
  --bg: #090b10;
  --bg-gradient: radial-gradient(1200px 500px at 15% -10%, rgba(34,211,238,0.07), transparent),
                 radial-gradient(900px 400px at 90% 0%, rgba(129,140,248,0.07), transparent),
                 #090b10;
  --surface: #111520;
  --surface2: #181d2c;
  --surface3: #20273b;
  --border: #232a3d;
  --border-focus: #38bdf8;
  --accent: #22d3ee;
  --accent-dim: #0ea5e9;
  --accent2: #818cf8;
  --green: #34d399;
  --yellow: #fbbf24;
  --red: #f87171;
  --text: #f8fafc;
  --text-muted: #94a3b8;
  --radius: 10px;
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "IBM Plex Sans", Helvetica, Arial, sans-serif;
  --font-display: "Space Grotesk", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-mono: "JetBrains Mono", "Fira Code", Consolas, monospace;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

html {
  font-size: 15.2px;
}

@media (min-width: 1440px) {
  html { font-size: 15.8px; }
}

@media (min-width: 1920px) {
  html { font-size: 16.5px; }
}

body {
  background: var(--bg-gradient);
  color: var(--text);
  font-family: var(--font-sans);
  height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  -webkit-font-smoothing: antialiased;
  transition: all 0.2s ease;
}

/* TOP HEADER CONTROLS */
header {
  background: linear-gradient(180deg, var(--surface), var(--bg));
  border-bottom: 1px solid var(--border);
  padding: 10px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
  z-index: 50;
  position: relative;
}

header::after {
  content: '';
  position: absolute; left: 0; right: 0; bottom: -1px; height: 1px;
  background: linear-gradient(90deg, var(--accent), var(--accent2), transparent 70%);
  opacity: 0.6;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-icon {
  width: 28px; height: 28px;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 14px rgba(34,211,238,0.4);
}

.brand-icon svg { width: 18px; height: 18px; fill: #04111d; }

.brand-text h1 {
  font-family: var(--font-display);
  font-size: 1.15rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.01em;
}

.brand-text h1 span { color: var(--accent); }
.brand-text p { font-size: 0.72rem; color: var(--text-muted); font-family: var(--font-mono); }

.header-center {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 12px;
}

.live-badge {
  background: #0d2319;
  color: var(--green);
  border: 1px solid #1a4d36;
  font-size: 0.74rem;
  padding: 4px 10px;
  border-radius: 20px;
  font-weight: 600;
  font-family: var(--font-mono);
  display: flex;
  align-items: center;
  gap: 6px;
}

.live-badge::before {
  content: ''; width: 7px; height: 7px; background: var(--green); border-radius: 50%; box-shadow: 0 0 6px var(--green);
}

.slide-counter {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  color: var(--accent);
  background: var(--surface2);
  padding: 5px 12px;
  border-radius: 6px;
  border: 1px solid var(--border);
  font-weight: 600;
}

.slide-select {
  background: var(--surface2);
  border: 1px solid var(--border);
  color: var(--text);
  font-family: var(--font-mono);
  font-size: 0.82rem;
  padding: 6px 12px;
  border-radius: 6px;
  outline: none;
  cursor: pointer;
  max-width: 260px;
}

.slide-select:focus { border-color: var(--accent); }

.header-actions { display: flex; gap: 8px; }

.btn {
  background: var(--surface2);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 0.84rem;
  font-family: var(--font-sans);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn:hover { background: var(--surface3); border-color: var(--accent); color: var(--accent); }
.btn-accent { background: var(--accent); color: #04140f; border-color: var(--accent); font-weight: 600; }
.btn-accent:hover { background: #38e1f0; color: #000; }
.btn-presenter { background: linear-gradient(135deg, #4f46e5, #7c3aed); color: #fff; border-color: #6366f1; font-weight: 600; }
.btn-presenter:hover { background: linear-gradient(135deg, #6366f1, #8b5cf6); color: #fff; box-shadow: 0 0 12px rgba(129,140,248,0.5); }
.btn-active { background: var(--surface3); border-color: var(--accent2); color: var(--accent2); }

/* MAIN SLIDE CONTAINER */
main {
  flex: 1;
  position: relative;
  overflow: hidden;
  padding: 12px 28px 10px;
  display: flex;
  flex-direction: column;
  transition: margin-right 0.25s ease-out;
}

/* Side-by-side mode: when in-deck notes drawer opens, shrink main width without backdrop */
body.notes-open main {
  margin-right: 360px;
}

.slide {
  display: none;
  flex-direction: column;
  height: 100%;
  animation: slideFadeIn 0.2s ease-out forwards;
}

.slide.active { display: flex; }

@keyframes slideFadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

/* SLIDE HEADER */
.slide-header {
  margin-bottom: 8px;
  flex-shrink: 0;
}

.slide-eyebrow {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--accent);
  letter-spacing: 0.12em;
  font-weight: 700;
  margin-bottom: 2px;
  text-transform: uppercase;
}

.slide-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
}

.slide-title {
  font-family: var(--font-display);
  font-size: 1.55rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.015em;
  line-height: 1.25;
}

.badges-group { display: flex; gap: 6px; flex-shrink: 0; flex-wrap: wrap; }

.badge-pill {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  padding: 3px 8px;
  background: var(--surface2);
  border: 1px solid var(--border);
  color: var(--accent);
  border-radius: 4px;
  font-weight: 600;
}

.slide-subtitle {
  font-size: 0.88rem;
  color: var(--text-muted);
  margin-top: 2px;
  line-height: 1.35;
}

/* SLIDE BODY SCROLLABLE AREA */
.slide-body {
  flex: 1;
  overflow-y: auto;
  padding-right: 8px;
  display: flex;
  flex-direction: column;
}

.slide-body::-webkit-scrollbar { width: 6px; }
.slide-body::-webkit-scrollbar-track { background: transparent; }
.slide-body::-webkit-scrollbar-thumb { background: var(--surface3); border-radius: 4px; }
.slide-body::-webkit-scrollbar-thumb:hover { background: var(--border-focus); }

/* FOOTER REFERENCE */
.slide-footer {
  margin-top: auto;
  padding-top: 10px;
  border-top: 1px solid var(--border);
  font-size: 0.82rem;
  color: var(--text-muted);
  font-family: var(--font-mono);
  flex-shrink: 0;
  line-height: 1.4;
}

/* CARD LAYOUTS & GRIDS */
.cards-grid {
  display: grid;
  gap: 12px;
  flex: 1;
}

.cards-1 { grid-template-columns: 1fr; }
.cards-2 { grid-template-columns: 1fr 1fr; }
.cards-3 { grid-template-columns: 1fr 1fr 1fr; }

.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px 15px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 18px rgba(0,0,0,0.3);
  position: relative;
}

.card.border-cyan { border-top: 3px solid var(--accent); }
.card.border-purple { border-top: 3px solid var(--accent2); }
.card.border-emerald { border-top: 3px solid var(--green); }
.card.border-yellow { border-top: 3px solid var(--yellow); }
.card.border-rose { border-top: 3px solid var(--red); }

.card-header { margin-bottom: 6px; }

.card-tag {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--accent);
  display: inline-block;
  margin-bottom: 2px;
}

.card h3 {
  font-family: var(--font-display);
  font-size: 1.08rem;
  font-weight: 700;
  color: #fff;
  line-height: 1.25;
}

.card-desc {
  font-size: 0.86rem;
  color: #cbd5e1;
  line-height: 1.42;
  margin-bottom: 6px;
}

.bullet-list {
  padding-left: 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 0.84rem;
  line-height: 1.42;
  color: #e2e8f0;
}

.bullet-list li strong { color: #fff; }

.metric-row {
  display: flex;
  gap: 10px;
  margin-bottom: 8px;
}

.metric-item {
  flex: 1;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 6px 10px;
  display: flex;
  flex-direction: column;
}

.metric-val {
  font-family: var(--font-mono);
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--accent);
}

.metric-lbl {
  font-size: 0.68rem;
  color: var(--text-muted);
}

.formula-box {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent);
  border-radius: 6px;
  padding: 6px 10px;
  margin: 6px 0 8px;
  font-family: var(--font-mono);
  font-size: 0.86rem;
  color: #e2e8f0;
}

/* CODE BOXES */
.code-box {
  background: #06080e;
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 10px 12px;
  font-family: var(--font-mono);
  font-size: 0.78rem;
  overflow-x: auto;
  line-height: 1.42;
  color: #e2e8f0;
}

.code-kw { color: #f472b6; font-weight: 600; }
.code-func { color: #38bdf8; }
.code-str { color: #a7f3d0; }
.code-comment { color: #64748b; font-style: italic; }
.code-param { color: #fbbf24; }
.code-num { color: #c084fc; }

/* TREE BOXES */
.tree-box {
  background: #06080e;
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 10px 12px;
  font-family: var(--font-mono);
  font-size: 0.76rem;
  line-height: 1.38;
  color: #94a3b8;
  max-height: 360px;
  overflow-y: auto;
}

.tree-box strong { color: var(--accent); }
.tree-box code { color: #e2e8f0; }

/* TABLES */
.table-container {
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: 6px;
}

.tech-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.80rem;
  text-align: left;
}

.tech-table th {
  background: var(--surface2);
  color: var(--accent);
  padding: 7px 10px;
  font-family: var(--font-mono);
  font-size: 0.74rem;
  border-bottom: 1px solid var(--border);
  border-right: 1px solid var(--border);
  font-weight: 700;
}

.tech-table td {
  padding: 6px 10px;
  border-bottom: 1px solid var(--border);
  border-right: 1px solid var(--border);
  color: #e2e8f0;
  line-height: 1.35;
}

.tech-table tr:nth-child(even) { background: rgba(255,255,255,0.015); }
.tech-table tr:hover { background: rgba(34,211,238,0.04); }

/* PIPELINE & FLOWCHART */
.pipeline-diagram {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.pipeline-step {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 0.84rem;
  line-height: 1.4;
}

.step-num {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--accent);
  letter-spacing: 0.1em;
}

.pipeline-step h4 {
  font-size: 0.96rem;
  color: #fff;
  margin: 2px 0 4px;
}

.step-badge {
  display: inline-block;
  font-family: var(--font-mono);
  font-size: 0.74rem;
  color: var(--green);
  background: rgba(52,211,153,0.1);
  padding: 3px 8px;
  border-radius: 4px;
  margin-top: 5px;
}

.pipeline-arrow {
  text-align: center;
  color: var(--accent);
  font-weight: 700;
  font-size: 1.0rem;
  line-height: 0.8;
}

/* VECTOR BAR */
.vector-bar-container {
  display: flex;
  height: 52px;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid var(--border);
  margin-bottom: 12px;
}

.vector-segment {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 4px 10px;
  color: #fff;
  font-size: 0.78rem;
}

.seg-chem { background: linear-gradient(135deg, #0284c7, #0369a1); }
.seg-fm { background: linear-gradient(135deg, #6366f1, #4f46e5); }
.seg-thermo { background: linear-gradient(135deg, #059669, #047857); }
.seg-dose { background: linear-gradient(135deg, #d97706, #b45309); }

.seg-title { font-weight: 700; font-size: 0.78rem; }
.seg-dims { font-family: var(--font-mono); font-size: 0.70rem; opacity: 0.95; }
.seg-desc { font-size: 0.68rem; opacity: 0.85; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* IMAGES & SCREENSHOTS */
.img-container {
  background: #000;
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  max-height: 240px;
}

.slide-img {
  width: 100%;
  height: auto;
  max-height: 240px;
  object-fit: cover;
  transition: transform 0.2s ease;
}

.slide-img:hover {
  transform: scale(1.02);
}


/* INTERACTIVE DEEP-DIVE MODAL & POPUP SYSTEM */
.clickable-metric, .clickable-pill, .clickable-row {
  cursor: pointer;
  position: relative;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.clickable-metric:hover {
  background: rgba(34, 211, 238, 0.14) !important;
  border-color: rgba(34, 211, 238, 0.5) !important;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(34, 211, 238, 0.25);
}
.clickable-metric::after {
  content: '🔍 Details';
  position: absolute;
  bottom: 2px;
  right: 6px;
  font-size: 0.65rem;
  color: var(--accent);
  font-family: var(--font-mono);
  opacity: 0.75;
  letter-spacing: 0.02em;
}
.clickable-metric:hover::after {
  opacity: 1;
  text-decoration: underline;
}

.clickable-row {
  transition: background 0.15s ease;
}
.clickable-row:hover {
  background: rgba(34, 211, 238, 0.12) !important;
  cursor: pointer;
}

.clickable-pill {
  cursor: pointer;
  transition: all 0.18s ease;
}
.clickable-pill:hover {
  filter: brightness(1.2);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.4);
}

.btn-dive-inline {
  background: rgba(34, 211, 238, 0.1);
  color: var(--accent);
  border: 1px solid rgba(34, 211, 238, 0.3);
  font-size: 0.70rem;
  font-family: var(--font-mono);
  padding: 2px 7px;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 6px;
  transition: all 0.15s ease;
}
.btn-dive-inline:hover {
  background: var(--accent);
  color: #04111d;
  box-shadow: 0 0 10px rgba(34, 211, 238, 0.4);
}

/* HORIZONTAL PIPELINE FLOWCHART BAR */
.pipeline-flowchart-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px 12px;
  margin-bottom: 12px;
  gap: 8px;
}
.flow-step-node {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 6px 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.flow-step-node:hover {
  border-color: var(--accent);
  background: rgba(34, 211, 238, 0.08);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(34, 211, 238, 0.15);
}
.flow-step-icon {
  font-size: 1.15rem;
  line-height: 1;
}
.flow-step-info strong {
  display: block;
  font-size: 0.78rem;
  color: #fff;
  white-space: nowrap;
}
.flow-step-info span {
  display: block;
  font-size: 0.68rem;
  color: var(--text-muted);
  font-family: var(--font-mono);
  white-space: nowrap;
}
.flow-node-arrow {
  color: var(--accent);
  font-weight: 700;
  font-size: 1.0rem;
  opacity: 0.7;
}

/* DEEP-DIVE MODAL OVERLAY & DIALOG */
.deep-dive-overlay {
  position: fixed;
  inset: 0;
  background: rgba(5, 7, 12, 0.85);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.deep-dive-overlay.open {
  opacity: 1;
  pointer-events: auto;
}
.deep-dive-modal {
  background: #111520;
  border: 1px solid var(--border-focus);
  border-radius: 12px;
  width: 90%;
  max-width: 820px;
  max-height: 88vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 60px -10px rgba(0,0,0,0.85), 0 0 35px rgba(34,211,238,0.2);
  transform: scale(0.95);
  transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.deep-dive-overlay.open .deep-dive-modal {
  transform: scale(1);
}
.modal-header {
  padding: 14px 18px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(180deg, var(--surface2), var(--surface));
  border-radius: 12px 12px 0 0;
}
.modal-title-group .modal-category {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--accent);
  letter-spacing: 0.08em;
  font-weight: 600;
}
.modal-title-group .modal-title {
  font-family: var(--font-display);
  font-size: 1.20rem;
  font-weight: 700;
  color: #fff;
  margin-top: 2px;
}
.modal-close {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-muted);
  width: 32px;
  height: 32px;
  border-radius: 6px;
  font-size: 1.4rem;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}
.modal-close:hover {
  background: rgba(248,113,113,0.15);
  border-color: var(--red);
  color: var(--red);
}
.modal-body {
  padding: 18px 22px;
  overflow-y: auto;
  font-size: 0.88rem;
  line-height: 1.55;
  color: #cbd5e1;
}
.modal-footer {
  padding: 10px 18px;
  border-top: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--surface);
  border-radius: 0 0 12px 12px;
}
.modal-tip {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-family: var(--font-mono);
}
.modal-tip kbd {
  background: var(--surface2);
  border: 1px solid var(--border);
  padding: 2px 5px;
  border-radius: 4px;
  color: var(--accent);
}

.dive-section {
  margin-bottom: 16px;
}
.dive-section h4 {
  font-family: var(--font-display);
  color: var(--accent);
  font-size: 0.94rem;
  font-weight: 600;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.dive-list {
  list-style: none;
  padding-left: 0;
}
.dive-list li {
  position: relative;
  padding-left: 18px;
  margin-bottom: 8px;
  font-size: 0.86rem;
}
.dive-list li::before {
  content: '▸';
  position: absolute;
  left: 0;
  color: var(--accent);
}
.dive-flow {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  padding: 8px 12px;
  background: rgba(34,211,238,0.05);
  border-radius: 6px;
  border: 1px dashed rgba(34,211,238,0.25);
  margin-top: 6px;
}
.flow-pill {
  background: var(--surface2);
  border: 1px solid var(--border);
  padding: 3px 8px;
  border-radius: 4px;
  font-family: var(--font-mono);
  font-size: 0.76rem;
  color: #fff;
}

/* MENTOR BOX */
.mentor-box {
  background: linear-gradient(135deg, rgba(129,140,248,0.1), rgba(34,211,238,0.04));
  border: 1px solid rgba(129,140,248,0.3);
  border-radius: 6px;
  padding: 10px 14px;
  font-size: 0.86rem;
  line-height: 1.48;
  color: #e2e8f0;
}

.mentor-title {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  color: var(--accent2);
  margin-bottom: 8px;
  font-weight: 600;
}

/* SPEAKER NOTES DRAWER (NON-BLOCKING SIDE-BY-SIDE) */
.notes-drawer {
  position: fixed;
  top: 0;
  right: -360px;
  width: 360px;
  height: 100vh;
  background: #0b0f19;
  border-left: 2px solid var(--border);
  box-shadow: -10px 0 35px rgba(0,0,0,0.6);
  z-index: 100;
  display: flex;
  flex-direction: column;
  transition: right 0.25s ease-out;
}

.notes-drawer.open { right: 0; }

.drawer-header {
  padding: 10px 14px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--surface2);
}

.drawer-title {
  font-family: var(--font-display);
  font-size: 0.98rem;
  font-weight: 700;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 8px;
}

.drawer-title span { color: var(--accent); }

.drawer-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.drawer-close {
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 1.2rem;
  cursor: pointer;
  padding: 4px;
}

.drawer-close:hover { color: #fff; }

.drawer-body {
  flex: 1;
  padding: 14px 16px;
  overflow-y: auto;
  font-size: 0.86rem;
  line-height: 1.5;
  color: #f1f5f9;
}

.drawer-body h4 {
  font-family: var(--font-display);
  font-size: 0.95rem;
  color: var(--accent);
  margin: 10px 0 6px;
}

.drawer-body h4:first-child { margin-top: 0; }
.drawer-body p { margin-bottom: 8px; }
.drawer-body strong { color: #38bdf8; }
.drawer-body em { color: var(--accent2); font-style: normal; font-weight: 600; }

.drawer-body blockquote {
  border-left: 3px solid var(--accent2);
  margin: 8px 0;
  color: #e2e8f0;
  background: var(--surface2);
  padding: 8px 10px;
  border-radius: 0 6px 6px 0;
  font-size: 0.84rem;
}

.drawer-body ul {
  padding-left: 18px;
  margin-bottom: 12px;
}

.drawer-body li {
  margin-bottom: 6px;
}
"""

JS_SCRIPT = """
(function() {
  let currentSlide = 1;
  const totalSlides = document.querySelectorAll('.slide').length;
  const slideSelect = document.getElementById('slideSelect');
  const slideCounter = document.getElementById('slideCounter');
  const notesDrawer = document.getElementById('notesDrawer');
  const notesContent = document.getElementById('notesContent');
  const notesBtn = document.getElementById('toggleNotesBtn');
  const presenterBtn = document.getElementById('presenterBtn');

  // Broadcast channel for dual-screen presenter synchronization
  let broadcast = null;
  try {
    broadcast = new BroadcastChannel('helixzero_presentation_sync');
    broadcast.onmessage = (event) => {
      const data = event.data;
      if (data && data.type === 'NAVIGATE' && data.slideIndex) {
        if (data.slideIndex !== currentSlide) {
          updateSlide(data.slideIndex, false);
        }
      }
    };
  } catch (e) {
    console.warn('BroadcastChannel not supported in this environment');
  }

  // Slide data storage for notes
  window.slideNotes = window.slideNotes || {};

  function updateSlide(newIndex, sendBroadcast = true) {
    if (newIndex < 1) newIndex = 1;
    if (newIndex > totalSlides) newIndex = totalSlides;

    document.querySelectorAll('.slide').forEach((s, idx) => {
      s.classList.toggle('active', (idx + 1) === newIndex);
    });

    currentSlide = newIndex;
    slideCounter.textContent = `Slide ${currentSlide.toString().padStart(2, '0')} / ${totalSlides.toString().padStart(2, '0')}`;
    slideSelect.value = currentSlide;

    // Update notes content
    const noteText = window.slideNotes[currentSlide] || "No speaker notes recorded for this slide.";
    notesContent.innerHTML = noteText;

    // Sync hash
    window.location.hash = `slide-${currentSlide}`;

    // Broadcast change to presenter window if open
    if (sendBroadcast && broadcast) {
      broadcast.postMessage({
        type: 'NAVIGATE',
        slideIndex: currentSlide,
        slideTitle: document.querySelector(`.slide#slide-${currentSlide} .slide-title`)?.textContent || '',
        notesHtml: noteText
      });
    }
  }

  function nextSlide() { updateSlide(currentSlide + 1); }
  function prevSlide() { updateSlide(currentSlide - 1); }

  // Non-blocking in-deck side-by-side notes toggle
  function toggleNotes() {
    const isOpen = notesDrawer.classList.contains('open');
    notesDrawer.classList.toggle('open', !isOpen);
    document.body.classList.toggle('notes-open', !isOpen);
    notesBtn.classList.toggle('btn-active', !isOpen);
  }

  function closeNotes() {
    notesDrawer.classList.remove('open');
    document.body.classList.remove('notes-open');
    notesBtn.classList.remove('btn-active');
  }

  function toggleFullscreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(() => {});
    } else {
      document.exitFullscreen().catch(() => {});
    }
  }

  // DUAL-SCREEN PRESENTER WINDOW (Opens on Laptop Screen)
  function openPresenterWindow() {
    const presenterWindow = window.open('', 'HelixZeroPresenterWindow', 'width=1150,height=750,menubar=no,toolbar=no,location=no,status=no');
    if (!presenterWindow) {
      alert('Popup was blocked! Please allow popups for this page to open the dual-screen presenter notes window.');
      return;
    }

    const currentNotes = window.slideNotes[currentSlide] || "No notes recorded.";
    const currentTitle = document.querySelector(`.slide#slide-${currentSlide} .slide-title`)?.textContent || `Slide ${currentSlide}`;
    const sTag = '<' + 'script>';
    const eTag = '<' + '/script>';
    const eBody = '<' + '/body>';
    const eHtml = '<' + '/html>';

    const presenterHtml = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Presenter Notes — Helix-Zero</title>
<style>
  :root {
    --bg: #0b0f19;
    --surface: #111726;
    --surface2: #192237;
    --border: #232f48;
    --accent: #22d3ee;
    --accent2: #818cf8;
    --green: #34d399;
    --text: #f8fafc;
    --text-muted: #94a3b8;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  header {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 12px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
  }
  .header-left { display: flex; align-items: center; gap: 14px; }
  .badge { background: #0e2b1f; color: var(--green); border: 1px solid #1a4d36; font-size: 0.75rem; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-family: monospace; }
  .counter { font-family: monospace; font-size: 1.05rem; color: var(--accent); font-weight: 700; background: var(--surface2); padding: 4px 12px; border-radius: 6px; }
  .timer-box {
    display: flex; align-items: center; gap: 8px; background: var(--surface2); border: 1px solid var(--border); padding: 4px 12px; border-radius: 6px;
  }
  .timer-val { font-family: monospace; font-size: 1.15rem; color: #fff; font-weight: 700; }
  .timer-btn { background: transparent; border: 1px solid var(--border); color: var(--text-muted); font-size: 0.72rem; padding: 2px 6px; border-radius: 4px; cursor: pointer; }
  .timer-btn:hover { color: #fff; border-color: var(--accent); }
  .header-actions { display: flex; gap: 8px; }
  .btn {
    background: var(--surface2); border: 1px solid var(--border); color: var(--text); padding: 6px 14px; border-radius: 6px; font-size: 0.85rem; cursor: pointer; font-weight: 600;
  }
  .btn:hover { border-color: var(--accent); color: var(--accent); }
  .btn-accent { background: var(--accent); color: #000; border-color: var(--accent); }
  .btn-accent:hover { background: #38e1f0; }
  
  .content-grid {
    flex: 1; display: grid; grid-template-columns: 240px 1fr; overflow: hidden;
  }
  .sidebar {
    background: var(--surface); border-right: 1px solid var(--border); padding: 14px; display: flex; flex-direction: column; gap: 12px; overflow-y: auto;
  }
  .preview-box {
    background: var(--surface2); border: 1px solid var(--border); border-radius: 6px; padding: 10px;
  }
  .preview-label { font-size: 0.68rem; color: var(--accent); font-family: monospace; font-weight: 700; text-transform: uppercase; margin-bottom: 4px; }
  .preview-title { font-size: 0.88rem; font-weight: 700; color: #fff; line-height: 1.3; }
  
  .notes-main {
    padding: 18px 24px; overflow-y: auto; display: flex; flex-direction: column;
  }
  .notes-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }
  .notes-heading { font-size: 1.15rem; font-weight: 700; color: #fff; }
  .font-controls { display: flex; gap: 6px; align-items: center; }
  .font-btn { background: var(--surface2); border: 1px solid var(--border); color: var(--text); width: 26px; height: 26px; border-radius: 4px; cursor: pointer; font-weight: 700; }
  .font-btn:hover { border-color: var(--accent); color: var(--accent); }
  
  .notes-body {
    font-size: 0.98rem; line-height: 1.55; color: #f1f5f9;
  }
  .notes-body p { margin-bottom: 10px; }
  .notes-body strong { color: #38bdf8; }
  .notes-body em { color: var(--accent2); font-style: normal; font-weight: 600; }
  .notes-body blockquote { border-left: 4px solid var(--accent2); background: var(--surface2); padding: 10px 14px; margin: 10px 0; border-radius: 0 6px 6px 0; font-size: 0.92rem; }
  .notes-body ul { padding-left: 18px; margin-bottom: 10px; }
  .notes-body li { margin-bottom: 6px; }
</style>
</head>
<body>
  <header>
    <div class="header-left">
      <div class="badge">PRESENTER VIEW &bull; SYNCED</div>
      <div class="counter" id="pCounter">Slide ${currentSlide.toString().padStart(2, '0')} / ${totalSlides.toString().padStart(2, '0')}</div>
      <div class="timer-box">
        <span class="timer-val" id="pTimer">00:00</span>
        <button class="timer-btn" id="pTimerStart">Start</button>
        <button class="timer-btn" id="pTimerPause">Pause</button>
        <button class="timer-btn" id="pTimerReset">Reset</button>
      </div>
    </div>
    <div class="header-actions">
      <button class="btn" id="pPrevBtn">&larr; Prev</button>
      <button class="btn btn-accent" id="pNextBtn">Next &rarr;</button>
    </div>
  </header>

  <div class="content-grid">
    <div class="sidebar">
      <div class="preview-box">
        <div class="preview-label">Active Slide Title</div>
        <div class="preview-title" id="pActiveTitle">${currentTitle}</div>
      </div>
      <div class="preview-box">
        <div class="preview-label">Dual-Screen Status</div>
        <p style="font-size: 0.80rem; color: var(--text-muted); line-height: 1.4;">
          Keep this window on your <strong>laptop screen</strong>. Place the main presentation on the <strong>projector / connected screen</strong> in fullscreen (Press F).
        </p>
      </div>
      <div class="preview-box">
        <div class="preview-label">Keyboard Controls</div>
        <p style="font-size: 0.78rem; color: #cbd5e1; line-height: 1.35;">
          <strong>&rarr; / Space:</strong> Next Slide<br>
          <strong>&larr;:</strong> Prev Slide<br>
          <strong>P:</strong> Re-focus Presenter
        </p>
      </div>
    </div>

    <div class="notes-main">
      <div class="notes-header-row">
        <div class="notes-heading">Spoken English Speaker Notes</div>
        <div class="font-controls">
          <span style="font-size: 0.75rem; color: var(--text-muted); margin-right: 4px;">Text Size:</span>
          <button class="font-btn" id="fontDec">-</button>
          <button class="font-btn" id="fontInc">+</button>
        </div>
      </div>
      <div class="notes-body" id="pNotesBody">
        ${currentNotes}
      </div>
    </div>
  </div>

  ${sTag}
    const pBroadcast = new BroadcastChannel('helixzero_presentation_sync');
    let pFontSize = 0.98;
    const pNotesBody = document.getElementById('pNotesBody');

    // Timer logic
    let timerSeconds = 0;
    let timerInterval = null;
    function updateTimerDisplay() {
      const mins = Math.floor(timerSeconds / 60).toString().padStart(2, '0');
      const secs = (timerSeconds % 60).toString().padStart(2, '0');
      document.getElementById('pTimer').textContent = mins + ':' + secs;
    }
    document.getElementById('pTimerStart').onclick = () => {
      if (!timerInterval) {
        timerInterval = setInterval(() => { timerSeconds++; updateTimerDisplay(); }, 1000);
      }
    };
    document.getElementById('pTimerPause').onclick = () => {
      clearInterval(timerInterval);
      timerInterval = null;
    };
    document.getElementById('pTimerReset').onclick = () => {
      clearInterval(timerInterval);
      timerInterval = null;
      timerSeconds = 0;
      updateTimerDisplay();
    };
    // Auto-start timer
    document.getElementById('pTimerStart').click();

    // Font scaling
    document.getElementById('fontInc').onclick = () => {
      pFontSize += 0.1;
      pNotesBody.style.fontSize = pFontSize + 'rem';
    };
    document.getElementById('fontDec').onclick = () => {
      if (pFontSize > 0.85) {
        pFontSize -= 0.1;
        pNotesBody.style.fontSize = pFontSize + 'rem';
      }
    };

    // Navigation buttons in presenter
    document.getElementById('pNextBtn').onclick = () => {
      pBroadcast.postMessage({ type: 'NAVIGATE', slideIndex: window.openerSlideIndex + 1 });
    };
    document.getElementById('pPrevBtn').onclick = () => {
      pBroadcast.postMessage({ type: 'NAVIGATE', slideIndex: window.openerSlideIndex - 1 });
    };

    window.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight' || e.key === ' ') {
        e.preventDefault();
        pBroadcast.postMessage({ type: 'NAVIGATE', slideIndex: window.openerSlideIndex + 1 });
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        pBroadcast.postMessage({ type: 'NAVIGATE', slideIndex: window.openerSlideIndex - 1 });
      }
    });

    // Listen for broadcast sync from main window
    window.openerSlideIndex = ${currentSlide};
    pBroadcast.onmessage = (event) => {
      const data = event.data;
      if (data && data.type === 'NAVIGATE' && data.slideIndex) {
        window.openerSlideIndex = data.slideIndex;
        document.getElementById('pCounter').textContent = 'Slide ' + data.slideIndex.toString().padStart(2, '0') + ' / ' + '${totalSlides.toString().padStart(2, '0')}';
        if (data.slideTitle) document.getElementById('pActiveTitle').textContent = data.slideTitle;
        if (data.notesHtml) pNotesBody.innerHTML = data.notesHtml;
      }
    };
  ${eTag}
${eBody}
${eHtml}`;

    presenterWindow.document.open();
    presenterWindow.document.write(presenterHtml);
    presenterWindow.document.close();
  }


  // Deep-Dive Modal Logic
  const deepDiveOverlay = document.getElementById('deepDiveOverlay');
  const modalCategory = document.getElementById('modalCategory');
  const modalTitle = document.getElementById('modalTitle');
  const modalBody = document.getElementById('modalBody');
  const modalCloseBtn = document.getElementById('modalCloseBtn');
  const modalDismissBtn = document.getElementById('modalDismissBtn');

  function openDeepDive(topicKey) {
    if (!window.deepDives || !window.deepDives[topicKey]) {
      console.warn('Deep dive topic not found:', topicKey);
      return;
    }
    const topic = window.deepDives[topicKey];
    if (modalCategory) modalCategory.textContent = topic.category || 'TECHNICAL EVALUATION DEEP DIVE';
    if (modalTitle) modalTitle.textContent = topic.title || 'Technical Breakdown';
    if (modalBody) modalBody.innerHTML = topic.content || '';
    if (deepDiveOverlay) deepDiveOverlay.classList.add('open');
  }

  function closeDeepDive() {
    if (deepDiveOverlay) deepDiveOverlay.classList.remove('open');
  }

  if (modalCloseBtn) modalCloseBtn.addEventListener('click', closeDeepDive);
  if (modalDismissBtn) modalDismissBtn.addEventListener('click', closeDeepDive);
  if (deepDiveOverlay) {
    deepDiveOverlay.addEventListener('click', (e) => {
      if (e.target === deepDiveOverlay) closeDeepDive();
    });
  }

  // Delegated click listener for all elements with data-deep-dive
  document.addEventListener('click', (e) => {
    const target = e.target.closest('[data-deep-dive]');
    if (target) {
      e.preventDefault();
      const topicKey = target.getAttribute('data-deep-dive');
      if (topicKey) openDeepDive(topicKey);
    }
  });

  // Keyboard navigation
  document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight' || e.key === ' ') {
      e.preventDefault();
      nextSlide();
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      prevSlide();
    } else if (e.key === 'n' || e.key === 'N') {
      e.preventDefault();
      toggleNotes();
    } else if (e.key === 'p' || e.key === 'P') {
      e.preventDefault();
      openPresenterWindow();
    } else if (e.key === 'f' || e.key === 'F') {
      e.preventDefault();
      toggleFullscreen();
    } else if (e.key === 'Escape') {
      if (deepDiveOverlay && deepDiveOverlay.classList.contains('open')) {
        e.preventDefault();
        closeDeepDive();
        return;
      }
      closeNotes();
    }
  });

  // Event listeners
  document.getElementById('nextBtn').addEventListener('click', nextSlide);
  document.getElementById('prevBtn').addEventListener('click', prevSlide);
  notesBtn.addEventListener('click', toggleNotes);
  presenterBtn.addEventListener('click', openPresenterWindow);
  document.getElementById('closeDrawerBtn').addEventListener('click', closeNotes);
  document.getElementById('fullscreenBtn').addEventListener('click', toggleFullscreen);

  slideSelect.addEventListener('change', (e) => {
    updateSlide(parseInt(e.target.value, 10));
  });

  // Handle URL hash on load
  const hash = window.location.hash;
  if (hash && hash.startsWith('#slide-')) {
    const idx = parseInt(hash.replace('#slide-', ''), 10);
    if (!isNaN(idx)) {
      updateSlide(idx);
    } else {
      updateSlide(1);
    }
  } else {
    updateSlide(1);
  }

  // Automatic image path fallback resolver
  document.querySelectorAll('img').forEach(img => {
    img.addEventListener('error', function() {
      if (!this.dataset.fallbackTried) {
        this.dataset.fallbackTried = "1";
        if (this.src.includes('/Outputs/')) {
          this.src = this.src.replace('/Outputs/', '/../Outputs/');
        } else if (this.src.includes('../Outputs/')) {
          this.src = this.src.replace('../Outputs/', 'Outputs/');
        }
      }
    });
  });
})();
"""

def generate_presentation_html():
    deep_dives_js = json.dumps(DEEP_DIVES)
    total_count = len(ALL_SLIDES)
    print(f"Total Slides to Compile: {total_count}")

    # Build Slide Dropdown Options
    options_html = []
    for s in ALL_SLIDES:
        title_snippet = s['title'].split(':')[0] if ':' in s['title'] else s['title'][:28]
        options_html.append(f'<option value="{s["id"]}">Slide {s["id"]:02d}: {title_snippet}</option>')
    select_options = "\n".join(options_html)

    # Build Slide HTML blocks and JavaScript notes dictionary
    slides_markup = []
    notes_dict_entries = []

    for s in ALL_SLIDES:
        badges_markup = "".join([f'<span class="badge-pill">{b}</span>' for b in s.get("badges", [])])
        
        active_class = " active" if s["id"] == 1 else ""
        slide_block = f"""
        <!-- SLIDE {s['id']}: {s['title']} -->
        <section class="slide{active_class}" id="slide-{s['id']}">
          <div class="slide-header">
            <div class="slide-eyebrow">{s['eyebrow']}</div>
            <div class="slide-title-row">
              <h2 class="slide-title">{s['title']}</h2>
              <div class="badges-group">{badges_markup}</div>
            </div>
            <p class="slide-subtitle">{s['subtitle']}</p>
          </div>
          <div class="slide-body">
            {s['body_html']}
          </div>
          <div class="slide-footer">
            {s['footer_ref']}
          </div>
        </section>
        """
        slides_markup.append(slide_block)

        # Format paragraphs into HTML in notes
        formatted_notes = ""
        paragraphs = [p.strip() for p in s['notes'].strip().split("\n\n") if p.strip()]
        for p in paragraphs:
            if p.startswith("#"):
                heading = p.lstrip("#").strip()
                formatted_notes += f"<h4>{heading}</h4>"
            elif p.startswith(">"):
                quote = p.lstrip(">").strip()
                formatted_notes += f"<blockquote>{quote}</blockquote>"
            elif p.startswith("-") or p.startswith("*"):
                items = p.split("\n")
                formatted_notes += "<ul>" + "".join([f"<li>{it.lstrip('*- ').strip()}</li>" for it in items]) + "</ul>"
            else:
                formatted_notes += f"<p>{p}</p>"

        notes_dict_entries.append(f'window.slideNotes[{s["id"]}] = {json.dumps(formatted_notes)};')

    all_slides_html = "\n".join(slides_markup)
    all_notes_js = "\n".join(notes_dict_entries)

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Helix-Zero — IT / Data Science / Software Engineering Presentation</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<!-- Clean native typography without external math scripts -->
<style>
{CSS_STYLES}
</style>
</head>
<body>

<!-- TOP APPLICATION HEADER & NAVIGATION -->
<header>
  <div class="brand">
    <div class="brand-icon">
      <svg viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
    </div>
    <div class="brand-text">
      <h1>HELIX<span>ZERO</span></h1>
      <p>HPC-M&BA GROUP &bull; C-DAC PUNE</p>
    </div>
  </div>

  <div class="header-center">
    <div class="live-badge">PRODUCTION PIPELINE</div>
    <div class="slide-counter" id="slideCounter">Slide 01 / {total_count:02d}</div>
    <select class="slide-select" id="slideSelect">
      {select_options}
    </select>
  </div>

  <div class="header-actions">
    <button class="btn" id="prevBtn" title="Previous Slide (ArrowLeft)">&larr; Prev</button>
    <button class="btn btn-accent" id="nextBtn" title="Next Slide (ArrowRight / Space)">Next &rarr;</button>
    <button class="btn btn-presenter" id="presenterBtn" title="Dual-Screen Presenter Window for Laptop Only (P)">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M21 3H3c-1.11 0-2 .89-2 2v12c0 1.1.89 2 2 2h5v2h8v-2h5c1.1 0 1.99-.9 1.99-2L23 5c0-1.11-.9-2-2-2zm0 14H3V5h18v12z"/></svg>
      Presenter Window (Laptop)
    </button>
    <button class="btn" id="toggleNotesBtn" title="Toggle Side-by-Side Notes (N)">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
      Side Notes (N)
    </button>
    <button class="btn" id="fullscreenBtn" title="Toggle Fullscreen (F)">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/></svg>
    </button>
  </div>
</header>

<!-- MAIN SLIDES CONTAINER (SHRINKS SMOOTHLY SIDE-BY-SIDE WHEN NOTES OPEN) -->
<main>
{all_slides_html}
</main>

<!-- SPEAKER NOTES RIGHT SLIDE-OVER DRAWER (NON-BLOCKING, ZERO OVERLAY BACKDROP) -->
<aside class="notes-drawer" id="notesDrawer">
  <div class="drawer-header">
    <div class="drawer-title">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="var(--accent)"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
      Speaker <span>Notes</span>
    </div>
    <div class="drawer-actions">
      <button class="drawer-close" id="closeDrawerBtn" title="Close Notes (Esc)">&times;</button>
    </div>
  </div>
  <div class="drawer-body" id="notesContent">
    <!-- Injected dynamically -->
  </div>
</aside>

<!-- INTERACTIVE TECHNICAL DEEP-DIVE MODAL DIALOG -->
<div class="deep-dive-overlay" id="deepDiveOverlay">
  <div class="deep-dive-modal">
    <div class="modal-header">
      <div class="modal-title-group">
        <span class="modal-category" id="modalCategory">TECHNICAL DEEP DIVE</span>
        <h3 class="modal-title" id="modalTitle">Evaluation Breakdown</h3>
      </div>
      <button class="modal-close" id="modalCloseBtn" title="Close (Esc)">&times;</button>
    </div>
    <div class="modal-body" id="modalBody">
      <!-- Injected dynamically -->
    </div>
    <div class="modal-footer">
      <span class="modal-tip"><kbd>Esc</kbd> or click outside to return to presentation</span>
      <button class="btn btn-accent" id="modalDismissBtn">Return to Slide</button>
    </div>
  </div>
</div>


<script>
window.slideNotes = {{}};
{all_notes_js}
window.deepDives = {deep_dives_js};
{JS_SCRIPT}
</script>

</body>
</html>
"""
    return full_html

def main():
    html_output = generate_presentation_html()
    
    # Save target 1: Paper/HelixZero_Software_Presentation.html (uses ../Outputs/)
    target1 = SCRIPTS_DIR.parent / "Paper" / "HelixZero_Software_Presentation.html"
    target1.parent.mkdir(parents=True, exist_ok=True)
    with open(target1, "w", encoding="utf-8") as f:
        f.write(html_output)
    print(f"[OK] Generated: {target1} ({len(html_output):,} bytes)")

    # Save target 2: HelixZero_Software_Architecture_Presentation.html in workspace root (uses Outputs/)
    html_root = html_output.replace('src="../Outputs/', 'src="Outputs/')
    target2 = SCRIPTS_DIR.parent / "HelixZero_Software_Architecture_Presentation.html"
    with open(target2, "w", encoding="utf-8") as f:
        f.write(html_root)
    print(f"[OK] Generated: {target2} ({len(html_root):,} bytes)")

if __name__ == "__main__":
    main()
