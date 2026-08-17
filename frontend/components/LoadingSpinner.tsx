"use client";

export default function LoadingSpinner({ size = 32, text }: { size?: number; text?: string }) {
  return (
    <div className="spinner-wrapper">
      <div className="spinner" style={{ width: size, height: size }}>
        <div className="spinner-ring" />
      </div>
      {text && <span className="spinner-text">{text}</span>}

      <style jsx>{`
        .spinner-wrapper {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 12px;
        }
        .spinner {
          position: relative;
        }
        .spinner-ring {
          width: 100%;
          height: 100%;
          border: 3px solid var(--bg-tertiary);
          border-top-color: var(--primary);
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }
        .spinner-text {
          font-size: 0.8rem;
          color: var(--text-muted);
          font-weight: 500;
        }
      `}</style>
    </div>
  );
}
