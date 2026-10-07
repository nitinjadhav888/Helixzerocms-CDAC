import re
from pathlib import Path

def audit():
    path = Path("HelixZero_Software_Architecture_Presentation.html")
    assert path.exists(), "HTML file missing!"
    content = path.read_text(encoding="utf-8")
    
    print(f"File size: {len(content):,} bytes")
    
    # 1. Slide count
    slides = re.findall(r'<section class="slide[^"]*" id="slide-(\d+)">', content)
    print(f"Total slides found: {len(slides)}")
    assert len(slides) == 31, f"Expected 31 slides, got {len(slides)}"
    
    # 2. Check Slide 30
    assert "Expert Validation" not in content[:content.find('id="slide-30"')] and "Expert Validation" not in content[content.find('id="slide-30"'):content.find('id="slide-31"')], "Slide 30 still has 'Expert Validation'!"
    assert "Literature Grounding" in content[content.find('id="slide-30"'):content.find('id="slide-31"')], "Slide 30 missing 'Literature Grounding'!"
    assert "Published Work &amp; Statements in Papers" in content or "Published Work & Statements in Papers" in content, "Slide 30 missing 'Published Work & Statements in Papers'!"
    assert "Translation &amp; Alignment to Helix-Zero" in content or "Translation & Alignment to Helix-Zero" in content, "Slide 30 missing 'Translation & Alignment to Helix-Zero'!"
    print("[PASS] Slide 30 structure & framing verified.")
    
    # 3. Check Slide 28 benchmark explanation in notes
    s28_match = re.search(r'window\.slideNotes\[28\]\s*=\s*"([^"]+)"', content)
    assert s28_match, "Slide 28 notes missing!"
    s28_notes = s28_match.group(1)
    assert "inter-laboratory batch noise" in s28_notes or "batch noise" in s28_notes, "Slide 28 missing batch noise explanation!"
    assert "0.6776" in s28_notes, "Slide 28 missing 0.6776!"
    assert "0.8359" in s28_notes, "Slide 28 missing 0.8359!"
    assert "Davis" in s28_notes, "Slide 28 missing Davis et al.!"
    print("[PASS] Slide 28 notes explanation for 0.6776 vs 0.8359 verified.")
    
    # 4. Check typography scaling & modal system
    assert "font-size: 15.2px;" in content or "font-size: 15.8px;" in content, "Calibrated base font size missing!"
    assert "deep-dive-overlay" in content, "Deep dive overlay modal markup missing!"
    assert "window.deepDives" in content, "Deep dive technical registry missing!"
    print("[PASS] Calibrated typography & deep-dive modal system verified.")
    
    # 5. Check Presenter Window & side-by-side notes
    assert "BroadcastChannel('helixzero_presentation_sync')" in content, "BroadcastChannel missing!"
    assert "openPresenterWindow" in content, "openPresenterWindow missing!"
    assert "body.notes-open main" in content, "Non-blocking side-by-side CSS missing!"
    print("[PASS] Dual-screen presenter mode & side-by-side notes verified.")
    
    # 6. Verify all 31 slide notes are present
    notes_count = len(re.findall(r'window\.slideNotes\[\d+\]\s*=', content))
    print(f"Slide notes entries: {notes_count} / 31")
    assert notes_count == 31, f"Expected 31 notes entries, got {notes_count}"
    print("[ALL AUDIT CHECKS PASSED PERFECTLY!]")

if __name__ == "__main__":
    audit()
