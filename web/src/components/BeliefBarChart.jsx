import React from "react";
import { BrainCircuit, Clock, Target } from "lucide-react";

export default function BeliefBarChart({ beliefs = [], components = {}, currentBand = 0, numBands = 16 }) {
  const displayBeliefs = beliefs.length === numBands ? beliefs : Array(numBands).fill(0.5);

  return (
    <div className="bg-[#0D1322] border border-gray-800 rounded-xl p-4 shadow-xl">
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-gray-800">
        <div className="flex items-center space-x-2">
          <BrainCircuit className="w-4 h-4 text-cyan-400" />
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wide">
            Bayesian Belief State & Restless Priority Map
          </h3>
        </div>
        <div className="text-xs font-mono text-slate-400">
          Current Dwell: <span className="text-cyan-400 font-bold">Band {currentBand}</span>
        </div>
      </div>

      {/* Per-band Bar Grid */}
      <div className="grid grid-cols-16 gap-1 h-36 items-end pt-4 pb-2 border-b border-gray-800/80 bg-gray-950/40 rounded px-2">
        {Array.from({ length: numBands }).map((_, b) => {
          const beliefVal = displayBeliefs[b] !== undefined ? displayBeliefs[b] : 0.5;
          const comp = components[b] || {};
          const isTarget = b === currentBand;
          const hasPreposition = comp.periodicity_boost && comp.periodicity_boost > 0.4;
          const heightPercent = Math.max(8, Math.min(100, Math.round(beliefVal * 100)));

          return (
            <div key={b} className="flex flex-col items-center h-full justify-end group relative">
              {/* Tooltip on Hover */}
              <div className="absolute -top-16 hidden group-hover:flex flex-col bg-gray-900 border border-cyan-500/40 text-[10px] text-white p-1.5 rounded shadow-lg z-20 pointer-events-none w-28">
                <span className="font-bold text-cyan-300">Band {b}</span>
                <span>Belief: {(beliefVal * 100).toFixed(1)}%</span>
                <span>Priority: {comp.total_score || "0.00"}</span>
                {comp.expected_period_step && (
                  <span className="text-emerald-400">Next Peak: #{comp.expected_period_step}</span>
                )}
              </div>

              {/* Pre-positioning Icon Indicator */}
              {hasPreposition && (
                <div className="mb-1 text-emerald-400 animate-bounce" title="Imminent Radar Beam Pre-Positioning!">
                  <Clock className="w-3 h-3" />
                </div>
              )}

              {/* Vertical Bar */}
              <div
                style={{ height: `${heightPercent}%` }}
                className={`w-full rounded-t transition-all duration-150 relative ${
                  isTarget
                    ? "bg-gradient-to-t from-cyan-600 to-cyan-300 ring-2 ring-white"
                    : hasPreposition
                    ? "bg-gradient-to-t from-emerald-600 to-emerald-400"
                    : beliefVal > 0.6
                    ? "bg-gradient-to-t from-cyan-800 to-cyan-500"
                    : "bg-gray-800"
                }`}
              >
                {isTarget && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <Target className="w-2.5 h-2.5 text-white" />
                  </div>
                )}
              </div>

              {/* Label */}
              <span className={`text-[10px] font-mono mt-1 ${isTarget ? "text-cyan-300 font-bold" : "text-slate-400"}`}>
                B{b}
              </span>
            </div>
          );
        })}
      </div>

      {/* Legend & Details */}
      <div className="flex flex-wrap items-center justify-between text-xs text-slate-400 pt-2 gap-2">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded bg-cyan-400"></span>
            <span>Current Dwell</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded bg-emerald-400"></span>
            <span>Pre-Positioning Boost</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded bg-gray-700"></span>
            <span>Dormant Prior</span>
          </div>
        </div>
        <div className="text-[11px] font-mono text-slate-400">
          Bar height = Posterior Probability P(S_b = 1)
        </div>
      </div>
    </div>
  );
}
