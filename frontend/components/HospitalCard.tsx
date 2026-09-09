"use client";

interface HospitalCardProps {
  hospital: {
    id: string;
    name: string;
    beds_available: number;
    distance_km?: number;
    is_recommended?: boolean;
    queue_length?: number;
  };
  onClick?: () => void;
}

export default function HospitalCard({ hospital, onClick }: HospitalCardProps) {
  return (
    <div className={`hospital-card ${hospital.is_recommended ? 'recommended' : ''}`} onClick={onClick}>
      {hospital.is_recommended && (
        <div className="badge">⭐ Recommended</div>
      )}
      <div className="card-header">
        <h3 className="hospital-name">{hospital.name}</h3>
        {hospital.distance_km !== undefined && (
          <span className="distance">{hospital.distance_km.toFixed(1)} km</span>
        )}
      </div>
      
      <div className="card-stats">
        <div className="stat">
          <span className="stat-value text-primary">{hospital.beds_available}</span>
          <span className="stat-label">Beds Available</span>
        </div>
        {hospital.queue_length !== undefined && (
          <div className="stat">
            <span className="stat-value text-warning">{hospital.queue_length}</span>
            <span className="stat-label">Wait Queue</span>
          </div>
        )}
      </div>

      <style jsx>{`
        .hospital-card {
          background: var(--surface-light);
          border: 1px solid var(--surface-border);
          border-radius: var(--radius-lg);
          padding: 16px;
          cursor: pointer;
          transition: all var(--transition-fast);
          position: relative;
          overflow: hidden;
        }

        .hospital-card:hover {
          border-color: var(--primary);
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }

        .hospital-card.recommended {
          border-color: var(--primary);
          background: linear-gradient(145deg, var(--surface-light), rgba(16, 185, 129, 0.05));
        }

        .badge {
          position: absolute;
          top: 0;
          right: 0;
          background: var(--primary);
          color: white;
          font-size: 0.7rem;
          padding: 4px 12px;
          border-bottom-left-radius: var(--radius-md);
          font-weight: 600;
        }

        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 12px;
          margin-top: 4px;
        }

        .hospital-name {
          margin: 0;
          font-size: 1.1rem;
          color: var(--text-primary);
          font-weight: 600;
        }

        .distance {
          font-size: 0.85rem;
          color: var(--text-secondary);
          background: rgba(255, 255, 255, 0.1);
          padding: 2px 6px;
          border-radius: 4px;
        }

        .card-stats {
          display: flex;
          gap: 16px;
        }

        .stat {
          display: flex;
          flex-direction: column;
        }

        .stat-value {
          font-size: 1.25rem;
          font-weight: 700;
        }
        
        .text-primary { color: var(--primary); }
        .text-warning { color: #f59e0b; }

        .stat-label {
          font-size: 0.75rem;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }
      `}</style>
    </div>
  );
}
