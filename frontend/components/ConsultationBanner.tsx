"use client";

interface ConsultationBannerProps {
  patientName: string;
  age: number;
  gender: string;
  onEndConsultation?: () => void;
}

export default function ConsultationBanner({ patientName, age, gender, onEndConsultation }: ConsultationBannerProps) {
  return (
    <div className="consultation-banner">
      <div className="patient-info">
        <div className="avatar">
          {patientName.charAt(0)}
        </div>
        <div>
          <h2 className="patient-name">Active Consultation: {patientName}</h2>
          <span className="patient-meta">{age} yrs, {gender}</span>
        </div>
      </div>
      
      {onEndConsultation && (
        <button className="btn-end" onClick={onEndConsultation}>
          End Consultation
        </button>
      )}

      <style jsx>{`
        .consultation-banner {
          background: linear-gradient(90deg, rgba(16, 185, 129, 0.1) 0%, rgba(30, 41, 59, 0.5) 100%);
          border: 1px solid var(--primary-dim);
          border-left: 4px solid var(--primary);
          border-radius: var(--radius-lg);
          padding: 16px 24px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 24px;
        }

        .patient-info {
          display: flex;
          align-items: center;
          gap: 16px;
        }

        .avatar {
          width: 48px;
          height: 48px;
          background: var(--primary);
          color: white;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.5rem;
          font-weight: 700;
        }

        .patient-name {
          margin: 0;
          font-size: 1.25rem;
          color: var(--text-primary);
        }

        .patient-meta {
          font-size: 0.85rem;
          color: var(--text-secondary);
        }

        .btn-end {
          background: rgba(239, 68, 68, 0.1);
          color: #ef4444;
          border: 1px solid rgba(239, 68, 68, 0.2);
          padding: 8px 16px;
          border-radius: var(--radius-md);
          font-weight: 600;
          cursor: pointer;
          transition: all var(--transition-fast);
        }

        .btn-end:hover {
          background: rgba(239, 68, 68, 0.2);
        }
      `}</style>
    </div>
  );
}
