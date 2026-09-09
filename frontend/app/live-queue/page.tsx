"use client";

import { useEffect, useState } from "react";
import { getLiveQueue, QueueItem } from "@/lib/api";

export default function LiveQueuePage() {
  const [queue, setQueue] = useState<QueueItem[]>([]);

  useEffect(() => {
    getLiveQueue().then(setQueue).catch(console.error);
  }, []);

  return (
    <div className="animate-in">
      <div className="page-header">
        <h1>Live Queue</h1>
        <p>Current patient waiting list</p>
      </div>
      
      <div className="glass-card">
        <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid var(--surface-border)" }}>
              <th style={{ padding: "12px", color: "var(--text-muted)" }}>Token</th>
              <th style={{ padding: "12px", color: "var(--text-muted)" }}>Patient</th>
              <th style={{ padding: "12px", color: "var(--text-muted)" }}>Department</th>
              <th style={{ padding: "12px", color: "var(--text-muted)" }}>Status</th>
              <th style={{ padding: "12px", color: "var(--text-muted)" }}>Est. Wait</th>
            </tr>
          </thead>
          <tbody>
            {queue.map((q) => (
              <tr key={q.token_id} style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                <td style={{ padding: "12px" }}>{q.token_id}</td>
                <td style={{ padding: "12px" }}>{q.patient_name}</td>
                <td style={{ padding: "12px" }}>{q.department}</td>
                <td style={{ padding: "12px" }}>{q.status}</td>
                <td style={{ padding: "12px" }}>{q.estimated_wait_time} min</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
