import React, { useMemo } from "react";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export default function VideoFeed({ running }) {
  const streamUrl = useMemo(() => `${API_BASE}/video_feed?ts=${Date.now()}`, []);

  return (
    <section className="panel video-panel">
      <h2>Live Surveillance Feed</h2>
      <div className="video-wrapper">
        {running ? (
          <img src={streamUrl} alt="Live processed stream" className="video-stream" />
        ) : (
          <div className="video-placeholder">Press Start to begin real-time analysis</div>
        )}
      </div>
    </section>
  );
}
