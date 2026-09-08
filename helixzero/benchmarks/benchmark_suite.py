"""
helixzero.benchmarks.benchmark_suite
====================================
Standardized External Benchmark Runner for HelixZero.

Evaluates against:
1. Roche JAK1 Unique Chemical Pattern Subset (N = 191, WO2024256707A1)
2. Alnylam APP Chemically Diverse Subset (N = 343, WO2020132227A2)
3. Molecular Therapy 15-siRNA Clinical Panel (N = 15)

Compares directly with published FENNEC Table 1 & Table 2 metrics.
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Any
import numpy as np
import pandas as pd

from helixzero.api.client import HelixZero
from helixzero.ontology.tokenizer import parse_sirna_sequence
from helixzero.training.validation import compute_comprehensive_metrics

BENCHMARKS_DATA_DIR = Path(__file__).parent.parent.parent / "benchmarks"


# Published Baseline Literature Numbers (From FENNEC Tables 1 & 2, bioRxiv August 2026)
PUBLISHED_LITERATURE_BASELINES = {
    "APP_343": [
        {"Model": "FENNEC (Roche/TUM 2026)", "Spearman_rho": 0.427, "Pearson_r": 0.402, "ROC_AUC_25pct": 0.674, "PR_AUC_25pct": 0.384},
        {"Model": "RNAxs Vienna (Gruber et al.)", "Spearman_rho": 0.297, "Pearson_r": 0.271, "ROC_AUC_25pct": 0.620, "PR_AUC_25pct": 0.328},
        {"Model": "cm-siRNA-pred (Tang et al. 2026)", "Spearman_rho": 0.188, "Pearson_r": 0.188, "ROC_AUC_25pct": 0.581, "PR_AUC_25pct": 0.296},
        {"Model": "OligoFormer 1-20 (Wang et al. 2024)", "Spearman_rho": 0.092, "Pearson_r": 0.111, "ROC_AUC_25pct": 0.509, "PR_AUC_25pct": 0.254},
        {"Model": "OligoFormer 0-19 (Wang et al. 2024)", "Spearman_rho": 0.078, "Pearson_r": 0.082, "ROC_AUC_25pct": 0.537, "PR_AUC_25pct": 0.543},
    ],
    "JAK1_191": [
        {"Model": "FENNEC (Roche/TUM 2026)", "Spearman_rho": 0.506, "Pearson_r": 0.508, "ROC_AUC_25pct": 0.667, "PR_AUC_25pct": 0.416},
        {"Model": "OligoFormer 0-19 (Wang et al. 2024)", "Spearman_rho": 0.302, "Pearson_r": 0.304, "ROC_AUC_25pct": 0.638, "PR_AUC_25pct": 0.399},
        {"Model": "OligoFormer 1-20 (Wang et al. 2024)", "Spearman_rho": 0.255, "Pearson_r": 0.253, "ROC_AUC_25pct": 0.573, "PR_AUC_25pct": 0.296},
        {"Model": "RNAxs Vienna (Gruber et al.)", "Spearman_rho": 0.226, "Pearson_r": 0.185, "ROC_AUC_25pct": 0.693, "PR_AUC_25pct": 0.415},
        {"Model": "cm-siRNA-pred (Tang et al. 2026)", "Spearman_rho": 0.144, "Pearson_r": 0.158, "ROC_AUC_25pct": 0.545, "PR_AUC_25pct": 0.329},
    ]
}


class BenchmarkSuite:
    """
    Automated benchmark suite for evaluating HelixZero models on published datasets.
    """

    def __init__(self, engine: HelixZero = None):
        self.engine = engine or HelixZero()

    def run_jak1_benchmark(self) -> pd.DataFrame:
        """Evaluates on Roche JAK1 N=191 dataset."""
        csv_path = BENCHMARKS_DATA_DIR / "fennec_jak1_191_dataset.csv"
        df = pd.read_csv(csv_path)

        y_true = df["knockdown_pct"].values
        concs = df["concentration_nM"].values

        preds_ens, preds_cb, preds_hier, preds_gnn = [], [], [], []

        for _, r in df.iterrows():
            s_slots = parse_sirna_sequence(r["sense_seq"], r["sense_mods"])
            a_slots = parse_sirna_sequence(r["anti_seq"], r["anti_mods"])

            final_kd, _, _, _, p_cb, p_hier, p_gnn, _ = self.engine.ensemble.predict(
                s_slots, a_slots, conc_nM=float(r["concentration_nM"])
            )
            preds_ens.append(final_kd)
            preds_cb.append(p_cb)
            preds_hier.append(p_hier)
            preds_gnn.append(p_gnn)

        results = [
            {"Dataset": "JAK1 (N=191)", "Model": "HelixZero Ensemble", **compute_comprehensive_metrics(y_true, np.array(preds_ens))},
            {"Dataset": "JAK1 (N=191)", "Model": "HelixZero CatBoost Multi-Slot", **compute_comprehensive_metrics(y_true, np.array(preds_cb))},
            {"Dataset": "JAK1 (N=191)", "Model": "HelixZero Hierarchical Engine", **compute_comprehensive_metrics(y_true, np.array(preds_hier))},
            {"Dataset": "JAK1 (N=191)", "Model": "HelixZero GNN Engine", **compute_comprehensive_metrics(y_true, np.array(preds_gnn))},
        ]
        return pd.DataFrame(results)

    def run_app_benchmark(self) -> pd.DataFrame:
        """Evaluates on Alnylam APP N=343 dataset."""
        csv_path = BENCHMARKS_DATA_DIR / "fennec_app_343_dataset.csv"
        df = pd.read_csv(csv_path)

        y_true = df["efficacy"].values
        concs = df["concentration_nM"].fillna(10.0).values

        preds_ens, preds_cb, preds_hier, preds_gnn = [], [], [], []

        for _, r in df.iterrows():
            s_slots = parse_sirna_sequence(r["base_sense"], r["sense"])
            a_slots = parse_sirna_sequence(r["base_antisense"], r["antisense"])

            final_kd, _, _, _, p_cb, p_hier, p_gnn, _ = self.engine.ensemble.predict(
                s_slots, a_slots, conc_nM=float(r.get("concentration_nM", 10.0) or 10.0)
            )
            preds_ens.append(final_kd)
            preds_cb.append(p_cb)
            preds_hier.append(p_hier)
            preds_gnn.append(p_gnn)

        results = [
            {"Dataset": "APP (N=343)", "Model": "HelixZero Ensemble", **compute_comprehensive_metrics(y_true, np.array(preds_ens))},
            {"Dataset": "APP (N=343)", "Model": "HelixZero CatBoost Multi-Slot", **compute_comprehensive_metrics(y_true, np.array(preds_cb))},
            {"Dataset": "APP (N=343)", "Model": "HelixZero Hierarchical Engine", **compute_comprehensive_metrics(y_true, np.array(preds_hier))},
            {"Dataset": "APP (N=343)", "Model": "HelixZero GNN Engine", **compute_comprehensive_metrics(y_true, np.array(preds_gnn))},
        ]
        return pd.DataFrame(results)

    def run_full_suite(self) -> Dict[str, pd.DataFrame]:
        """Runs all benchmarks and outputs comparative tables."""
        df_jak = self.run_jak1_benchmark()
        df_app = self.run_app_benchmark()

        # Combine with published baselines
        pub_jak = pd.DataFrame([{"Dataset": "JAK1 (N=191)", **m} for m in PUBLISHED_LITERATURE_BASELINES["JAK1_191"]])
        pub_app = pd.DataFrame([{"Dataset": "APP (N=343)", **m} for m in PUBLISHED_LITERATURE_BASELINES["APP_343"]])

        full_jak = pd.concat([df_jak, pub_jak], ignore_index=True)
        full_app = pd.concat([df_app, pub_app], ignore_index=True)

        return {
            "JAK1_191": full_jak,
            "APP_343": full_app
        }
