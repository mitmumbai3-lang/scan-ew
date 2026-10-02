import React from "react";
import { Radio, ShieldAlert, Cpu, Activity, BarChart3, Database, FileSpreadsheet } from "lucide-react";

export default function Navbar({ activeTab, setActiveTab, isConnected, isRunning, speedHz }) {
  const tabs = [
    { id: "live", label: "Live Waterfall", icon: Activity },
    { id: "scenarios", label: "Scenario Lab", icon: ShieldAlert },
    { id: "benchmark", label: "Benchmark Suite", icon: BarChart3 },
    { id: "explain", label: "Explainability", icon: Cpu },
    { id: "dataset", label: "Dataset Studio", icon: Database },
  ];

  return (
    <header className="bg-[#0B0F19] border-b border-gray-800 sticky top-0 z-50 px-6 py-3">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Brand & Project Identity */}
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-cyan-950/70 border border-cyan-500/40 rounded-lg shadow-lg shadow-cyan-950/40">
            <Radio className="w-6 h-6 text-cyan-400 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-lg tracking-wider text-slate-100 uppercase">
                AURA-ES
              </span>
              <span className="bg-cyan-900/60 border border-cyan-500/40 text-cyan-300 text-xs px-2 py-0.5 rounded font-mono font-medium">
                SIH26055 • DRDO
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium">
              Closed-Loop Cognitive ES Surveillance Scheduler
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex space-x-1 bg-gray-900/80 p-1 rounded-xl border border-gray-800">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 shadow-sm"
                    : "text-slate-400 hover:text-slate-200 hover:bg-gray-800/60"
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? "text-cyan-400" : "text-slate-400"}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Status Indicators */}
        <div className="flex items-center space-x-4 text-xs font-mono">
          <div className="flex items-center space-x-2 bg-gray-900 px-3 py-1.5 rounded-lg border border-gray-800">
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                isConnected ? "bg-emerald-500 shadow-sm shadow-emerald-500/50 animate-ping" : "bg-rose-500"
              }`}
            />
            <span className={isConnected ? "text-emerald-400" : "text-rose-400"}>
              {isConnected ? "WS STREAMING" : "DISCONNECTED"}
            </span>
          </div>

          {isRunning && (
            <div className="hidden sm:flex items-center space-x-1.5 bg-cyan-950/40 border border-cyan-500/30 px-2.5 py-1 rounded-md text-cyan-300">
              <span className="animate-spin inline-block w-2.5 h-2.5 border-2 border-cyan-400 border-t-transparent rounded-full"></span>
              <span>{speedHz} Hz</span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
