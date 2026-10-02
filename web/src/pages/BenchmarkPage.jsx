import React, { useState, useEffect } from "react";
import { BarChart3, Download, Play, RefreshCw, CheckCircle2, TrendingUp, AlertTriangle } from "lucide-react";
import { runBenchmark, fetchLatestBenchmark } from "../api/client";

export default function BenchmarkPage({ presets = [] }) {
  const [benchmarkData, setBenchmarkData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [scenario, setScenario] = useState("periodic_emitters");
  const [numSeeds, setNumSeeds] = useState(10);

  useEffect(() => {
    loadLatest();
  }, []);

  async function loadLatest() {
    try {
      setLoading(true);
      const data = await fetchLatestBenchmark();
      setBenchmarkData(data);
    } catch (err) {
      console.error("Failed to load latest benchmark", err);
    } finally {
      setLoading(false);
    }
  }

  async function handleRunBenchmark() {
    try {
      setLoading(true);
      const data = await runBenchmark({
        scenario_id: scenario,
        num_seeds: numSeeds,
        base_seed: 100,
      });
      setBenchmarkData(data);
    } catch (err) {
      console.error("Failed to execute benchmark", err);
    } finally {
      setLoading(false);
    }
  }

  const summary = benchmarkData ? benchmarkData.summary : null;
  const scheds = benchmarkData ? benchmarkData.schedulers : [];
  const significance = benchmarkData ? benchmarkData.significance : {};

  return (
    <div className="space-y-6">
      {/* Benchmark Control Bar */}
      <div className="bg-[#0D1322] border border-gray-800 rounded-xl p-6 shadow-xl flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center space-x-2">
            <BarChart3 className="w-5 h-5 text-cyan-400" />
            <span>Multi-Seed Monte Carlo Benchmark Suite</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Empirical evaluation across 30+ seeds with paired Student's t-test and Wilcoxon signed-rank tests.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Scenario Selector */}
          <div className="bg-gray-900 border border-gray-800 px-3 py-1.5 rounded-lg text-xs">
            <span className="text-slate-400 mr-2">Scenario:</span>
            <select
              value={scenario}
              onChange={(e) => setScenario(e.target.value)}
              className="bg-transparent text-slate-200 font-medium focus:outline-none cursor-pointer"
            >
              {presets.map((p) => (
                <option key={p.id} value={p.id} className="bg-gray-900 text-white">
                  {p.name}
                </option>
              ))}
            </select>
          </div>

          {/* Seed Count */}
          <div className="bg-gray-900 border border-gray-800 px-3 py-1.5 rounded-lg text-xs">
            <span className="text-slate-400 mr-2">Seeds:</span>
            <select
              value={numSeeds}
              onChange={(e) => setNumSeeds(Number(e.target.value))}
              className="bg-transparent text-slate-200 font-medium focus:outline-none cursor-pointer"
            >
              <option value={5} className="bg-gray-900 text-white">5 Seeds (Fast)</option>
              <option value={10} className="bg-gray-900 text-white">10 Seeds</option>
              <option value={30} className="bg-gray-900 text-white">30 Seeds (DRDO Rigorous)</option>
            </select>
          </div>

          <button
            onClick={handleRunBenchmark}
            disabled={loading}
            className="flex items-center space-x-1.5 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white font-bold text-xs rounded-lg shadow-lg shadow-cyan-900/30 transition active:scale-95"
          >
            {loading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5 fill-current" />}
            <span>{loading ? "EXECUTING BENCHMARK..." : "RUN BENCHMARK"}</span>
          </button>

          <a
            href="http://localhost:8000/api/benchmark/export/csv"
            download
            className="flex items-center space-x-1 px-3 py-2 bg-gray-800 hover:bg-gray-700 text-slate-200 text-xs font-medium rounded-lg border border-gray-700 transition"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </a>
        </div>
      </div>

      {/* Comparative Results Table */}
      {summary && (
        <div className="bg-[#0D1322] border border-gray-800 rounded-xl p-6 shadow-xl overflow-x-auto">
          <div className="flex items-center justify-between pb-3 border-b border-gray-800 mb-4">
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wide">
              Comparative Benchmark Results ({benchmarkData.scenario_id} • {benchmarkData.num_seeds} seeds)
            </h3>
            <span className="text-xs text-slate-400 font-mono">Mean ± Standard Deviation</span>
          </div>

          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-gray-900/80 text-[11px] font-mono uppercase text-slate-400 border-b border-gray-800">
              <tr>
                <th className="py-3 px-4">Algorithm</th>
                <th className="py-3 px-4">Threat Intercept Rate</th>
                <th className="py-3 px-4">Periodic Revisit Rate</th>
                <th className="py-3 px-4">Mean TTFI (steps)</th>
                <th className="py-3 px-4">Dwell Efficiency</th>
                <th className="py-3 px-4">LO Retune (ms)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60 font-mono">
              {scheds.map((sid) => {
                const s = summary[sid];
                const isProposed = sid === "smart_scan";
                return (
                  <tr
                    key={sid}
                    className={isProposed ? "bg-cyan-950/20 font-bold text-cyan-200" : "hover:bg-gray-800/30"}
                  >
                    <td className="py-3 px-4 flex items-center space-x-2">
                      {isProposed && <span className="text-cyan-400">★</span>}
                      <span>{sid}</span>
                    </td>
                    <td className="py-3 px-4">
                      {(s.threat_intercept_rate.mean * 100).toFixed(1)}% ± {(s.threat_intercept_rate.std * 100).toFixed(1)}%
                    </td>
                    <td className="py-3 px-4">
                      {(s.periodic_revisit_rate.mean * 100).toFixed(1)}% ± {(s.periodic_revisit_rate.std * 100).toFixed(1)}%
                    </td>
                    <td className="py-3 px-4">
                      {s.mean_ttfi_steps.mean.toFixed(1)} ± {s.mean_ttfi_steps.std.toFixed(1)}
                    </td>
                    <td className="py-3 px-4">
                      {(s.dwell_efficiency.mean * 100).toFixed(1)}% ± {(s.dwell_efficiency.std * 100).toFixed(1)}%
                    </td>
                    <td className="py-3 px-4">
                      {s.total_retune_cost_ms.mean.toFixed(1)} ± {s.total_retune_cost_ms.std.toFixed(1)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Paired Statistical Significance Matrix */}
      {Object.keys(significance).length > 0 && (
        <div className="bg-[#0D1322] border border-gray-800 rounded-xl p-6 shadow-xl">
          <div className="pb-3 border-b border-gray-800 mb-4">
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wide flex items-center space-x-2">
              <TrendingUp className="w-4 h-4 text-emerald-400" />
              <span>Statistical Significance: SmartScan-BayesianRMAB vs Baselines</span>
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              Paired Student's t-test and Wilcoxon signed-rank test results. Significance threshold α = 0.05.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(significance).map(([baselineSid, metricsDict]) => (
              <div key={baselineSid} className="bg-gray-900/80 border border-gray-800 rounded-xl p-4">
                <h4 className="font-bold text-sm text-cyan-300 pb-2 border-b border-gray-800 mb-3">
                  vs {baselineSid}
                </h4>
                <div className="space-y-3 text-xs">
                  {Object.entries(metricsDict).map(([metricName, comp]) => (
                    <div key={metricName} className="flex flex-col bg-gray-950/60 p-2 rounded">
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300 font-medium capitalize">
                          {metricName.replace(/_/g, " ")}
                        </span>
                        <span
                          className={`font-mono font-bold text-[10px] px-1.5 py-0.5 rounded ${
                            comp.statistically_significant
                              ? "bg-emerald-950 text-emerald-300 border border-emerald-800"
                              : "bg-gray-800 text-slate-400"
                          }`}
                        >
                          {comp.significance_label}
                        </span>
                      </div>
                      <div className="text-[11px] font-mono text-slate-400 mt-1 flex justify-between">
                        <span>p = {comp.p_value_ttest}</span>
                        <span>Cohen's d = {comp.cohens_d}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
