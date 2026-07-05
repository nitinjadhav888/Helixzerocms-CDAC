# Technical Implementation: Code, Algorithms, and ML Architecture

This document breaks down the exact technical architecture of HelixZero-CMS for a software and engineering audience. It explains how the biological concepts are translated into code, why we chose specific machine learning algorithms, and the core logic running under the hood.

---

## 1. Why LightGBM? (The Machine Learning Core)

When designing the core Efficacy Predictor (the AI that predicts the exact % gene silencing of a drug), we actively chose **LightGBM** (a Gradient-Boosted Decision Tree framework by Microsoft) over Deep Learning (Neural Networks). 

Here is our engineering logic:

1. **Tabular Data Supremacy:** We do not feed raw RNA sequences (like `AUCG`) into the model. For the modified model, we engineer sequences into a **389-dimensional tabular feature vector** containing explicit chemical knowledge (294 positional category flags + 80 aggregate stats + 1 concentration + 14 engineered features). For the naked baseline, we use a 214-d vector. For structured tabular data, Gradient Boosted Trees consistently outperform Deep Learning.
2. **Interpretability & Feature Importance:** Unlike a neural network "black box," LightGBM allows us to exactly trace which chemical features the model relied on to make its prediction. 
3. **Robustness to Noisy Biology Data:** Biological assay data is inherently noisy. Decision trees are highly resistant to outliers and do not require massive data scaling or normalization.
4. **CPU Inference Speed:** Our server architecture requires us to run Beam Search over thousands of variants in milliseconds. LightGBM allows blazing-fast inference on standard CPUs, entirely eliminating the need for expensive GPU clusters.

### The Model Specification
- **Training Data:** 53,570 chemically modified siRNAs (23,187 hetero-patent + 25,765 HelixZero catalog + 4,618 CMsiRNAdb) mapped to physical laboratory efficacy results.
- **Algorithm:** LightGBM Regressor (1,361 trees).
- **Calibrator:** Isotonic Regression (to perfectly map the raw tree outputs to a strict 0-100% biological bounds).

---

## 2. Feature Extraction (How the AI "Sees" Biology)

The AI cannot read a sequence string like `MSMMFFFSS`. Instead, the `features.py` engine translates the sequence into **389 mathematical dimensions** (Phase 2 modified model) or **214 dimensions** (V4 naked model). 

### The 389-D Vector (Phase 2, Modified Model):
- **294 Dimensions:** Positional chemical-category flags — 7 chemical categories (2'-OMe, 2'-F, LNA, MOE, PS, base mod, other) × 21 positions × 2 strands. This replaces old one-hot encoding with chemistry-aware grouping for better generalization.
- **80 Dimensions:** Aggregate strand statistics — per-strand counts of each chemical category + modification density metrics + GC content + terminal PS flags.
- **1 Dimension:** log₁₀(concentration) — assay condition.
- **14 Dimensions:** Engineered biological features — duplex stability asymmetry, modification-position interactions, ΔTm estimates.

### The 214-D Vector (V4, Naked/Rank Model):
- **84 Dimensions:** Positional one-hot encoding (4 bases × 21 positions).
- **128 Dimensions:** Trinucleotide composition — 64-bin frequency vector for each strand.
- **2 Dimensions:** GC content of sense and antisense strands.

### Code Snippet: Feature Translation
Here is a simplified look at how the code converts chemistry into math. It counts how many times each specific chemical symbol appears and divides by the length of the drug.

```python
def _calculate_mnc(sequence: str, valid_symbols: list) -> list:
    """
    Converts a sequence into a fractional composition vector.
    E.g., If a 21-mer has 7 'M' (2'-OMe) modifications, its 'M' fraction is 0.33.
    """
    length = len(sequence)
    if length == 0:
        return [0.0] * len(valid_symbols)
        
    counts = {sym: 0 for sym in valid_symbols}
    for char in sequence:
        if char in counts:
            counts[char] += 1
            
    # Return as an array of percentages (fractions)
    return [counts[sym] / length for sym in valid_symbols]
```

---

## 3. The Multi-Mod Beam Search Algorithm

When the user asks the system to "Find the best chemistry," the system cannot use brute force. There are 30 possible chemicals and 42 positions on the drug, resulting in billions of combinations. We solved this using a **Beam Search** algorithm.

### How it works:
1. It tries 1 chemical at a time across all positions.
2. It scores them all and keeps only the **Top K** (the "Beam Width", usually 10 to 30).
3. It takes those Top K winners, adds a second chemical, and scores the new combinations.
4. It throws away the losers and keeps the new Top K.

### Code Snippet: The Beam Search Engine
```python
def multi_mod_scan(sense: str, antisense: str, max_mods: int = 14, beam_width: int = 30):
    # Start with the naked sequence
    current_beam = [ (score, naked_sequence_object) ]
    
    for step in range(max_mods):
        next_candidates = []
        
        # Expand every sequence currently surviving in the beam
        for _, seq_obj in current_beam:
            
            # Try adding a modification to every available position
            for pos in range(1, 22):
                for chem in ['M', 'F', 'S']: # Try 2'-OMe, 2'-F, Phosphorothioate
                    
                    new_seq = apply_chemistry(seq_obj, pos, chem)
                    
                    # AI Model Inference
                    raw_score = lightgbm_model.predict(new_seq.features)
                    
                    # Physics Engine Adjustments
                    final_score, penalties = calculate_adjusted_efficacy(raw_score, new_seq)
                    
                    next_candidates.append( (final_score, new_seq) )
                    
        # Sort all generated combinations by highest efficacy
        next_candidates.sort(key=lambda x: x[0], reverse=True)
        
        # Prune: Keep only the Top K (The Beam Width) for the next round
        current_beam = next_candidates[:beam_width]
        
    return current_beam
```

---

## 4. The Biophysics Engine (The Guardrails)

The AI model (LightGBM) is incredibly smart at predicting efficacy, but AI has no concept of "human life" or "toxicity." It might predict that covering the entire drug in heavy armor makes it 100% effective, but biologically, that drug would be physically rejected by the human cell.

To solve this, we built a deterministic **Biophysics Engine** (`biophysics.py`) wrapped around the AI.

### The Logic:
The AI provides a `Raw_Score` (e.g., 85%). The Physics Engine then runs a series of strict Boolean checks based on actual FDA and scientific guidelines. If the sequence breaks a rule of physics, the engine deducts points from the AI's score.

### Code Snippet: Thermodynamic Physics Penalty
```python
def calculate_adjusted_efficacy(raw_score: float, modified_sequence: str):
    total_penalty = 0.0
    
    # 1. Immune System Check (TLR7/8)
    if contains_unmasked_immune_motifs(modified_sequence):
        total_penalty += 15.0  # Massive penalty for triggering inflammation
        
    # 2. Argonaute Physical Loading (RISC Check)
    if has_steric_blockade_in_seed(modified_sequence):
        total_penalty += 24.0  # Drug physically won't fit into cellular machinery
        
    # 3. Nuclease Defense Check
    if not has_armored_termini(modified_sequence):
        total_penalty += 12.0  # Drug will be eaten by blood enzymes
        
    # The final, true clinical score
    adjusted_score = raw_score - total_penalty
    return max(0.0, adjusted_score), total_penalty
```

### Summary for the Engineering Panel
We successfully hybridized two entirely different fields of computer science: 
1. **Data-Driven AI (LightGBM):** Used exclusively for high-dimensional feature interaction to predict raw efficacy.
2. **Deterministic Rules Engine (Physics):** Used to ruthlessly enforce biological boundaries, ensuring the AI never outputs an unsafe hallucination.
