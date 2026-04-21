import React from "react";

export default function AlertsPanel({ alerts }) {
  return (
    <section className="panel alerts-panel">
      <h2>Recent Alerts</h2>
      <div className="alerts-list">
        {alerts.length === 0 && <p className="muted">No alerts captured yet.</p>}
        {alerts.map((a, idx) => (
          <article key={`${a.timestamp}-${a.object_id}-${idx}`} className="alert-card">
            <header>
              <span className="tag">{a.type}</span>
              <time>{new Date(a.timestamp).toLocaleString()}</time>
            </header>
            <p>{a.message}</p>
            <small>Object ID: {a.object_id}</small>
          </article>
        ))}
      </div>
    </section>
  );
}
