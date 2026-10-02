"""
Evaluation metrics for Electronic Support (ES) surveillance and smart scan schedulers.
Computes TTFI, intercept rates, periodic revisit rates, dwell efficiency, fairness, and retuning overhead.
"""
from typing import Dict, List, Any, Optional
import numpy as np
from sim.receiver import ReceiverTelemetry
from sim.emitter import PeriodicRadarEmitter


class EWMetricsCalculator:
    """
    Evaluates an episode's telemetry and ground truth history to produce standardized EW metrics.
    """

    @staticmethod
    def compute_episode_metrics(
        telemetry_history: List[ReceiverTelemetry],
        all_emitters: list,
        num_bands: int,
        estimated_periods: Optional[Dict[int, Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        total_dwells = len(telemetry_history)
        if total_dwells == 0:
            return {}

        # 1. Distinct Emitters Intercepted & TTFI
        emitter_ids = {e.id for e in all_emitters}
        first_intercept_step: Dict[str, int] = {}
        intercept_counts: Dict[str, int] = {e.id: 0 for e in all_emitters}

        for telem in telemetry_history:
            for eid in telem.intercepted_emitter_ids:
                intercept_counts[eid] += 1
                if eid not in first_intercept_step:
                    first_intercept_step[eid] = telem.step

        distinct_intercepted = len(first_intercept_step)
        intercepted_fraction = distinct_intercepted / len(emitter_ids) if emitter_ids else 0.0

        # Mean TTFI for intercepted emitters
        ttfi_list = list(first_intercept_step.values())
        mean_ttfi = float(np.mean(ttfi_list)) if ttfi_list else float(total_dwells)

        # 2. Intercept Rate
        # Total emissions across all emitters vs total intercepted emissions
        total_threat_emissions = sum(
            e.total_emissions for e in all_emitters if getattr(e, "emitter_type", "") != "decoy"
        )
        total_threat_intercepts = sum(
            len([eid for eid in t.intercepted_emitter_ids if not t.is_decoy])
            for t in telemetry_history if t.hit
        )
        threat_intercept_rate = (
            total_threat_intercepts / total_threat_emissions if total_threat_emissions > 0 else 0.0
        )

        # 3. Periodic Emitter Revisit / Illumination Capture Rate
        periodic_emitters = [e for e in all_emitters if isinstance(e, PeriodicRadarEmitter)]
        periodic_revisit_rates = []
        period_estimation_errors = []

        for p_emitter in periodic_emitters:
            # How many main beam illumination windows did it have?
            scan_period = p_emitter.scan_period
            total_windows = max(1, total_dwells // scan_period)
            # Hits for this periodic radar
            hits = intercept_counts.get(p_emitter.id, 0)
            revisit_rate = min(1.0, hits / float(total_windows))
            periodic_revisit_rates.append(revisit_rate)

            # Check period estimation accuracy
            if estimated_periods and p_emitter.band in estimated_periods:
                est = estimated_periods[p_emitter.band]["estimated_period"]
                rel_err = abs(est - scan_period) / float(scan_period)
                period_estimation_errors.append(rel_err)

        mean_periodic_revisit = float(np.mean(periodic_revisit_rates)) if periodic_revisit_rates else 1.0
        mean_period_error = float(np.mean(period_estimation_errors)) if period_estimation_errors else 0.0

        # 4. Dwell Efficiency (Empty or Decoy Dwells)
        empty_or_decoy_dwells = sum(
            1 for t in telemetry_history if (not t.hit) or t.is_decoy or t.is_false_alarm
        )
        wasted_dwell_ratio = empty_or_decoy_dwells / float(total_dwells)
        useful_dwell_ratio = 1.0 - wasted_dwell_ratio

        # 5. Band Coverage Fairness (Normalized Shannon Entropy)
        band_visits = [0] * num_bands
        for t in telemetry_history:
            band_visits[t.dwell_band] += 1

        probs = np.array(band_visits, dtype=float) / total_dwells
        # Filter non-zero for entropy
        nonzero_p = probs[probs > 0]
        entropy = -np.sum(nonzero_p * np.log2(nonzero_p)) if len(nonzero_p) > 0 else 0.0
        max_entropy = np.log2(num_bands) if num_bands > 1 else 1.0
        fairness_score = float(entropy / max_entropy) if max_entropy > 0 else 1.0

        # 6. Retuning Cost Overhead
        total_retune_ms = sum(t.retune_cost_ms for t in telemetry_history)
        avg_retune_ms_per_step = total_retune_ms / float(total_dwells)

        return {
            "total_dwells": total_dwells,
            "distinct_emitters_intercepted": distinct_intercepted,
            "total_emitters": len(emitter_ids),
            "intercepted_fraction": round(intercepted_fraction, 4),
            "mean_ttfi_steps": round(mean_ttfi, 2),
            "threat_intercept_rate": round(threat_intercept_rate, 4),
            "periodic_revisit_rate": round(mean_periodic_revisit, 4),
            "period_estimation_error": round(mean_period_error, 4),
            "dwell_efficiency": round(useful_dwell_ratio, 4),
            "wasted_dwell_ratio": round(wasted_dwell_ratio, 4),
            "band_coverage_fairness": round(fairness_score, 4),
            "total_retune_cost_ms": round(total_retune_ms, 2),
            "avg_retune_cost_ms": round(avg_retune_ms_per_step, 4),
            "first_intercept_step": first_intercept_step,
        }
