"""
Statistical hypothesis testing and significance analysis for multi-seed benchmarks.
Includes paired Student's t-test, Wilcoxon signed-rank test, and Cohen's d effect size.
"""
from typing import Dict, List, Any, Tuple
import numpy as np
from scipy import stats


class SignificanceTester:
    """Computes paired statistical tests comparing proposed scheduler against baselines."""

    @staticmethod
    def compare_samples(
        sample_proposed: List[float],
        sample_baseline: List[float],
        metric_name: str,
        higher_is_better: bool = True,
    ) -> Dict[str, Any]:
        arr_p = np.array(sample_proposed, dtype=float)
        arr_b = np.array(sample_baseline, dtype=float)

        if len(arr_p) != len(arr_b) or len(arr_p) < 2:
            return {"metric": metric_name, "error": "Insufficient or mismatched sample sizes"}

        diff = arr_p - arr_b
        mean_diff = float(np.mean(diff))

        # Check for zero variance
        if np.all(diff == 0):
            return {
                "metric": metric_name,
                "mean_proposed": round(float(np.mean(arr_p)), 4),
                "mean_baseline": round(float(np.mean(arr_b)), 4),
                "mean_difference": 0.0,
                "p_value_ttest": 1.0,
                "p_value_wilcoxon": 1.0,
                "cohens_d": 0.0,
                "statistically_significant": False,
                "significance_label": "ns",
                "superiority": "tie",
            }

        # 1. Paired Student's t-test
        t_res = stats.ttest_rel(arr_p, arr_b)
        p_ttest = float(t_res.pvalue)

        # 2. Wilcoxon signed-rank test
        try:
            w_res = stats.wilcoxon(arr_p, arr_b)
            p_wilcoxon = float(w_res.pvalue)
        except Exception:
            p_wilcoxon = p_ttest

        # 3. Cohen's d effect size
        std_diff = np.std(diff, ddof=1)
        cohens_d = float(mean_diff / std_diff) if std_diff > 1e-9 else 0.0

        is_sig = bool(p_ttest < 0.05)
        if p_ttest < 0.001:
            sig_label = "*** (p < 0.001)"
        elif p_ttest < 0.01:
            sig_label = "** (p < 0.01)"
        elif p_ttest < 0.05:
            sig_label = "* (p < 0.05)"
        else:
            sig_label = "ns (not significant)"

        return {
            "metric": metric_name,
            "mean_proposed": round(float(np.mean(arr_p)), 4),
            "mean_baseline": round(float(np.mean(arr_b)), 4),
            "mean_difference": round(mean_diff, 4),
            "p_value_ttest": round(p_ttest, 6),
            "p_value_wilcoxon": round(p_wilcoxon, 6),
            "cohens_d": round(cohens_d, 3),
            "statistically_significant": is_sig,
            "significance_label": sig_label,
            "superiority": "proposed" if (mean_diff > 0 if higher_is_better else mean_diff < 0) else "baseline",
        }
