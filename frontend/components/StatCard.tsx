"use client";

interface StatCardProps {
  icon: string;
  label: string;
  value: string | number;
  subtitle?: string;
  color?: string;
  pulse?: boolean;
}

export default function StatCard({ icon, label, value, subtitle, color = "var(--primary)", pulse }: StatCardProps) {
  return (
    <div className="stat-card glass-card">
      <div className="stat-icon" style={{ background: `${color}20`, color }}>
        {icon}
      </div>
      <div className="stat-body">
        <span className="stat-label">{label}</span>
        <span className="stat-value" style={{ color }}>{value}</span>
        {subtitle && <span className="stat-subtitle">{subtitle}</span>}
      </div>
      {pulse && <div className="stat-pulse" style={{ background: color }} />}

      <style jsx>{`
        .stat-card {
          display: flex;
          align-items: center;
          gap: 16px;
          position: relative;
          overflow: hidden;
        }
        .stat-icon {
          width: 48px;
          height: 48px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: var(--radius-lg);
          font-size: 1.4rem;
          flex-shrink: 0;
        }
        .stat-body {
          display: flex;
          flex-direction: column;
          min-width: 0;
        }
        .stat-label {
          font-size: 0.75rem;
          color: var(--text-muted);
          font-weight: 500;
          text-transform: uppercase;
          letter-spacing: 0.04em;
        }
        .stat-value {
          font-size: 1.5rem;
          font-weight: 700;
          letter-spacing: -0.02em;
          line-height: 1.2;
        }
        .stat-subtitle {
          font-size: 0.75rem;
          color: var(--text-secondary);
          margin-top: 2px;
        }
        .stat-pulse {
          position: absolute;
          top: 12px;
          right: 12px;
          width: 8px;
          height: 8px;
          border-radius: 50%;
          animation: pulse-glow 2s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}
