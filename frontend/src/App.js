import React, { useEffect, useMemo, useState } from "react";
import AlertsPanel from "./AlertsPanel";
import VideoFeed from "./VideoFeed";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

async function post(path) {
  const res = await fetch(`${API_BASE}${path}`, { method: "POST" });
  if (!res.ok) {
    throw new Error(`Request failed for ${path}`);
  }
  return res.json();
}

async function fetchAlerts(limit = 30) {
  const res = await fetch(`${API_BASE}/alerts?limit=${limit}`);
  if (!res.ok) {
    throw new Error("Failed to fetch alerts");
  }
  return res.json();
}

export default function App() {
  const [running, setRunning] = useState(false);
  const [alerts, setAlerts] = useState([]);
  const [error, setError] = useState("");

  const stats = useMemo(() => {
    const counts = { intrusion: 0, loitering: 0, abandoned_object: 0 };
    for (const item of alerts) {
      if (counts[item.type] !== undefined) {
        counts[item.type] += 1;
      }
    }
    return counts;
  }, [alerts]);

  useEffect(() => {
    let mounted = true;

    async function pollAlerts() {
      try {
        const data = await fetchAlerts();
        if (mounted) {
          setAlerts(data);
        }
      } catch (err) {
        if (mounted) {
          setError(err.message);
        }
      }
    }

    pollAlerts();
    const timer = setInterval(pollAlerts, 3000);
    return () => {
      mounted = false;
      clearInterval(timer);
    };
  }, []);

  async function start() {
    setError("");
    try {
      await post("/start");
      setRunning(true);
    } catch (err) {
      setError(err.message);
    }
  }

  async function stop() {
    setError("");
    try {
      await post("/stop");
      setRunning(false);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <main className="app-shell">
      <section className="hero">
        <p className="eyebrow">Campus Security Intelligence</p>
        <h1>Real-Time Multi-Object Tracking System</h1>
        <p className="subtitle">
          Detect, track, and alert on loitering, restricted-zone intrusion, and abandoned objects from live CCTV.
        </p>
        <div className="controls">
          <button className="btn btn-start" onClick={start}>Start Detection</button>
          <button className="btn btn-stop" onClick={stop}>Stop Detection</button>
        </div>
        {error && <p className="error">{error}</p>}
      </section>

      <section className="stats-grid">
        <article className="stat-card">
          <h3>Intrusion</h3>
          <p>{stats.intrusion}</p>
        </article>
        <article className="stat-card">
          <h3>Loitering</h3>
          <p>{stats.loitering}</p>
        </article>
        <article className="stat-card">
          <h3>Abandoned</h3>
          <p>{stats.abandoned_object}</p>
        </article>
      </section>

      <section className="content-grid">
        <VideoFeed running={running} />
        <AlertsPanel alerts={alerts} />
      </section>
    </main>
  );
}
