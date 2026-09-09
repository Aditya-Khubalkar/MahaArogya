"use client";

import { useEffect, useState } from "react";
import { getWardPatients } from "@/lib/api";

export default function NurseWardPage() {
  const [patients, setPatients] = useState<any[]>([]);

  useEffect(() => {
    getWardPatients().then(setPatients).catch(console.error);
  }, []);

  return (
    <div className="animate-in">
      <div className="page-header">
        <h1>Nurse Ward</h1>
        <p>Patient vitals and ward overview</p>
      </div>

      <div className="glass-card">
        <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid var(--surface-border)" }}>
              <th style={{ padding: "12px", color: "var(--text-muted)" }}>Bed ID</th>
              <th style={{ padding: "12px", color: "var(--text-muted)" }}>Patient</th>
              <th style={{ padding: "12px", color: "var(--text-muted)" }}>HR</th>
              <th style={{ padding: "12px", color: "var(--text-muted)" }}>BP</th>
              <th style={{ padding: "12px", color: "var(--text-muted)" }}>SpO2</th>
              <th style={{ padding: "12px", color: "var(--text-muted)" }}>Temp</th>
              <th style={{ padding: "12px", color: "var(--text-muted)" }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {patients.map((p) => (
              <tr key={p.bed_id} style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                <td style={{ padding: "12px" }}>{p.bed_id}</td>
                <td style={{ padding: "12px" }}>{p.patient_name}</td>
                <td style={{ padding: "12px" }}>{p.heart_rate}</td>
                <td style={{ padding: "12px" }}>{p.blood_pressure}</td>
                <td style={{ padding: "12px" }}>{p.oxygen_saturation}%</td>
                <td style={{ padding: "12px" }}>{p.temperature}°F</td>
                <td style={{ padding: "12px", color: p.status === "STABLE" ? "var(--routine)" : "var(--urgent)" }}>
                  {p.status}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
