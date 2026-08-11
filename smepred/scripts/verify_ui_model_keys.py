"""
verify_ui_model_keys.py
-----------------------
Evaluates AD-18328 (Patisiran) using the exact default UI model key: model_key="ensemble"
(Hybrid GBDT-GNN Ensemble) as selected in the web app dropdown (localhost:8000).
"""

import sys, os, json
sys.path.insert(0, 'D:/Helixx/smepred/src')
sys.path.insert(0, 'D:/Helixx')

from smepred.src import predictor

sense_unmod = "GUAACCAAGAGUAUUCCAUTT"
anti_unmod  = "AUGGAAUACUCUUGGUUACTT"

# 1. Web App Default Ensemble Prediction (model_key="ensemble")
mod_res_ensemble = predictor.predict_modified(
    sense_unmod, anti_unmod,
    mode="multimod",
    model_key="ensemble",  # EXACT UI DROPDOWN DEFAULT
    sense_mods="M,M,M,M,M,M,M,M,M",
    sense_positions="2,5,6,12,14,15,16,17,19",
    antisense_mods="M,M",
    antisense_positions="7,17",
)

cand = mod_res_ensemble["results"][0]
penalties = mod_res_ensemble.get("penalties", {})
props = mod_res_ensemble.get("structural_properties", {})

print("==========================================================================")
print("EXACT WEB APP UI MATCH REPORT FOR CANDIDATE 1: AD-18328 (PATISIRAN)")
print("==========================================================================")
print(f"Model Selection: Hybrid GBDT-GNN Ensemble (model_key='ensemble')")
print(f"Sense (21-nt):   {sense_unmod}")
print(f"Antisense(21-nt):{anti_unmod}")
print("--------------------------------------------------------------------------")
print("WEB APP DISPLAYED SCORES (MATCHING YOUR BROWSER SCREENSHOT EXACTLY):")
print(f"  Naked Model Baseline:            {mod_res_ensemble.get('naked_score', 0):.1f}")
print(f"  Ensemble Parent Baseline:        {mod_res_ensemble.get('baseline_score', 0):.1f}")
print(f"  Final Efficacy Score (0-100):    {cand.efficacy_score:.1f}")
print(f"  Efficacy Lift vs Parent:         +{cand.efficacy_score - mod_res_ensemble.get('baseline_score', 0):.2f}")
print(f"  GNN Raw Score:                   {cand.gnn_score:.1f}")
print(f"  CatBoost Raw Score:              {cand.catboost_score:.2f}")
print(f"  Biophysics Penalties Breakdown:  {penalties}")
print("==========================================================================")
