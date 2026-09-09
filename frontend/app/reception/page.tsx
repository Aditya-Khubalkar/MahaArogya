"use client";
import { useState } from "react";
import LoadingSpinner from "@/components/LoadingSpinner";
import DataTable from "@/components/DataTable";
import { checkinPatient, type PatientQueueEntry } from "@/lib/api";

export default function ReceptionPage() {
  const [tokenId, setTokenId] = useState("");
  const [staffId, setStaffId] = useState("reception_staff_01");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [queue, setQueue] = useState<PatientQueueEntry[]>([]);

  const handleCheckin = async () => {
    if (!tokenId.trim()) return;
    setError(null);
    setLoading(true);
    try {
      const entry = await checkinPatient({ token_id: tokenId.trim(), staff_user_id: staffId });
      setQueue((prev) => {
        const idx = prev.findIndex((e) => e.token_id === entry.token_id);
        if (idx >= 0) {
          const updated = [...prev];
          updated[idx] = entry;
          return updated;
        }
        return [entry, ...prev];
      });
      setTokenId("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Check-in failed");
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const map: Record<string, string> = {
      ISSUED: "badge-info",
      CHECKED_IN: "badge-success",
      IN_CONSULTATION: "badge-priority",
      COMPLETED: "badge-neutral",
      NO_SHOW: "badge-emergency",
    };
    return map[status] ?? "badge-neutral";
  };

  return (
    <div>
      <div className="page-header animate-in">
        <h1>🏥 Reception Check-in</h1>
        <p>Patient arrival desk — scan or enter token ID to check in</p>
      </div>

      {/* Check-in Panel */}
      <div className="glass-card animate-in animate-in-delay-1 checkin-panel">
        <div className="checkin-row">
          <div className="checkin-icon">🎫</div>
          <div className="checkin-form">
            <input
              className="input-field checkin-input"
              placeholder="Enter or scan OPD Token ID (e.g., OPD-MUM-8921)"
              value={tokenId}
              onChange={(e) => setTokenId(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleCheckin()}
              disabled={loading}
            />
            <select className="input-field staff-select" value={staffId} onChange={(e) => setStaffId(e.target.value)}>
              <option value="reception_staff_01">Reception Staff 01</option>
              <option value="reception_staff_02">Reception Staff 02</option>
              <option value="reception_staff_03">Reception Staff 03</option>
            </select>
            <button className="btn btn-primary" onClick={handleCheckin} disabled={loading || !tokenId.trim()}>
              {loading ? <LoadingSpinner size={18} /> : "✅ Check In"}
            </button>
          </div>
        </div>
        {error && (
          <div className="error-banner">⚠️ {error}</div>
        )}
      </div>

      {/* Queue Table */}
      <div className="glass-card animate-in animate-in-delay-2" style={{ marginTop: 24 }}>
        <div className="queue-header">
          <h3>Patient Queue</h3>
          <span className="badge badge-info">{queue.length} patients</span>
        </div>

        <DataTable 
          columns={[
            { key: "token_id", header: "Token ID", render: (e: any) => <span style={{ color: "var(--primary)", fontWeight: 600 }}>{e.token_id}</span> },
            { key: "patient_id", header: "Patient ID" },
            { key: "department_name", header: "Department" },
            { key: "queue_number", header: "Queue #", render: (e: any) => <span style={{ color: "var(--accent)", fontWeight: 700, fontSize: "1.1rem" }}>{e.queue_number}</span> },
            { key: "arrival_status", header: "Status", render: (e: any) => <span className={`badge ${getStatusBadge(e.arrival_status)}`}>{e.arrival_status}</span> },
            { key: "checked_in_at", header: "Checked In At", render: (e: any) => <span>{e.checked_in_at ? new Date(e.checked_in_at).toLocaleString() : "—"}</span> }
          ]} 
          data={queue} 
          emptyMessage="No patients in queue. Check in a patient to see them here." 
        />
      </div>

      {/* Status Legend */}
      <div className="glass-card animate-in animate-in-delay-3" style={{ marginTop: 24 }}>
        <h3 style={{ marginBottom: 12 }}>Status Legend</h3>
        <div className="legend-grid">
          {[
            { status: "ISSUED", desc: "Token issued, patient not yet arrived", badge: "badge-info" },
            { status: "CHECKED_IN", desc: "Patient has arrived and checked in", badge: "badge-success" },
            { status: "IN_CONSULTATION", desc: "Patient is with the doctor", badge: "badge-priority" },
            { status: "COMPLETED", desc: "Visit complete", badge: "badge-neutral" },
            { status: "NO_SHOW", desc: "Patient did not arrive", badge: "badge-emergency" },
          ].map((item) => (
            <div key={item.status} className="legend-item">
              <span className={`badge ${item.badge}`}>{item.status}</span>
              <span className="legend-desc">{item.desc}</span>
            </div>
          ))}
        </div>
      </div>

      <style jsx>{`
        .checkin-panel {
          padding: 24px;
        }
        .checkin-row {
          display: flex;
          align-items: center;
          gap: 20px;
        }
        .checkin-icon {
          font-size: 3rem;
          flex-shrink: 0;
        }
        .checkin-form {
          flex: 1;
          display: flex;
          gap: 12px;
          align-items: center;
        }
        .checkin-input { flex: 1; }
        .staff-select { width: 200px; }

        .error-banner {
          background: var(--emergency-dim);
          color: var(--emergency);
          padding: 10px 14px;
          border-radius: var(--radius-md);
          font-size: 0.8rem;
          margin-top: 12px;
        }

        .queue-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 16px;
        }

        .legend-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
          gap: 12px;
        }
        .legend-item {
          display: flex;
          align-items: center;
          gap: 10px;
        }
        .legend-desc {
          font-size: 0.8rem;
          color: var(--text-secondary);
        }

        @media (max-width: 768px) {
          .checkin-form {
            flex-direction: column;
            gap: 8px;
          }
          .staff-select { width: 100%; }
        }
      `}</style>
    </div>
  );
}
