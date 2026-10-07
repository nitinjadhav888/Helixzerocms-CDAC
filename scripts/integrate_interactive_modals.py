import re
from pathlib import Path

scripts_dir = Path("d:/Helixx/scripts")

def update_generator():
    gen_file = scripts_dir / "generate_helixzero_presentation.py"
    content = gen_file.read_text(encoding="utf-8")
    
    # 1. Add import of DEEP_DIVES if not present
    if "from presentation_deep_dives import DEEP_DIVES" not in content:
        content = content.replace(
            "from presentation_slides_part2 import SLIDES_PART2",
            "from presentation_slides_part2 import SLIDES_PART2\nfrom presentation_deep_dives import DEEP_DIVES"
        )
    
    # 2. Adjust base font sizes (calibrated ~5% boost as requested: 'only little more not much only little')
    old_font_rule = """html {
  font-size: 14.5px;
}

@media (min-width: 1440px) {
  html { font-size: 15px; }
}

@media (min-width: 1920px) {
  html { font-size: 16px; }
}"""

    new_font_rule = """html {
  font-size: 15.2px;
}

@media (min-width: 1440px) {
  html { font-size: 15.8px; }
}

@media (min-width: 1920px) {
  html { font-size: 16.5px; }
}"""
    if old_font_rule in content:
        content = content.replace(old_font_rule, new_font_rule)
        print("Updated font size scaling.")
    
    # 3. Add Modal and Flowchart CSS styles before end of CSS_STYLES
    modal_css = """
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
"""
    if "/* INTERACTIVE DEEP-DIVE MODAL & POPUP SYSTEM */" not in content:
        content = content.replace("/* MENTOR BOX */", modal_css + "\n/* MENTOR BOX */")
        print("Added modal and flowchart CSS styles.")
        
    # 4. Add Modal HTML markup before </main> or after notesDrawer
    modal_html = """
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
"""
    if 'id="deepDiveOverlay"' not in content:
        content = content.replace("</aside>", "</aside>\n" + modal_html)
        print("Added modal HTML overlay markup.")
        
    # 5. Add window.deepDives JSON injection
    if "window.deepDives = " not in content:
        content = content.replace(
            "window.slideNotes = {{}};\n{all_notes_js}",
            "window.slideNotes = {{}};\n{all_notes_js}\nwindow.deepDives = {deep_dives_js};"
        )
        # Update function signature to inject deep_dives_js
        content = content.replace(
            "def generate_presentation_html():",
            "def generate_presentation_html():\n    deep_dives_js = json.dumps(DEEP_DIVES)"
        )
        print("Added window.deepDives data binding.")

    # 6. Add modal JS handlers into JS_SCRIPT
    modal_js = """
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
"""
    if "// Deep-Dive Modal Logic" not in content:
        content = content.replace(
            "  // Keyboard navigation",
            modal_js + "\n  // Keyboard navigation"
        )
        # Update keydown to close modal on Escape
        content = content.replace(
            "    } else if (e.key === 'Escape') {\n      closeNotes();\n    }",
            "    } else if (e.key === 'Escape') {\n      if (deepDiveOverlay && deepDiveOverlay.classList.contains('open')) {\n        e.preventDefault();\n        closeDeepDive();\n        return;\n      }\n      closeNotes();\n    }"
        )
        print("Added modal JS event handling.")

    gen_file.write_text(content, encoding="utf-8")
    print("Saved generate_helixzero_presentation.py")

if __name__ == "__main__":
    update_generator()
