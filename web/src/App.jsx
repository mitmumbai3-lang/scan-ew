import React, { useState, useEffect, useRef } from "react";
import Navbar from "./components/Navbar";
import LiveScanPage from "./pages/LiveScanPage";
import ScenarioLabPage from "./pages/ScenarioLabPage";
import BenchmarkPage from "./pages/BenchmarkPage";
import ExplainabilityPage from "./pages/ExplainabilityPage";
import DatasetPage from "./pages/DatasetPage";
import {
  fetchPresets,
  fetchSchedulers,
  initSim,
  stepSim,
  playSim,
  pauseSim,
  resetSim,
  fetchState,
  connectLiveWebSocket,
} from "./api/client";

export default function App() {
  const [activeTab, setActiveTab] = useState("live");
  const [isConnected, setIsConnected] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [speedHz, setSpeedHz] = useState(20);

  const [presets, setPresets] = useState([]);
  const [schedulers, setSchedulers] = useState([]);
  const [selectedScenario, setSelectedScenario] = useState("periodic_emitters");
  const [selectedScheduler, setSelectedScheduler] = useState("smart_scan");
  const [numBands, setNumBands] = useState(16);
  const [showGroundTruth, setShowGroundTruth] = useState(true);

  // Simulation state
  const [history, setHistory] = useState([]);
  const [currentBand, setCurrentBand] = useState(0);
  const [beliefs, setBeliefs] = useState(Array(16).fill(0.5));
  const [metrics, setMetrics] = useState({});
  const [explainability, setExplainability] = useState({});
  const [emitters, setEmitters] = useState([]);
  const [latestStepData, setLatestStepData] = useState(null);

  const wsRef = useRef(null);

  // Load initial presets, schedulers, and session state
  useEffect(() => {
    async function loadInitial() {
      try {
        const [presetList, schedList, state] = await Promise.all([
          fetchPresets(),
          fetchSchedulers(),
          fetchState(),
        ]);
        setPresets(presetList);
        setSchedulers(schedList);
        if (state) {
          setSelectedScenario(state.scenario_id);
          setSelectedScheduler(state.scheduler_id);
          setNumBands(state.num_bands || 16);
          setBeliefs(state.beliefs || Array(16).fill(0.5));
          setMetrics(state.metrics || {});
          setExplainability(state.explainability || {});
          setEmitters(state.emitters || []);
          setIsRunning(state.is_running || false);
          setSpeedHz(state.speed_hz || 20);
        }
      } catch (err) {
        console.error("Failed to load initial metadata", err);
      }
    }
    loadInitial();

    // Connect WebSocket
    const ws = connectLiveWebSocket(
      (msg) => {
        if (msg.type === "sim_step") {
          const d = msg.data;
          setLatestStepData(d);
          setCurrentBand(d.action);
          setBeliefs(d.beliefs || []);
          setMetrics(d.metrics || {});
          setExplainability(d.explainability || {});
          setHistory((prev) => {
            const updated = [...prev, d];
            return updated.length > 70 ? updated.slice(-70) : updated;
          });
          if (d.done) {
            setIsRunning(false);
          }
        } else if (msg.type === "init_state") {
          const s = msg.data;
          setBeliefs(s.beliefs || []);
          setMetrics(s.metrics || {});
          setExplainability(s.explainability || {});
          setEmitters(s.emitters || []);
          setIsRunning(s.is_running || false);
        }
      },
      () => setIsConnected(true),
      () => setIsConnected(false)
    );
    wsRef.current = ws;

    return () => {
      ws.close();
    };
  }, []);

  async function handlePlay() {
    setIsRunning(true);
    await playSim(speedHz);
  }

  async function handlePause() {
    setIsRunning(false);
    await pauseSim();
  }

  async function handleStep(steps = 1) {
    const res = await stepSim(steps);
    if (res && res.latest) {
      const d = res.latest;
      setLatestStepData(d);
      setCurrentBand(d.action);
      setBeliefs(d.beliefs || []);
      setMetrics(d.metrics || {});
      setExplainability(d.explainability || {});
      setHistory((prev) => {
        const updated = [...prev, d];
        return updated.length > 70 ? updated.slice(-70) : updated;
      });
    }
  }

  async function handleReset() {
    setIsRunning(false);
    setHistory([]);
    const res = await resetSim();
    if (res && res.state) {
      setBeliefs(res.state.beliefs || []);
      setMetrics(res.state.metrics || {});
      setExplainability(res.state.explainability || {});
      setEmitters(res.state.emitters || []);
      setCurrentBand(0);
    }
  }

  async function handleScenarioChange(scenId) {
    setSelectedScenario(scenId);
    setHistory([]);
    setIsRunning(false);
    const res = await initSim({
      scenario_id: scenId,
      scheduler_id: selectedScheduler,
      seed: 42,
      num_bands: numBands,
      speed_hz: speedHz,
    });
    if (res && res.state) {
      setBeliefs(res.state.beliefs || []);
      setMetrics(res.state.metrics || {});
      setExplainability(res.state.explainability || {});
      setEmitters(res.state.emitters || []);
      setCurrentBand(0);
    }
  }

  async function handleSchedulerChange(schedId) {
    setSelectedScheduler(schedId);
    setHistory([]);
    setIsRunning(false);
    const res = await initSim({
      scenario_id: selectedScenario,
      scheduler_id: schedId,
      seed: 42,
      num_bands: numBands,
      speed_hz: speedHz,
    });
    if (res && res.state) {
      setBeliefs(res.state.beliefs || []);
      setMetrics(res.state.metrics || {});
      setExplainability(res.state.explainability || {});
      setEmitters(res.state.emitters || []);
    }
  }

  return (
    <div className="min-h-screen bg-[#070B14] flex flex-col justify-between">
      <div>
        <Navbar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          isConnected={isConnected}
          isRunning={isRunning}
          speedHz={speedHz}
        />

        <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
          {activeTab === "live" && (
            <LiveScanPage
              history={history}
              latestStepData={latestStepData}
              currentBand={currentBand}
              beliefs={beliefs}
              metrics={metrics}
              explainability={explainability}
              numBands={numBands}
              isRunning={isRunning}
              onPlay={handlePlay}
              onPause={handlePause}
              onStep={handleStep}
              onReset={handleReset}
              speedHz={speedHz}
              onSpeedChange={(hz) => {
                setSpeedHz(hz);
                if (isRunning) playSim(hz);
              }}
              presets={presets}
              selectedScenario={selectedScenario}
              onScenarioChange={handleScenarioChange}
              schedulers={schedulers}
              selectedScheduler={selectedScheduler}
              onSchedulerChange={handleSchedulerChange}
              showGroundTruth={showGroundTruth}
              setShowGroundTruth={setShowGroundTruth}
            />
          )}

          {activeTab === "scenarios" && (
            <ScenarioLabPage
              presets={presets}
              selectedScenario={selectedScenario}
              onScenarioChange={handleScenarioChange}
              emitters={emitters}
            />
          )}

          {activeTab === "benchmark" && <BenchmarkPage presets={presets} />}

          {activeTab === "explain" && (
            <ExplainabilityPage
              explainability={explainability}
              currentBand={currentBand}
              numBands={numBands}
            />
          )}

          {activeTab === "dataset" && (
            <DatasetPage
              onDatasetLoaded={async () => {
                const s = await fetchState();
                if (s) {
                  setEmitters(s.emitters || []);
                  setSelectedScenario(s.scenario_id);
                  setNumBands(s.num_bands);
                  setHistory([]);
                }
              }}
            />
          )}
        </main>
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-900 bg-[#0B0F19] py-4 text-center text-xs text-slate-500 font-mono">
        DRDO Problem Statement SIH26055 • "Smart Scan Strategy for Electronic Warfare" • Purely Synthetic Research Simulation
      </footer>
    </div>
  );
}
