import React from "react";
import { Play, Pause, StepForward, RotateCcw, FastForward, Sliders, Shield } from "lucide-react";

export default function Controls({
  isRunning,
  onPlay,
  onPause,
  onStep,
  onReset,
  speedHz,
  onSpeedChange,
  presets = [],
  selectedScenario,
  onScenarioChange,
  schedulers = [],
  selectedScheduler,
  onSchedulerChange,
  seed,
  onSeedChange,
}) {
  return (
    <div className="bg-[#0D1322] border border-gray-800 rounded-xl p-4 shadow-xl flex flex-wrap items-center justify-between gap-4">
      {/* Simulation Stepper & Playback Controls */}
      <div className="flex items-center space-x-2">
        {isRunning ? (
          <button
            onClick={onPause}
            className="flex items-center space-x-1.5 px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs rounded-lg shadow-lg shadow-amber-900/30 transition active:scale-95"
          >
            <Pause className="w-3.5 h-3.5 fill-current" />
            <span>PAUSE</span>
          </button>
        ) : (
          <button
            onClick={onPlay}
            className="flex items-center space-x-1.5 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs rounded-lg shadow-lg shadow-cyan-900/30 transition active:scale-95"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>LIVE SCAN</span>
          </button>
        )}

        <button
          onClick={() => onStep(1)}
          disabled={isRunning}
          className="flex items-center space-x-1 px-3 py-2 bg-gray-800 hover:bg-gray-700 disabled:opacity-40 text-slate-200 text-xs font-medium rounded-lg border border-gray-700 transition"
          title="Advance 1 Dwell Step"
        >
          <StepForward className="w-3.5 h-3.5" />
          <span>Step 1x</span>
        </button>

        <button
          onClick={() => onStep(10)}
          disabled={isRunning}
          className="flex items-center space-x-1 px-3 py-2 bg-gray-800 hover:bg-gray-700 disabled:opacity-40 text-slate-200 text-xs font-medium rounded-lg border border-gray-700 transition"
          title="Advance 10 Dwell Steps"
        >
          <FastForward className="w-3.5 h-3.5" />
          <span>Step 10x</span>
        </button>

        <button
          onClick={onReset}
          className="flex items-center space-x-1 px-3 py-2 bg-gray-800 hover:bg-gray-700 text-rose-300 text-xs font-medium rounded-lg border border-rose-900/40 transition"
          title="Reset Episode"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset</span>
        </button>
      </div>

      {/* Selectors */}
      <div className="flex flex-wrap items-center gap-3 text-xs">
        {/* Scenario Preset Selector */}
        <div className="flex items-center space-x-1.5 bg-gray-900 border border-gray-800 px-2.5 py-1.5 rounded-lg">
          <Shield className="w-3.5 h-3.5 text-cyan-400" />
          <span className="text-slate-400 font-medium">Scenario:</span>
          <select
            value={selectedScenario}
            onChange={(e) => onScenarioChange(e.target.value)}
            disabled={isRunning}
            className="bg-transparent text-slate-200 font-medium focus:outline-none cursor-pointer"
          >
            {presets.map((p) => (
              <option key={p.id} value={p.id} className="bg-gray-900 text-white">
                {p.name}
              </option>
            ))}
          </select>
        </div>

        {/* Algorithm Scheduler Selector */}
        <div className="flex items-center space-x-1.5 bg-gray-900 border border-gray-800 px-2.5 py-1.5 rounded-lg">
          <Sliders className="w-3.5 h-3.5 text-purple-400" />
          <span className="text-slate-400 font-medium">Scheduler:</span>
          <select
            value={selectedScheduler}
            onChange={(e) => onSchedulerChange(e.target.value)}
            disabled={isRunning}
            className="bg-transparent text-slate-200 font-medium focus:outline-none cursor-pointer"
          >
            {schedulers.map((s) => (
              <option key={s.id} value={s.id} className="bg-gray-900 text-white">
                {s.name}
              </option>
            ))}
          </select>
        </div>

        {/* Speed Slider */}
        <div className="flex items-center space-x-2 bg-gray-900 border border-gray-800 px-3 py-1.5 rounded-lg">
          <span className="text-slate-400">Rate:</span>
          <input
            type="range"
            min={2}
            max={60}
            step={2}
            value={speedHz}
            onChange={(e) => onSpeedChange(Number(e.target.value))}
            className="w-20 accent-cyan-400 cursor-pointer"
          />
          <span className="font-mono text-cyan-300 w-8">{speedHz}Hz</span>
        </div>
      </div>
    </div>
  );
}
