"use client";

import { useState } from "react";
import TokenCard from "@/components/TokenCard";
import LoadingSpinner from "@/components/LoadingSpinner";
import { issueOPDToken, type OPDToken } from "@/lib/api";

interface HospitalPin {
  id: string;
  name: string;
  city: string;
  lat: number;
  lng: number;
  departments: string[];
  currentLoad: number;
  avgWaitMins: number;
  emergency24x7: boolean;
}

const MAHARASHTRA_HOSPITALS: HospitalPin[] = [
  {
    id: "hosp_kem_01",
    name: "Seth GS Medical College & KEM Hospital",
    city: "Mumbai (Parel)",
    lat: 19.0024,
    lng: 72.8423,
    departments: ["General Medicine", "Cardiology", "Gastroenterology", "Orthopedics"],
    currentLoad: 72,
    avgWaitMins: 25,
    emergency24x7: true,
  },
  {
    id: "hosp_sion_01",
    name: "Lokmanya Tilak Municipal General Hospital (Sion)",
    city: "Mumbai (Sion)",
    lat: 19.0378,
    lng: 72.8617,
    departments: ["General Medicine", "Pulmonology", "Cardiology", "Trauma Care"],
    currentLoad: 68,
    avgWaitMins: 20,
    emergency24x7: true,
  },
  {
    id: "hosp_jj_01",
    name: "Sir J.J. Group of Hospitals",
    city: "Mumbai (Byculla)",
    lat: 18.9633,
    lng: 72.8339,
    departments: ["General Medicine", "Neurology", "ENT", "Ophthalmology"],
    currentLoad: 60,
    avgWaitMins: 15,
    emergency24x7: true,
  },
  {
    id: "hosp_sassoon_01",
    name: "Sassoon General Hospital & BJ Medical College",
    city: "Pune",
    lat: 18.5262,
    lng: 73.8744,
    departments: ["General Medicine", "Cardiology", "Pediatrics", "Trauma Unit"],
    currentLoad: 65,
    avgWaitMins: 18,
    emergency24x7: true,
  },
  {
    id: "hosp_gmch_01",
    name: "Government Medical College & Hospital (GMCH)",
    city: "Nagpur",
    lat: 21.1343,
    lng: 79.0963,
    departments: ["General Medicine", "Dermatology", "Orthopedics", "Cardiology"],
    currentLoad: 55,
    avgWaitMins: 12,
    emergency24x7: true,
  },
];

