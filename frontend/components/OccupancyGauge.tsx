"use client";

interface OccupancyGaugeProps {
  percentage: number;
  label: string;
  size?: number;
}

export default function OccupancyGauge({ percentage, label, size = 160 }: OccupancyGaugeProps) {
  const strokeWidth = 10;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;

  const getColor = (pct: number) => {
    if (pct >= 90) return "var(--emergency)";
    if (pct >= 75) return "var(--urgent)";
    if (pct >= 50) return "var(--priority)";
    return "var(--primary)";
  };

  const color = getColor(percentage);

  return (
    <div className="gauge-wrapper">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--bg-tertiary)"
          strokeWidth={strokeWidth}
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="gauge-progress"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
        {/* Glow filter */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          opacity={0.3}
          filter="blur(4px)"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </svg>
      <div className="gauge-center">
        <span className="gauge-value" style={{ color }}>{percentage}%</span>
        <span className="gauge-label">{label}</span>
      </div>

      <style jsx>{`
        .gauge-wrapper {
          position: relative;
          display: inline-flex;
          align-items: center;
          justify-content: center;
        }
        .gauge-progress {
          transition: stroke-dashoffset 1s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .gauge-center {
          position: absolute;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 2px;
        }
        .gauge-value {
          font-size: 1.75rem;
          font-weight: 800;
          letter-spacing: -0.03em;
        }
        .gauge-label {
          font-size: 0.7rem;
          color: var(--text-muted);
          font-weight: 500;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }
      `}</style>
    </div>
  );
}
