"use client";

interface Vitals {
  heartRate: number;
  bloodPressure: string;
  temperature: number;
  spo2: number;
}

interface VitalsDisplayProps {
  vitals: Vitals;
}

export default function VitalsDisplay({ vitals }: VitalsDisplayProps) {
  return (
    <div className="vitals-grid">
      <div className="vital-card">
        <span className="vital-icon">❤️</span>
        <div className="vital-info">
          <span className="vital-label">Heart Rate</span>
          <span className="vital-value">{vitals.heartRate} <span className="vital-unit">bpm</span></span>
        </div>
      </div>
      
      <div className="vital-card">
        <span className="vital-icon">🩸</span>
        <div className="vital-info">
          <span className="vital-label">Blood Pressure</span>
          <span className="vital-value">{vitals.bloodPressure} <span className="vital-unit">mmHg</span></span>
        </div>
      </div>
      
      <div className="vital-card">
        <span className="vital-icon">🌡️</span>
        <div className="vital-info">
          <span className="vital-label">Temperature</span>
          <span className="vital-value">{vitals.temperature}°<span className="vital-unit">F</span></span>
        </div>
      </div>
      
      <div className="vital-card">
        <span className="vital-icon">🫁</span>
        <div className="vital-info">
          <span className="vital-label">SpO2</span>
          <span className="vital-value">{vitals.spo2}<span className="vital-unit">%</span></span>
        </div>
      </div>

      <style jsx>{`
        .vitals-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
          gap: 16px;
        }

        .vital-card {
          background: rgba(30, 41, 59, 0.5);
          border: 1px solid var(--surface-border);
          border-radius: var(--radius-md);
          padding: 12px;
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .vital-icon {
          font-size: 1.5rem;
          background: rgba(255, 255, 255, 0.05);
          width: 40px;
          height: 40px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .vital-info {
          display: flex;
          flex-direction: column;
        }

        .vital-label {
          font-size: 0.75rem;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .vital-value {
          font-size: 1.1rem;
          font-weight: 700;
          color: var(--text-primary);
        }

        .vital-unit {
          font-size: 0.75rem;
          color: var(--text-secondary);
          font-weight: normal;
        }
      `}</style>
    </div>
  );
}
