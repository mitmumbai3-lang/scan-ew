import React, { useRef, useEffect } from "react";
import { Eye, EyeOff, Layers, Zap } from "lucide-react";

export default function WaterfallCanvas({
  history,
  numBands = 16,
  showGroundTruth = true,
  setShowGroundTruth,
  freqMinGhz = 0.5,
  freqMaxGhz = 18.0,
}) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const width = canvas.width;
    const height = canvas.height;

    // Background clear
    ctx.fillStyle = "#0B0F19";
    ctx.fillRect(0, 0, width, height);

    const bandWidth = width / numBands;
    const rowHeight = 14;
    const maxVisibleRows = Math.floor(height / rowHeight);

    // Draw vertical band separators
    ctx.strokeStyle = "#161F30";
    ctx.lineWidth = 1;
    for (let b = 0; b <= numBands; b++) {
      const x = b * bandWidth;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }

    // Display history slice (newest at bottom)
    const visibleHistory = history.slice(-maxVisibleRows);
    const startY = height - visibleHistory.length * rowHeight;

    // Draw past dwell steps
    visibleHistory.forEach((item, index) => {
      const y = startY + index * rowHeight;

      // 1. Draw Ground Truth Layer if enabled
      if (showGroundTruth && item.ground_truth_active) {
        Object.entries(item.ground_truth_active).forEach(([bandStr, emitterIds]) => {
          const b = parseInt(bandStr, 10);
          if (b >= 0 && b < numBands && emitterIds.length > 0) {
            const x = b * bandWidth;
            // Determine dominant color from emitter IDs
            let color = "rgba(16, 185, 129, 0.28)"; // default periodic/green
            if (emitterIds.some((id) => id.includes("DECOY") || id.includes("JAMMER"))) {
              color = "rgba(239, 68, 68, 0.35)"; // red for decoy
            } else if (emitterIds.some((id) => id.includes("AGILE") || id.includes("HOPPER"))) {
              color = "rgba(168, 85, 247, 0.35)"; // purple for agile
            } else if (emitterIds.some((id) => id.includes("FIXED") || id.includes("COMM"))) {
              color = "rgba(245, 158, 11, 0.30)"; // amber for fixed
            }

            ctx.fillStyle = color;
            ctx.fillRect(x + 1, y + 1, bandWidth - 2, rowHeight - 2);
          }
        });
      }

      // 2. Draw Receiver Dwell Position
      const dwellBand = item.telemetry ? item.telemetry.dwell_band : item.action;
      const x = dwellBand * bandWidth;

      if (item.telemetry && item.telemetry.hit) {
        // HIT: Glowing cyan / golden box
        ctx.fillStyle = item.telemetry.is_decoy
          ? "rgba(239, 68, 68, 0.85)"
          : "rgba(6, 182, 212, 0.85)";
        ctx.fillRect(x + 2, y + 2, bandWidth - 4, rowHeight - 4);

        // Bright border
        ctx.strokeStyle = "#FFFFFF";
        ctx.lineWidth = 1.5;
        ctx.strokeRect(x + 2, y + 2, bandWidth - 4, rowHeight - 4);

        // Small pulse tag if room
        if (bandWidth > 36) {
          ctx.fillStyle = "#FFFFFF";
          ctx.font = "bold 9px monospace";
          ctx.fillText(
            `${Math.round(item.telemetry.measured_snr_db)}dB`,
            x + 4,
            y + rowHeight - 4
          );
        }
      } else {
        // MISS: Subtle dwell outline
        ctx.strokeStyle = "rgba(6, 182, 212, 0.45)";
        ctx.lineWidth = 1;
        ctx.strokeRect(x + 2, y + 2, bandWidth - 4, rowHeight - 4);
      }
    });

    // Draw retune trajectory line linking recent dwells
    if (visibleHistory.length > 1) {
      ctx.beginPath();
      ctx.strokeStyle = "rgba(6, 182, 212, 0.5)";
      ctx.lineWidth = 1.2;
      ctx.setLineDash([2, 3]);

      visibleHistory.forEach((item, index) => {
        const y = startY + index * rowHeight + rowHeight / 2;
        const dwellBand = item.telemetry ? item.telemetry.dwell_band : item.action;
        const x = dwellBand * bandWidth + bandWidth / 2;
        if (index === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });
      ctx.stroke();
      ctx.setLineDash([]);
    }
  }, [history, numBands, showGroundTruth]);

  // Frequency range labels
  const bandStepGhz = (freqMaxGhz - freqMinGhz) / numBands;

  return (
    <div className="bg-[#0D1322] border border-gray-800 rounded-xl p-4 shadow-xl">
      {/* Header & Controls */}
      <div className="flex flex-wrap items-center justify-between pb-3 mb-2 border-b border-gray-800 gap-2">
        <div className="flex items-center space-x-2">
          <Layers className="w-4 h-4 text-cyan-400" />
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wide">
            Real-Time Spectrum Waterfall (RF Heatmap)
          </h3>
          <span className="text-xs text-slate-500 font-mono">
            {freqMinGhz} GHz → {freqMaxGhz} GHz ({numBands} sub-bands)
          </span>
        </div>

        <div className="flex items-center space-x-3">
          {/* Ground Truth Toggle */}
          <button
            onClick={() => setShowGroundTruth(!showGroundTruth)}
            className={`flex items-center space-x-1.5 px-2.5 py-1 rounded text-xs font-medium transition ${
              showGroundTruth
                ? "bg-emerald-950/70 border border-emerald-500/50 text-emerald-300"
                : "bg-gray-800 border border-gray-700 text-slate-400"
            }`}
          >
            {showGroundTruth ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
            <span>Ground Truth Emitters: {showGroundTruth ? "ON" : "OFF"}</span>
          </button>
        </div>
      </div>

      {/* Frequency Column Headers */}
      <div
        className="grid gap-0 text-center text-[10px] font-mono text-slate-400 mb-1 border-b border-gray-800 pb-1"
        style={{ gridTemplateColumns: `repeat(${numBands}, minmax(0, 1fr))` }}
      >
        {Array.from({ length: numBands }).map((_, b) => {
          const centerFreq = (freqMinGhz + (b + 0.5) * bandStepGhz).toFixed(1);
          return (
            <div key={b} className="truncate px-0.5" title={`Band ${b}: ~${centerFreq} GHz`}>
              B{b}
              <div className="text-[9px] text-slate-500">{centerFreq}G</div>
            </div>
          );
        })}
      </div>

      {/* HTML5 Canvas Waterfall */}
      <div className="relative border border-gray-800 rounded bg-[#0B0F19] overflow-hidden">
        <canvas
          ref={canvasRef}
          width={840}
          height={380}
          className="w-full h-[380px] block"
        />

        {/* Scanline overlay effect */}
        <div className="absolute inset-0 pointer-events-none bg-gradient-to-b from-transparent via-cyan-500/5 to-transparent h-16 w-full animate-scanline"></div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap items-center justify-between text-xs text-slate-400 pt-3 mt-2 border-t border-gray-800/80 gap-2">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded-sm bg-cyan-400 border border-white"></span>
            <span>Receiver Intercept (Hit)</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded-sm border border-cyan-400/50"></span>
            <span>Receiver Dwell (Miss)</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded-sm bg-emerald-500/30 border border-emerald-500/50"></span>
            <span>Periodic Radar Beam</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded-sm bg-purple-500/30 border border-purple-500/50"></span>
            <span>Agile Hopper</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded-sm bg-rose-500/30 border border-rose-500/50"></span>
            <span>Decoy Jammer</span>
          </div>
        </div>
        <div className="text-[11px] font-mono text-cyan-400">
          Showing latest ~27 dwell steps
        </div>
      </div>
    </div>
  );
}
