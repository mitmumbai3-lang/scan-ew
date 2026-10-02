import React from "react";
import WaterfallCanvas from "../components/WaterfallCanvas";
import BeliefBarChart from "../components/BeliefBarChart";
import MetricCards from "../components/MetricCards";
import Controls from "../components/Controls";
import ExplainabilityDrawer from "../components/ExplainabilityDrawer";

export default function LiveScanPage({
  history,
  latestStepData,
  currentBand,
  beliefs,
  metrics,
  explainability,
  numBands,
  isRunning,
  onPlay,
  onPause,
  onStep,
  onReset,
  speedHz,
  onSpeedChange,
  presets,
  selectedScenario,
  onScenarioChange,
  schedulers,
  selectedScheduler,
  onSchedulerChange,
  showGroundTruth,
  setShowGroundTruth,
}) {
  return (
    <div className="space-y-4">
      {/* Top Metrics Cards */}
      <MetricCards metrics={metrics} />

      {/* Control Bar */}
      <Controls
        isRunning={isRunning}
        onPlay={onPlay}
        onPause={onPause}
        onStep={onStep}
        onReset={onReset}
        speedHz={speedHz}
        onSpeedChange={onSpeedChange}
        presets={presets}
        selectedScenario={selectedScenario}
        onScenarioChange={onScenarioChange}
        schedulers={schedulers}
        selectedScheduler={selectedScheduler}
        onSchedulerChange={onSchedulerChange}
      />

      {/* Main Grid: Waterfall + Belief Map */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Waterfall Spectrogram (Left 7 Cols) */}
        <div className="lg:col-span-7">
          <WaterfallCanvas
            history={history}
            numBands={numBands}
            showGroundTruth={showGroundTruth}
            setShowGroundTruth={setShowGroundTruth}
          />
        </div>

        {/* Live Belief State & Priority (Right 5 Cols) */}
        <div className="lg:col-span-5 space-y-4">
          <BeliefBarChart
            beliefs={beliefs}
            components={explainability.components || {}}
            currentBand={currentBand}
            numBands={numBands}
          />

          <ExplainabilityDrawer
            explainability={explainability}
            chosenBand={currentBand}
            numBands={numBands}
          />
        </div>
      </div>
    </div>
  );
}
