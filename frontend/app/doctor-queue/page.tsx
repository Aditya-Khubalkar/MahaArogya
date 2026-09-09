"use client";

import { useEffect, useState } from "react";
import { getDoctorQueue } from "@/lib/api";

export default function DoctorQueuePage() {
  const [queue, setQueue] = useState<any[]>([]);

  useEffect(() => {
    getDoctorQueue().then(setQueue).catch(console.error);
  }, []);

  return (
    <div className="animate-in">
      <div className="page-header">
        <h1>Doctor Queue</h1>
        <p>Consultation workflow</p>
      </div>

      <div className="glass-card" style={{ marginBottom: "20px", padding: "16px", borderLeft: "4px solid var(--primary)" }}>
        <h3>Consultation Banner</h3>
        <p style={{ color: "var(--text-muted)", marginTop: "8px" }}>
          Next patient is <strong>{queue.length > 0 ? queue[0].patient_name : "None"}</strong>. Estimated wait time for others is updated.
        </p>
      </div>

      <div className="glass-card">
        <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid var(--surface-border)" }}>
              <th style={{ padding: "12px", color: "var(--text-muted)" }}>Token</th>
              <th style={{ padding: "12px", color: "var(--text-muted)" }}>Patient</th>
              <th style={{ padding: "12px", color: "var(--text-muted)" }}>Age/Gender</th>
              <th style={{ padding: "12px", color: "var(--text-muted)" }}>Triage Category</th>
              <th style={{ padding: "12px", color: "var(--text-muted)" }}>Condition</th>
              <th style={{ padding: "12px", color: "var(--text-muted)" }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {queue.map((q) => (
              <tr key={q.token_id} style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                <td style={{ padding: "12px" }}>{q.token_id}</td>
                <td style={{ padding: "12px" }}>{q.patient_name}</td>
                <td style={{ padding: "12px" }}>{q.age} / {q.gender}</td>
                <td style={{ padding: "12px" }}>
                  <span style={{ 
                    padding: "4px 8px", 
                    borderRadius: "4px", 
                    fontSize: "0.8rem", 
                    backgroundColor: q.triage_category === "PRIORITY" ? "var(--priority)" : "var(--routine)" 
                  }}>
                    {q.triage_category}
                  </span>
                </td>
                <td style={{ padding: "12px" }}>{q.predicted_condition}</td>
                <td style={{ padding: "12px" }}>{q.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
