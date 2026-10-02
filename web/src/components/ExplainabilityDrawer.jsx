import React, { useState } from "react";
import { Info, HelpCircle, ArrowUpRight, ArrowDownRight, Sparkles } from "lucide-react";

export default function ExplainabilityDrawer({ explainability = {}, chosenBand = 0, numBands = 16 }) {
  const [inspectedBand, setInspectedBand] = useState(chosenBand);
  const activeBand = inspectedBand !== null ? inspectedBand : chosenBand;
  const components = explainability.components || {};
  const bandInfo = components[activeBand] || {};
  const periodEstimates = explainability.period_estimates || {};

  return (
    <div className="bg-[#0D1322] border border-gray-800 rounded-xl p-4 shadow-xl">
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-gray-800">
        <div className="flex items-center space-x-2">
          <Sparkles className="w-4 h-4 text-cyan-400" />
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wide">
            Decision Explainability Inspector
          </h3>
        </div>
        <div className="flex items-center space-x-2 text-xs">
          <span className="text-slate-400">Inspect Band:</span>
          <select
            value={activeBand}
            onChange={(e) => setInspectedBand(Number(e.target.value))}
            className="bg-gray-900 border border-gray-700 text-cyan-300 font-mono font-bold px-2 py-1 rounded"
          >
            {Array.from({ length: numBands }).map((_, b) => (
              <option key={b} value={b}>
                Band {b} {b === chosenBand ? "(CHOSEN)" : ""}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Priority Decomposition Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3 mb-4">
        {/* Total Score */}
        <div className="bg-gray-900/80 border border-cyan-500/40 rounded-lg p-3">
          <div className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Total Priority Index</div>
          <div className="text-xl font-bold font-mono text-cyan-300 mt-1">
            {bandInfo.total_score !== undefined ? bandInfo.total_score.toFixed(3) : "0.000"}
          </div>
          <div className="text-[10px] text-cyan-400/80 mt-1">
            {activeBand === chosenBand ? "★ Argmax Winner" : "Runner Up"}
          </div>
        </div>

        {/* Bayesian Exploitation */}
        <div className="bg-gray-900/80 border border-gray-800 rounded-lg p-3">
          <div className="text-[10px] text-slate-400 uppercase font-bold tracking-wider flex items-center justify-between">
            <span>Bayesian Exploitation</span>
            <ArrowUpRight className="w-3 h-3 text-emerald-400" />
          </div>
          <div className="text-xl font-bold font-mono text-emerald-400 mt-1">
            +{bandInfo.exploitation !== undefined ? bandInfo.exploitation.toFixed(3) : "0.000"}
          </div>
          <div className="text-[10px] text-slate-400 mt-1">
            P(Occupied) = {bandInfo.belief ? (bandInfo.belief * 100).toFixed(1) : 0}%
          </div>
        </div>

        {/* Exploration Floor */}
        <div className="bg-gray-900/80 border border-gray-800 rounded-lg p-3">
          <div className="text-[10px] text-slate-400 uppercase font-bold tracking-wider flex items-center justify-between">
            <span>Exploration Bonus</span>
            <ArrowUpRight className="w-3 h-3 text-cyan-400" />
          </div>
          <div className="text-xl font-bold font-mono text-cyan-400 mt-1">
            +{bandInfo.exploration !== undefined ? bandInfo.exploration.toFixed(3) : "0.000"}
          </div>
          <div className="text-[10px] text-slate-400 mt-1">Non-stationarity Floor</div>
        </div>

        {/* Periodicity Pre-Positioning */}
        <div className="bg-gray-900/80 border border-gray-800 rounded-lg p-3">
          <div className="text-[10px] text-slate-400 uppercase font-bold tracking-wider flex items-center justify-between">
            <span>Periodicity Boost</span>
            <ArrowUpRight className="w-3 h-3 text-purple-400" />
          </div>
          <div className="text-xl font-bold font-mono text-purple-400 mt-1">
            +{bandInfo.periodicity_boost !== undefined ? bandInfo.periodicity_boost.toFixed(3) : "0.000"}
          </div>
          <div className="text-[10px] text-slate-400 mt-1">
            {bandInfo.expected_period_step ? `Peak Step #${bandInfo.expected_period_step}` : "No Imminent Beam"}
          </div>
        </div>

        {/* Retune Distance Cost */}
        <div className="bg-gray-900/80 border border-gray-800 rounded-lg p-3">
          <div className="text-[10px] text-slate-400 uppercase font-bold tracking-wider flex items-center justify-between">
            <span>LO Retune Penalty</span>
            <ArrowDownRight className="w-3 h-3 text-rose-400" />
          </div>
          <div className="text-xl font-bold font-mono text-rose-400 mt-1">
            -{bandInfo.retune_penalty !== undefined ? bandInfo.retune_penalty.toFixed(3) : "0.000"}
          </div>
          <div className="text-[10px] text-slate-400 mt-1">Synthesizer Hop Distance</div>
        </div>
      </div>

      {/* Online Periodicity Diagnostics */}
      {periodEstimates[activeBand] && (
        <div className="p-3 bg-purple-950/30 border border-purple-800/40 rounded-lg flex items-center justify-between text-xs font-mono">
          <div className="flex items-center space-x-2 text-purple-300">
            <Info className="w-4 h-4 text-purple-400" />
            <span>
              Detected Periodic Radar on Band {activeBand}: Scan Period ≈{" "}
              <strong>{periodEstimates[activeBand].estimated_period} steps</strong> (Confidence:{" "}
              {(periodEstimates[activeBand].confidence * 100).toFixed(0)}%)
            </span>
          </div>
          <span className="text-purple-400 text-[11px]">
            {periodEstimates[activeBand].sample_count} pulse hits recorded
          </span>
        </div>
      )}
    </div>
  );
}