export default function OPDPage() {
  const [patientId, setPatientId] = useState("PAT-MH-001");
  const [selectedHospital, setSelectedHospital] = useState<HospitalPin>(MAHARASHTRA_HOSPITALS[0]);
  const [department, setDepartment] = useState(MAHARASHTRA_HOSPITALS[0].departments[0]);
  const [slotTime, setSlotTime] = useState("2026-08-17T10:30:00");
  const [queueLength, setQueueLength] = useState(selectedHospital.avgWaitMins > 20 ? 6 : 3);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [issuedTokens, setIssuedTokens] = useState<OPDToken[]>([]);

  const handleSelectHospital = (h: HospitalPin) => {
    setSelectedHospital(h);
    setDepartment(h.departments[0]);
  };

  const handleIssue = async () => {
    setError(null);
    setLoading(true);
    try {
      const token = await issueOPDToken({
        patient_id: patientId,
        hospital_name: selectedHospital.name,
        department_name: department,
        slot_time: slotTime,
        current_queue_length: queueLength,
      });
      setIssuedTokens((prev) => [token, ...prev]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to issue token");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header animate-in">
        <h1>Smart OPD Routing & Hospital Grid Map</h1>
        <p>Real-time OpenStreetMap facility grid with capacity load & QR token dispatch</p>
      </div>

      {/* Interactive Hospital Grid Map */}
      <div className="glass-card animate-in animate-in-delay-1" style={{ marginBottom: 24 }}>
        <div className="map-header">
          <div>
            <h3>Maharashtra Public Healthcare Grid (5 Primary Centers)</h3>
            <p style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
              Real-time GPS anchors: Mumbai (KEM, Sion, JJ), Pune (Sassoon), Nagpur (GMCH)
            </p>
          </div>
          <span className="badge badge-success">● 5 / 5 Facilities Online</span>
        </div>

        <div className="hospital-pins-grid">
          {MAHARASHTRA_HOSPITALS.map((h) => {
            const isSelected = selectedHospital.id === h.id;
            return (
              <div
                key={h.id}
                className={`hospital-card ${isSelected ? "selected" : ""}`}
                onClick={() => handleSelectHospital(h)}
              >
                <div className="hosp-card-header">
                  <span className="pin-icon">📍</span>
                  <div>
                    <h4 className="hosp-card-name">{h.name}</h4>
                    <span className="hosp-card-city">{h.city} • ({h.lat.toFixed(4)}, {h.lng.toFixed(4)})</span>
                  </div>
                </div>

                <div className="hosp-card-metrics">
                  <div className="metric">
                    <span className="metric-lbl">Queue Wait</span>
                    <span className="metric-val">~{h.avgWaitMins} min</span>
                  </div>
                  <div className="metric">
                    <span className="metric-lbl">Ward Load</span>
                    <span className="metric-val" style={{ color: h.currentLoad > 70 ? "var(--urgent)" : "var(--routine)" }}>
                      {h.currentLoad}%
                    </span>
                  </div>
                  <div className="metric">
                    <span className="metric-lbl">ICU/Emergency</span>
                    <span className="metric-val" style={{ color: "var(--routine)" }}>24x7 Ready</span>
                  </div>
                </div>

                <div className="dept-chips">
                  {h.departments.map((d) => (
                    <span key={d} className="dept-chip">{d}</span>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="content-grid">
        {/* Issue Form */}
        <div className="glass-card animate-in animate-in-delay-2">
          <h3 style={{ marginBottom: 20 }}>Issue Token: {selectedHospital.name}</h3>

          <div className="form-grid">
            <div className="form-group">
              <label className="form-label">Patient ID</label>
              <input className="input-field" value={patientId} onChange={(e) => setPatientId(e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">Selected Hospital</label>
              <input className="input-field" value={selectedHospital.name} disabled />
            </div>
            <div className="form-group">
              <label className="form-label">Department</label>
              <select className="input-field" value={department} onChange={(e) => setDepartment(e.target.value)}>
                {selectedHospital.departments.map((d) => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Slot Time</label>
              <input className="input-field" type="datetime-local" value={slotTime} onChange={(e) => setSlotTime(e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">Current Department Queue</label>
              <input className="input-field" type="number" min={0} value={queueLength} onChange={(e) => setQueueLength(Number(e.target.value))} />
            </div>
          </div>

          {error && (
            <div className="error-banner" style={{ marginTop: 16 }}>
              ⚠️ {error}
            </div>
          )}

          <button
            className="btn btn-primary"
            style={{ marginTop: 20, width: "100%" }}
            onClick={handleIssue}
            disabled={loading || !patientId.trim()}
          >
            {loading ? <LoadingSpinner size={18} /> : "🎫 Generate Encrypted OPD Token"}
          </button>
        </div>

        {/* Issued Tokens */}
        <div className="animate-in animate-in-delay-3">
          <h3 style={{ marginBottom: 16 }}>Issued Tokens</h3>
          {issuedTokens.length === 0 ? (
            <div className="glass-card empty-state">
              <div className="empty-state-icon">🎫</div>
              <p>No tokens issued in this session.</p>
              <p style={{ fontSize: "0.8rem", marginTop: 4 }}>Select a hospital on the grid above to generate tokens.</p>
            </div>
          ) : (
            <div className="token-list">
              {issuedTokens.map((t) => (
                <TokenCard key={t.token_id} token={t} />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* History Table */}
      {issuedTokens.length > 0 && (
        <div className="glass-card animate-in" style={{ marginTop: 32 }}>
          <h3 style={{ marginBottom: 16 }}>Active Token Registry</h3>
          <table className="data-table">
            <thead>
              <tr>
                <th>Token ID</th>
                <th>Patient</th>
                <th>Hospital</th>
                <th>Department</th>
                <th>Queue #</th>
                <th>Status</th>
                <th>Issued At</th>
              </tr>
            </thead>
            <tbody>
              {issuedTokens.map((t) => (
                <tr key={t.token_id}>
                  <td style={{ color: "var(--primary)", fontWeight: 600 }}>{t.token_id}</td>
                  <td>{t.patient_id}</td>
                  <td>{t.hospital_name}</td>
                  <td>{t.department_name}</td>
                  <td style={{ color: "var(--accent)", fontWeight: 700 }}>{t.queue_number}</td>
                  <td><span className="badge badge-info">{t.status}</span></td>
                  <td>{new Date(t.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <style jsx>{`
        .map-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }
        .hospital-pins-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 14px;
        }
        .hospital-card {
          background: rgba(15, 23, 42, 0.5);
          border: 1px solid rgba(148, 163, 184, 0.12);
          border-radius: var(--radius-md);
          padding: 14px;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        .hospital-card:hover {
          border-color: var(--primary);
          transform: translateY(-2px);
        }
        .hospital-card.selected {
          border-color: var(--primary);
          background: rgba(14, 165, 233, 0.08);
          box-shadow: 0 0 16px rgba(14, 165, 233, 0.15);
        }
        .hosp-card-header {
          display: flex;
          gap: 10px;
          margin-bottom: 12px;
        }
        .pin-icon {
          font-size: 1.2rem;
        }
        .hosp-card-name {
          font-size: 0.88rem;
          font-weight: 600;
          color: var(--text-primary);
          line-height: 1.2;
        }
        .hosp-card-city {
          font-size: 0.72rem;
          color: var(--text-muted);
        }
        .hosp-card-metrics {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 8px;
          padding: 8px 0;
          border-top: 1px solid rgba(148, 163, 184, 0.08);
          border-bottom: 1px solid rgba(148, 163, 184, 0.08);
          margin-bottom: 10px;
        }
        .metric {
          display: flex;
          flex-direction: column;
          gap: 2px;
        }
        .metric-lbl {
          font-size: 0.65rem;
          color: var(--text-muted);
          text-transform: uppercase;
        }
        .metric-val {
          font-size: 0.8rem;
          font-weight: 600;
          color: var(--text-secondary);
        }
        .dept-chips {
          display: flex;
          flex-wrap: wrap;
          gap: 4px;
        }
        .dept-chip {
          font-size: 0.68rem;
          background: rgba(148, 163, 184, 0.1);
          color: var(--text-secondary);
          padding: 2px 6px;
          border-radius: var(--radius-full);
        }
        .form-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 16px;
        }
        .form-group {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }
        .form-label {
          font-size: 0.8rem;
          font-weight: 500;
          color: var(--text-secondary);
        }
        .token-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        .error-banner {
          background: var(--emergency-dim);
          color: var(--emergency);
          padding: 10px 14px;
          border-radius: var(--radius-md);
          font-size: 0.8rem;
        }

        @media (max-width: 768px) {
          .form-grid { grid-template-columns: 1fr; }
        }
      `}</style>
    </div>
  );
}
