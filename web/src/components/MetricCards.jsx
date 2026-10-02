import React from "react";
import { Crosshair, Zap, RotateCcw, Clock, Gauge, BarChart2 } from "lucide-react";

export default function MetricCards({ metrics = {} }) {
  const cards = [
    {
      title: "Threat Intercept Rate",
      value: metrics.threat_intercept_rate !== undefined ? `${(metrics.threat_intercept_rate * 100).toFixed(1)}%` : "0.0%",
      sub: "Illuminations Captured",
      icon: Crosshair,
      color: "text-cyan-400",
      bg: "bg-cyan-950/40 border-cyan-800/40",
    },
    {
      title: "Periodic Revisit Rate",
      value: metrics.periodic_revisit_rate !== undefined ? `${(metrics.periodic_revisit_rate * 100).toFixed(1)}%` : "0.0%",
      sub: "Radar Beam Intercepts",
      icon: RotateCcw,
      color: "text-emerald-400",
      bg: "bg-emerald-950/40 border-emerald-800/40",
    },
    {
      title: "Distinct Emitters",
      value: metrics.distinct_emitters_intercepted !== undefined ? `${metrics.distinct_emitters_intercepted} / ${metrics.total_emitters || "-"}` : "0",
      sub: `${metrics.intercepted_fraction ? (metrics.intercepted_fraction * 100).toFixed(0) : 0}% Spectrum Discovery`,
      icon: Zap,
      color: "text-amber-400",
      bg: "bg-amber-950/40 border-amber-800/40",
    },
    {
      title: "Mean TTFI",
      value: metrics.mean_ttfi_steps !== undefined ? `${metrics.mean_ttfi_steps} steps` : "0.0",
      sub: "Time-To-First-Intercept",
      icon: Clock,
      color: "text-indigo-400",
      bg: "bg-indigo-950/40 border-indigo-800/40",
    },
    {
      title: "Dwell Efficiency",
      value: metrics.dwell_efficiency !== undefined ? `${(metrics.dwell_efficiency * 100).toFixed(1)}%` : "0.0%",
      sub: `${(metrics.wasted_dwell_ratio ? metrics.wasted_dwell_ratio * 100 : 0).toFixed(1)}% Wasted on Empty/Decoy`,
      icon: Gauge,
      color: "text-rose-400",
      bg: "bg-rose-950/40 border-rose-800/40",
    },
    {
      title: "LO Retune Overhead",
      value: metrics.total_retune_cost_ms !== undefined ? `${metrics.total_retune_cost_ms.toFixed(1)} ms` : "0.0 ms",
      sub: `Avg: ${metrics.avg_retune_cost_ms ? metrics.avg_retune_cost_ms.toFixed(2) : 0} ms / dwell`,
      icon: BarChart2,
      color: "text-purple-400",
      bg: "bg-purple-950/40 border-purple-800/40",
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div
            key={idx}
            className={`border rounded-xl p-3 flex flex-col justify-between shadow-md transition-transform hover:-translate-y-0.5 ${card.bg}`}
          >
            <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
              <span className="truncate font-medium">{card.title}</span>
              <Icon className={`w-3.5 h-3.5 ${card.color}`} />
            </div>
            <div className={`text-xl font-bold font-mono tracking-tight ${card.color}`}>
              {card.value}
            </div>
            <div className="text-[10px] text-slate-400 mt-1 truncate">
              {card.sub}
            </div>
          </div>
        );
      })}
    </div>
  );
}
