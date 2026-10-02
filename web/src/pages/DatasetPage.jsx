import React, { useState, useEffect } from "react";
import { Database, Upload, FileText, Download, CheckCircle2, AlertCircle } from "lucide-react";
import { fetchSampleDatasets, uploadDataset } from "../api/client";

export default function DatasetPage({ onDatasetLoaded }) {
  const [samples, setSamples] = useState(null);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchSampleDatasets()
      .then((data) => setSamples(data))
      .catch((err) => console.error("Error loading sample datasets", err));
  }, []);

  async function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    try {
      setUploading(true);
      setUploadStatus(null);
      const res = await uploadDataset(file);
      setUploadStatus({ success: true, message: res.message, details: res });
      onDatasetLoaded && onDatasetLoaded();
    } catch (err) {
      setUploadStatus({ success: false, message: err.message || "Upload failed" });
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="bg-[#0D1322] border border-gray-800 rounded-xl p-6 shadow-xl">
        <h2 className="text-lg font-bold text-slate-100 flex items-center space-x-2">
          <Database className="w-5 h-5 text-cyan-400" />
          <span>Dataset Studio & Scenario Replayer</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Import external synthetic emitter datasets (CSV / JSON) or download compliant templates to evaluate
          custom operational test vectors against the smart scan scheduler.
        </p>

        {/* Upload Zone */}
        <div className="mt-6 border-2 border-dashed border-gray-800 hover:border-cyan-500/50 rounded-xl p-8 text-center transition bg-gray-950/40">
          <Upload className="w-8 h-8 text-cyan-400 mx-auto mb-2 animate-bounce" />
          <h4 className="text-sm font-bold text-slate-200">Upload Scenario File</h4>
          <p className="text-xs text-slate-500 mt-1">Supports structured CSV or JSON formatted emitter scenarios</p>

          <label className="mt-4 inline-flex items-center space-x-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs rounded-lg cursor-pointer shadow-lg shadow-cyan-900/30 transition">
            <span>{uploading ? "Parsing File..." : "Choose File (.csv, .json)"}</span>
            <input
              type="file"
              accept=".csv,.json"
              onChange={handleFileUpload}
              disabled={uploading}
              className="hidden"
            />
          </label>
        </div>

        {/* Upload feedback */}
        {uploadStatus && (
          <div
            className={`mt-4 p-4 rounded-lg flex items-center space-x-3 text-xs ${
              uploadStatus.success
                ? "bg-emerald-950/40 border border-emerald-500/50 text-emerald-300"
                : "bg-rose-950/40 border border-rose-500/50 text-rose-300"
            }`}
          >
            {uploadStatus.success ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
            )}
            <div>
              <span className="font-bold">{uploadStatus.message}</span>
              {uploadStatus.details && (
                <div className="text-[11px] font-mono text-slate-400 mt-1">
                  Bands: {uploadStatus.details.num_bands} | Loaded {uploadStatus.details.emitter_count} emitters
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Sample Dataset Inspection */}
      {samples && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* CSV Sample */}
          <div className="bg-[#0D1322] border border-gray-800 rounded-xl p-5 shadow-xl flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between pb-2 border-b border-gray-800 mb-3">
                <span className="text-xs font-bold text-slate-200 flex items-center space-x-1.5">
                  <FileText className="w-4 h-4 text-cyan-400" />
                  <span>Standard CSV Format (`sample_dense_radar.csv`)</span>
                </span>
              </div>
              <pre className="p-3 bg-gray-950 rounded text-[10px] font-mono text-cyan-300 overflow-x-auto border border-gray-800/80 max-h-52">
                {samples.csv_sample}
              </pre>
            </div>
          </div>

          {/* JSON Sample */}
          <div className="bg-[#0D1322] border border-gray-800 rounded-xl p-5 shadow-xl flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between pb-2 border-b border-gray-800 mb-3">
                <span className="text-xs font-bold text-slate-200 flex items-center space-x-1.5">
                  <FileText className="w-4 h-4 text-purple-400" />
                  <span>Configurable JSON Format (`sample_agile_scenario.json`)</span>
                </span>
              </div>
              <pre className="p-3 bg-gray-950 rounded text-[10px] font-mono text-purple-300 overflow-x-auto border border-gray-800/80 max-h-52">
                {JSON.stringify(samples.json_sample, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
