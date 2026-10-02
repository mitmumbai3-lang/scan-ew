/**
 * API client and WebSocket service for EW Smart Scan backend.
 */
const host = typeof window !== "undefined" && window.location.hostname ? window.location.hostname : "127.0.0.1";
const API_BASE = `http://${host}:8000`;
const WS_BASE = `ws://${host}:8000`;

export async function fetchPresets() {
  const res = await fetch(`${API_BASE}/api/sim/presets`);
  return res.json();
}

export async function fetchSchedulers() {
  const res = await fetch(`${API_BASE}/api/sim/schedulers`);
  return res.json();
}

export async function initSim(params) {
  const res = await fetch(`${API_BASE}/api/sim/init`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  return res.json();
}

export async function stepSim(steps = 1) {
  const res = await fetch(`${API_BASE}/api/sim/step`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ steps }),
  });
  return res.json();
}

export async function playSim(speed_hz = 20) {
  const res = await fetch(`${API_BASE}/api/sim/play?speed_hz=${speed_hz}`, {
    method: "POST",
  });
  return res.json();
}

export async function pauseSim() {
  const res = await fetch(`${API_BASE}/api/sim/pause`, {
    method: "POST",
  });
  return res.json();
}

export async function resetSim() {
  const res = await fetch(`${API_BASE}/api/sim/reset`, {
    method: "POST",
  });
  return res.json();
}

export async function fetchState() {
  const res = await fetch(`${API_BASE}/api/sim/state`);
  return res.json();
}

export async function runBenchmark(params) {
  const res = await fetch(`${API_BASE}/api/benchmark/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  return res.json();
}

export async function fetchLatestBenchmark() {
  const res = await fetch(`${API_BASE}/api/benchmark/latest`);
  return res.json();
}

export async function fetchSampleDatasets() {
  const res = await fetch(`${API_BASE}/api/dataset/samples`);
  return res.json();
}

export async function uploadDataset(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/api/dataset/upload`, {
    method: "POST",
    body: formData,
  });
  return res.json();
}

export function connectLiveWebSocket(onMessage, onOpen, onClose) {
  let ws = null;
  let isClosedExplicitly = false;
  let reconnectTimer = null;

  function connect() {
    if (isClosedExplicitly) return;
    try {
      ws = new WebSocket(`${WS_BASE}/ws/live`);
      ws.onopen = () => {
        onOpen && onOpen();
      };
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage && onMessage(data);
        } catch (err) {
          console.error("WS Parse error", err);
        }
      };
      ws.onclose = () => {
        onClose && onClose();
        if (!isClosedExplicitly) {
          clearTimeout(reconnectTimer);
          reconnectTimer = setTimeout(connect, 2000);
        }
      };
      ws.onerror = () => {
        try {
          if (ws) ws.close();
        } catch (e) {}
      };
    } catch (err) {
      if (!isClosedExplicitly) {
        clearTimeout(reconnectTimer);
        reconnectTimer = setTimeout(connect, 2000);
      }
    }
  }

  connect();

  return {
    close: () => {
      isClosedExplicitly = true;
      clearTimeout(reconnectTimer);
      if (ws) {
        try {
          ws.close();
        } catch (e) {}
      }
    },
  };
}
