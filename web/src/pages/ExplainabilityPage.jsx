import React from "react";
import { Cpu, BrainCircuit, Activity, RotateCw, Shield, Sparkles } from "lucide-react";

export default function ExplainabilityPage({ explainability = {}, currentBand = 0, numBands = 16 }) {
  const components = explainability.components || {};

  return (
    <div className="space-y-6">
      {/* Overview Banner */}
      <div className="bg-[#0D1322] border border-gray-800 rounded-xl p-6 shadow-xl">
        <h2 className="text-lg font-bold text-slate-100 flex items-center space-x-2">
          <BrainCircuit className="w-5 h-5 text-cyan-400" />
          <span>SmartScan-BayesianRMAB Architecture & Mathematical Formulation</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1 max-w-3xl leading-relaxed">
          The proposed engine operates in a closed loop with zero prior intelligence. It solves the non-stationary
          restless bandit problem by continuously updating per-band Bayesian occupancy posteriors, tracking radar
          antenna rotation periods online, and pre-positioning the tuner ahead of periodic illumination windows.
        </p>
      </div>

      {/* 4 Pillars of Innovation */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Pillar 1 */}
        <div className="bg-[#0D1322] border border-gray-800 rounded-xl p-5 shadow-lg">
          <div className="flex items-center space-x-2 text-cyan-400 font-bold text-sm mb-2">
            <Activity className="w-4 h-4" />
            <span>1. Recursive Bayesian Belief Filter</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Maintains the posterior probability P(S = 1 | y) for each sub-band. Unobserved bands
            naturally decay towards the stationary prior &pi; = p01 / (p01 + p10), building exploration
            urgency automatically without heuristics.
          </p>
          <div className="bg-gray-950 p-2.5 rounded font-mono text-[11px] text-cyan-300 mt-3 border border-gray-800">
            p_post = (Pd * p_prior) / [Pd * p_prior + Pfa * (1 - p_prior)]
          </div>
        </div>

        {/* Pillar 2 */}
        <div className="bg-[#0D1322] border border-gray-800 rounded-xl p-5 shadow-lg">
          <div className="flex items-center space-x-2 text-purple-400 font-bold text-sm mb-2">
            <RotateCw className="w-4 h-4" />
            <span>2. Online Periodicity & Main-Beam Pre-Positioning</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Extracts the fundamental antenna scan period $\hat{T}_{scan}$ and phase from pulse time-of-arrival (TOA) intervals.
            Injects an exponential boost $\Gamma_{pred}$ when $t \in [t_{exp} - 1, t_{exp} + 1]$, meeting rotating radars exactly as they illuminate the receiver.
          </p>
          <div className="bg-gray-950 p-2.5 rounded font-mono text-[11px] text-purple-300 mt-3 border border-gray-800">
            Γ_pred(b, t) = 2.5 * Confidence * exp(-0.5 * (t - t_exp)²)
          </div>
        </div>

        {/* Pillar 3 */}
        <div className="bg-[#0D1322] border border-gray-800 rounded-xl p-5 shadow-lg">
          <div className="flex items-center space-x-2 text-rose-400 font-bold text-sm mb-2">
            <Shield className="w-4 h-4" />
            <span>3. Decoy & Saturation Profiler</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Detects continuous, high-duty-cycle distractors and jammers that attempt to trap greedy algorithms.
            Attenuates exploitation weights dynamically, preventing dwell starvation of critical tactical bands.
          </p>
          <div className="bg-gray-950 p-2.5 rounded font-mono text-[11px] text-rose-300 mt-3 border border-gray-800">
            w_decoy(b) = 1.0 / (1.0 + 0.05 * hits_continuous)
          </div>
        </div>

        {/* Pillar 4 */}
        <div className="bg-[#0D1322] border border-gray-800 rounded-xl p-5 shadow-lg">
          <div className="flex items-center space-x-2 text-emerald-400 font-bold text-sm mb-2">
            <Sparkles className="w-4 h-4" />
            <span>4. LO Retune & Starvation Floor</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Subtracts frequency hopping distance penalty &lambda; &middot; |&Delta;b| / N to optimize synthesizer settling latency.
            Enforces a hard exploration floor so dormant or new threats are never starved.
          </p>
          <div className="bg-gray-950 p-2.5 rounded font-mono text-[11px] text-emerald-300 mt-3 border border-gray-800">
            I(b, t) = Exploitation + Exploration + PeriodicityBoost - RetunePenalty
          </div>
        </div>
      </div>

      {/* Live Priority Index Breakdown for All Bands */}
      <div className="bg-[#0D1322] border border-gray-800 rounded-xl p-6 shadow-xl">
        <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wide mb-4">
          Current Step Priority Index Decomposition (All {numBands} Sub-Bands)
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300 font-mono">
            <thead className="bg-gray-900 text-slate-400 border-b border-gray-800">
              <tr>
                <th className="py-2.5 px-3">Band</th>
                <th className="py-2.5 px-3">Total Priority I(b)</th>
                <th className="py-2.5 px-3">Exploitation (p_b)</th>
                <th className="py-2.5 px-3">Exploration Bonus</th>
                <th className="py-2.5 px-3">Periodicity Boost</th>
                <th className="py-2.5 px-3">Retune Penalty</th>
                <th className="py-2.5 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {Array.from({ length: numBands }).map((_, b) => {
                const comp = components[b] || {};
                const isChosen = b === currentBand;
                return (
                  <tr key={b} className={isChosen ? "bg-cyan-950/40 text-cyan-200 font-bold" : "hover:bg-gray-800/20"}>
                    <td className="py-2.5 px-3">Band {b}</td>
                    <td className="py-2.5 px-3 text-cyan-300">{comp.total_score !== undefined ? comp.total_score.toFixed(3) : "-"}</td>
                    <td className="py-2.5 px-3 text-emerald-400">+{comp.exploitation !== undefined ? comp.exploitation.toFixed(3) : "-"}</td>
                    <td className="py-2.5 px-3 text-cyan-400">+{comp.exploration !== undefined ? comp.exploration.toFixed(3) : "-"}</td>
                    <td className="py-2.5 px-3 text-purple-400">+{comp.periodicity_boost !== undefined ? comp.periodicity_boost.toFixed(3) : "-"}</td>
                    <td className="py-2.5 px-3 text-rose-400">-{comp.retune_penalty !== undefined ? comp.retune_penalty.toFixed(3) : "-"}</td>
                    <td className="py-2.5 px-3">
                      {isChosen ? (
                        <span className="bg-cyan-900/60 text-cyan-300 px-2 py-0.5 rounded text-[10px]">CHOSEN DWELL</span>
                      ) : (
                        <span className="text-slate-500 text-[10px]">STANDBY</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
