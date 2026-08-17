"use client";
import type { OPDToken } from "@/lib/api";

interface TokenCardProps {
  token: OPDToken;
}

export default function TokenCard({ token }: TokenCardProps) {
  return (
    <div className="token-card glass-card">
      <div className="token-header">
        <div className="token-id-badge">
          <span className="token-hash">#</span>
          <span className="token-id">{token.token_id}</span>
        </div>
        <span className={`badge ${token.status === "CHECKED_IN" ? "badge-success" : "badge-info"}`}>
          {token.status}
        </span>
      </div>

      <div className="token-details">
        <div className="detail-row">
          <span className="detail-label">Patient</span>
          <span className="detail-value">{token.patient_id}</span>
        </div>
        <div className="detail-row">
          <span className="detail-label">Hospital</span>
          <span className="detail-value">{token.hospital_name}</span>
        </div>
        <div className="detail-row">
          <span className="detail-label">Department</span>
          <span className="detail-value">{token.department_name}</span>
        </div>
        <div className="detail-row">
          <span className="detail-label">Slot</span>
          <span className="detail-value">{token.slot_time}</span>
        </div>
        <div className="detail-row">
          <span className="detail-label">Queue #</span>
          <span className="detail-value queue-number">{token.queue_number}</span>
        </div>
      </div>

      {/* QR Code representation */}
      <div className="qr-section">
        <div className="qr-placeholder">
          <span className="qr-icon">📱</span>
          <span className="qr-label">QR Code</span>
        </div>
        <code className="qr-payload">{token.qr_payload.substring(0, 60)}...</code>
      </div>

      <div className="token-footer">
        <span className="token-time">Issued: {new Date(token.created_at).toLocaleString()}</span>
      </div>

      <style jsx>{`
        .token-card {
          position: relative;
          overflow: hidden;
        }
        .token-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          height: 3px;
          background: linear-gradient(90deg, var(--primary), var(--accent));
        }

        .token-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 16px;
          padding-top: 4px;
        }
        .token-id-badge {
          display: flex;
          align-items: baseline;
          gap: 2px;
        }
        .token-hash {
          font-size: 0.9rem;
          color: var(--text-muted);
          font-weight: 600;
        }
        .token-id {
          font-size: 1.1rem;
          font-weight: 700;
          color: var(--primary);
          letter-spacing: -0.01em;
        }

        .token-details {
          display: flex;
          flex-direction: column;
          gap: 8px;
          margin-bottom: 16px;
        }
        .detail-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        .detail-label {
          font-size: 0.8rem;
          color: var(--text-muted);
          font-weight: 500;
        }
        .detail-value {
          font-size: 0.875rem;
          color: var(--text-primary);
          font-weight: 500;
        }
        .queue-number {
          font-size: 1.2rem;
          font-weight: 700;
          color: var(--accent);
        }

        .qr-section {
          background: var(--bg-secondary);
          border-radius: var(--radius-md);
          padding: 14px;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 8px;
          margin-bottom: 12px;
        }
        .qr-placeholder {
          display: flex;
          align-items: center;
          gap: 6px;
          color: var(--text-secondary);
        }
        .qr-icon { font-size: 1.5rem; }
        .qr-label { font-size: 0.8rem; font-weight: 500; }
        .qr-payload {
          font-size: 0.65rem;
          color: var(--text-muted);
          word-break: break-all;
          max-width: 100%;
          text-align: center;
        }

        .token-footer {
          text-align: right;
        }
        .token-time {
          font-size: 0.7rem;
          color: var(--text-muted);
        }
      `}</style>
    </div>
  );
}
