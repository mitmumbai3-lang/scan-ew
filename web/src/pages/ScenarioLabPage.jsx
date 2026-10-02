import React from "react";
import { Shield, Radio, CheckCircle2, ArrowRight, Zap, Target } from "lucide-react";

export default function ScenarioLabPage({
  presets = [],
  selectedScenario,
  onScenarioChange,
  emitters = [],
  onLoadScenario,
}) {
  return (
    <div className="space-y-6">
      <div className="bg-[#0D1322] border border-gray-800 rounded-xl p-6 shadow-xl">
        <h2 className="text-lg font-bold text-slate-100 flex items-center space-x-2">
          <Shield className="w-5 h-5 text-cyan-400" />
          <span>Electronic Warfare Scenario Lab</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Select or customize realistic RF environments to test the scheduler's adaptation under different operational threats.
        </p>

        {/* Preset Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
          {presets.map((p) => {
            const isSelected = selectedScenario === p.id;
            return (
              <div
                key={p.id}
                onClick={() => onScenarioChange(p.id)}
                className={`p-4 rounded-xl border cursor-pointer transition-all ${
                  isSelected
                    ? "bg-cyan-950/40 border-cyan-500/70 shadow-lg shadow-cyan-950/50 ring-1 ring-cyan-400"
                    : "bg-gray-900/60 border-gray-800 hover:border-gray-700 hover:bg-gray-800/40"
                }`}
              >
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-slate-200">{p.name}</h3>
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded font-mono ${
                      p.difficulty === "Medium"
                        ? "bg-blue-900/40 text-blue-300 border border-blue-700/40"
                        : p.difficulty === "Hard"
                        ? "bg-amber-900/40 text-amber-300 border border-amber-700/40"
                        : "bg-rose-900/40 text-rose-300 border border-rose-700/40"
                    }`}
                  >
                    {p.difficulty}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-2 line-clamp-2">{p.description}</p>

                <div className="mt-4 pt-3 border-t border-gray-800/80 flex items-center justify-between text-xs">
                  <span className="text-slate-500 font-mono">ID: {p.id}</span>
                  {isSelected ? (
                    <span className="flex items-center space-x-1 text-cyan-400 font-bold">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>ACTIVE</span>
                    </span>
                  ) : (
                    <span className="text-slate-400 flex items-center space-x-1 group-hover:text-slate-200">
                      <span>Select</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Active Scenario Emitter Layout */}
      <div className="bg-[#0D1322] border border-gray-800 rounded-xl p-6 shadow-xl">
        <div className="flex items-center justify-between pb-3 border-b border-gray-800 mb-4">
          <div className="flex items-center space-x-2">
            <Radio className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wide">
              Active Ground Truth Emitter Manifest ({emitters.length} Emitters)
            </h3>
          </div>
          <span className="text-xs font-mono text-cyan-400">
            Current: {selectedScenario}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {emitters.map((e) => (
            <div key={e.id} className="bg-gray-900/80 border border-gray-800 rounded-lg p-3">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-200 text-xs">{e.name}</span>
                <span
                  className={`text-[9px] uppercase font-mono font-bold px-1.5 py-0.5 rounded ${
                    e.type === "periodic"
                      ? "bg-emerald-950 text-emerald-300 border border-emerald-800"
                      : e.type === "agile"
                      ? "bg-purple-950 text-purple-300 border border-purple-800"
                      : e.type === "decoy"
                      ? "bg-rose-950 text-rose-300 border border-rose-800"
                      : "bg-amber-950 text-amber-300 border border-amber-800"
                  }`}
                >
                  {e.type}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2 mt-2 text-[11px] text-slate-400 font-mono">
                <div>ID: {e.id}</div>
                <div>Priority: {e.priority === 1 ? "Threat (1)" : e.priority === 2 ? "Medium (2)" : "Decoy (3)"}</div>
                <div>Nominal SNR: {e.base_snr_db} dB</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
