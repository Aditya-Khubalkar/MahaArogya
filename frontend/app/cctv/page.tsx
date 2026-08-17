"use client";

import { useState, useRef, useEffect } from "react";
import OccupancyGauge from "@/components/OccupancyGauge";
import LoadingSpinner from "@/components/LoadingSpinner";
import { estimateCCTV, type CCTVOccupancyResult } from "@/lib/api";

export default function CCTVPage() {
  const [cameraId, setCameraId] = useState("CAM-ICU-04");
  const [wardId, setWardId] = useState("ICU Ward A");
  const [detectedBeds, setDetectedBeds] = useState(14);
  const [totalBeds, setTotalBeds] = useState(16);
  const [dbOccupied, setDbOccupied] = useState(10);
  const [confidence, setConfidence] = useState(0.92);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [latestResult, setLatestResult] = useState<CCTVOccupancyResult | null>(null);
  const [results, setResults] = useState<CCTVOccupancyResult[]>([]);
  const [simulatedBeds, setSimulatedBeds] = useState([
    { id: 1, occupied: true, conf: 0.94 },
    { id: 2, occupied: true, conf: 0.91 },
    { id: 3, occupied: true, conf: 0.96 },
    { id: 4, occupied: false, conf: 0.89 },
    { id: 5, occupied: true, conf: 0.93 },
    { id: 6, occupied: true, conf: 0.95 },
    { id: 7, occupied: true, conf: 0.88 },
    { id: 8, occupied: true, conf: 0.92 },
    { id: 9, occupied: true, conf: 0.90 },
    { id: 10, occupied: true, conf: 0.97 },
    { id: 11, occupied: true, conf: 0.85 },
    { id: 12, occupied: true, conf: 0.91 },
    { id: 13, occupied: true, conf: 0.93 },
    { id: 14, occupied: true, conf: 0.94 },
    { id: 15, occupied: false, conf: 0.92 },
    { id: 16, occupied: false, conf: 0.90 },
  ]);

  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Render CCTV bounding box simulation
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animId: number;
    let scanlineY = 0;

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Dark ward background simulation
      ctx.fillStyle = "#090d16";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Grid lines
      ctx.strokeStyle = "rgba(56, 189, 248, 0.08)";
      ctx.lineWidth = 1;
      for (let x = 0; x < canvas.width; x += 40) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
        ctx.stroke();
      }
      for (let y = 0; y < canvas.height; y += 40) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
      }

      // Draw 16 bed bounding boxes (4x4 grid)
      const cols = 4;
      const rows = 4;
      const padX = 24;
      const padY = 24;
      const boxW = (canvas.width - padX * (cols + 1)) / cols;
      const boxH = (canvas.height - padY * (rows + 1)) / rows;

      simulatedBeds.forEach((bed, idx) => {
        const c = idx % cols;
        const r = Math.floor(idx / cols);
        const bx = padX + c * (boxW + padX);
        const by = padY + r * (boxH + padY);

        // Discrepancy highlighted if bed index >= dbOccupied and is occupied
        const isDiscrepant = bed.occupied && idx >= dbOccupied;

        ctx.strokeStyle = isDiscrepant ? "#ef4444" : bed.occupied ? "#38bdf8" : "#22c55e";
        ctx.lineWidth = isDiscrepant ? 2.5 : 1.5;
        ctx.fillStyle = isDiscrepant
          ? "rgba(239, 68, 68, 0.18)"
          : bed.occupied
          ? "rgba(56, 189, 248, 0.12)"
          : "rgba(34, 197, 94, 0.08)";

        ctx.fillRect(bx, by, boxW, boxH);
        ctx.strokeRect(bx, by, boxW, boxH);

        // Bed Label & Confidence Tag
        ctx.fillStyle = isDiscrepant ? "#fca5a5" : bed.occupied ? "#bae6fd" : "#86efac";
        ctx.font = "10px sans-serif";
        ctx.fillText(`BED ${bed.id} [${bed.occupied ? "OCCUPIED" : "VACANT"}]`, bx + 6, by + 16);
        ctx.fillText(`${(bed.conf * 100).toFixed(0)}% CONF`, bx + 6, by + 30);
      });

      // Animated Scanline
      scanlineY = (scanlineY + 1.2) % canvas.height;
      ctx.strokeStyle = "rgba(14, 165, 233, 0.25)";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(0, scanlineY);
      ctx.lineTo(canvas.width, scanlineY);
      ctx.stroke();

      // Top HUD Overlay
      ctx.fillStyle = "#38bdf8";
      ctx.font = "bold 11px monospace";
      ctx.fillText(`● LIVE FEED [${cameraId}] - ${wardId}`, 12, 18);
      ctx.fillText(`FPS: 30.0 | RES: 1080p | EDGE CV: YOLOv8-CLINICAL`, canvas.width - 320, 18);

      animId = requestAnimationFrame(render);
    };

    render();

    return () => cancelAnimationFrame(animId);
  }, [simulatedBeds, dbOccupied, cameraId, wardId]);

  const handleEstimate = async () => {
    setError(null);
    setLoading(true);
    try {
      const res = await estimateCCTV({
        camera_id: cameraId,
        ward_id: wardId,
        detected_occupied_beds: detectedBeds,
        total_beds: totalBeds,
        db_authoritative_occupied: dbOccupied,
        confidence,
      });
      setLatestResult(res);
      setResults((prev) => [res, ...prev]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to run estimation");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header animate-in">
        <h1>CCTV Ward Bed Occupancy & CV Telemetry</h1>
        <p>Computer-vision discrepancy detection between CCTV live video feeds and authoritative HMS database</p>
      </div>

      {/* CCTV Live Canvas Feed Overlay */}
      <div className="glass-card animate-in animate-in-delay-1" style={{ marginBottom: 24 }}>
        <div className="cctv-header">
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span className="live-pulse" />
            <h3 style={{ margin: 0 }}>Active CCTV Stream: {cameraId} ({wardId})</h3>
          </div>
          <span className="badge badge-info">16 Detected Bed RoIs</span>
        </div>
        <div className="canvas-wrapper">
          <canvas ref={canvasRef} width={760} height={280} className="cctv-canvas" />
        </div>
        <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: 8 }}>
          🟢 Green = Verified Vacant | 🔵 Blue = Verified Occupied | 🔴 Red = Discrepancy (CV detects patient but HMS records bed as vacant)
        </p>
      </div>

      <div className="content-grid">
        {/* Controls */}
        <div className="glass-card animate-in animate-in-delay-2">
          <h3 style={{ marginBottom: 20 }}>Simulation Parameters</h3>

          <div className="form-grid">
            <div className="form-group">
              <label className="form-label">Camera ID</label>
              <input className="input-field" value={cameraId} onChange={(e) => setCameraId(e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">Ward ID</label>
              <input className="input-field" value={wardId} onChange={(e) => setWardId(e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">CV Detected Occupied Beds</label>
              <input className="input-field" type="number" min={0} max={totalBeds} value={detectedBeds} onChange={(e) => setDetectedBeds(Number(e.target.value))} />
            </div>
            <div className="form-group">
              <label className="form-label">Total Ward Beds</label>
              <input className="input-field" type="number" min={1} value={totalBeds} onChange={(e) => setTotalBeds(Number(e.target.value))} />
            </div>
            <div className="form-group">
              <label className="form-label">HMS Database Authoritative Occupied</label>
              <input className="input-field" type="number" min={0} max={totalBeds} value={dbOccupied} onChange={(e) => setDbOccupied(Number(e.target.value))} />
            </div>
            <div className="form-group">
              <label className="form-label">Detection Confidence</label>
              <input className="input-field" type="number" step="0.01" min={0} max={1} value={confidence} onChange={(e) => setConfidence(Number(e.target.value))} />
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
            onClick={handleEstimate}
            disabled={loading}
          >
            {loading ? <LoadingSpinner size={18} /> : "🔍 Run Discrepancy Analysis"}
          </button>
        </div>

        {/* Results */}
        <div className="animate-in animate-in-delay-3">
          {latestResult ? (
            <div className="glass-card result-card">
              {latestResult.discrepancy_detected && (
                <div className="alert-banner">
                  <span>🚨 Discrepancy Detected ({latestResult.discrepancy_delta > 0 ? "+" : ""}{latestResult.discrepancy_delta} Beds)</span>
                  <span className="alert-sub">CV detected {latestResult.estimated_occupied_beds} occupied beds, but HMS database lists {latestResult.db_authoritative_occupied}. Human verification required.</span>
                </div>
              )}

              <div className="gauge-section">
                <OccupancyGauge percentage={latestResult.occupancy_percentage} label="CV Estimated Occupancy" />
              </div>

              <div className="result-stats">
                <div className="result-stat">
                  <span className="stat-label-sm">DB Authoritative</span>
                  <span className="stat-value-sm">{latestResult.db_authoritative_occupied} / {latestResult.total_beds}</span>
                </div>
                <div className="result-stat">
                  <span className="stat-label-sm">Confidence</span>
                  <span className="stat-value-sm">{(latestResult.confidence_score * 100).toFixed(0)}%</span>
                </div>
                <div className="result-stat">
                  <span className="stat-label-sm">Discrepancy</span>
                  <span className="stat-value-sm" style={{ color: latestResult.discrepancy_detected ? "var(--emergency)" : "var(--routine)" }}>
                    {latestResult.discrepancy_detected
                      ? `⚠️ ${latestResult.discrepancy_delta > 0 ? "+" : ""}${latestResult.discrepancy_delta}`
                      : "None"}
                  </span>
                </div>
              </div>

              <div className="comparison-section">
                <h4 style={{ marginBottom: 12 }}>DB vs CV Comparison</h4>
                <div className="comparison-bars">
                  <div className="comp-row">
                    <span className="comp-label">HMS Database</span>
                    <div className="comp-track">
                      <div className="comp-fill comp-db" style={{ width: `${(latestResult.db_authoritative_occupied / latestResult.total_beds) * 100}%` }} />
                    </div>
                    <span className="comp-val">{latestResult.db_authoritative_occupied}</span>
                  </div>
                  <div className="comp-row">
                    <span className="comp-label">CV Camera Feed</span>
                    <div className="comp-track">
                      <div className="comp-fill comp-cv" style={{ width: `${(latestResult.estimated_occupied_beds / latestResult.total_beds) * 100}%` }} />
                    </div>
                    <span className="comp-val">{latestResult.estimated_occupied_beds}</span>
                  </div>
                </div>
              </div>

              <div className="result-timestamp">
                Last updated: {new Date(latestResult.timestamp).toLocaleString()}
              </div>
            </div>
          ) : (
            <div className="glass-card empty-state">
              <div className="empty-state-icon">📹</div>
              <p>No analysis run yet.</p>
              <p style={{ fontSize: "0.8rem", marginTop: 4 }}>Configure telemetry inputs and click Run Discrepancy Analysis.</p>
            </div>
          )}
        </div>
      </div>

      <style jsx>{`
        .cctv-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }
        .live-pulse {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          background: #ef4444;
          animation: pulse 1s infinite;
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
        .canvas-wrapper {
          background: #020617;
          border-radius: var(--radius-md);
          overflow: hidden;
          border: 1px solid rgba(56, 189, 248, 0.2);
        }
        .cctv-canvas {
          width: 100%;
          height: 280px;
          display: block;
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
        .error-banner {
          background: var(--emergency-dim);
          color: var(--emergency);
          padding: 10px 14px;
          border-radius: var(--radius-md);
          font-size: 0.8rem;
        }
        .result-card { position: relative; overflow: hidden; }
        .alert-banner {
          background: var(--emergency-dim);
          border: 1px solid rgba(239, 68, 68, 0.3);
          border-radius: var(--radius-md);
          padding: 12px 16px;
          margin-bottom: 20px;
          display: flex;
          flex-direction: column;
          gap: 4px;
          color: var(--emergency);
          font-weight: 600;
          font-size: 0.9rem;
        }
        .alert-sub {
          font-size: 0.8rem;
          font-weight: 400;
          opacity: 0.8;
        }
        .gauge-section {
          display: flex;
          justify-content: center;
          padding: 20px 0;
        }
        .result-stats {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 12px;
          margin-bottom: 20px;
        }
        .result-stat {
          display: flex;
          flex-direction: column;
          gap: 4px;
          padding: 10px;
          background: var(--bg-secondary);
          border-radius: var(--radius-md);
        }
        .stat-label-sm {
          font-size: 0.7rem;
          font-weight: 500;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.04em;
        }
        .stat-value-sm {
          font-size: 0.9rem;
          font-weight: 600;
          color: var(--text-primary);
        }
        .comparison-section {
          padding-top: 16px;
          border-top: 1px solid var(--surface-border);
          margin-bottom: 16px;
        }
        .comparison-section h4 {
          font-size: 0.85rem;
          color: var(--text-secondary);
        }
        .comparison-bars {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .comp-row {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        .comp-label {
          font-size: 0.75rem;
          color: var(--text-muted);
          width: 110px;
          flex-shrink: 0;
        }
        .comp-track {
          flex: 1;
          height: 10px;
          background: var(--bg-tertiary);
          border-radius: var(--radius-full);
          overflow: hidden;
        }
        .comp-fill {
          height: 100%;
          border-radius: var(--radius-full);
          transition: width 0.8s ease;
        }
        .comp-db { background: var(--primary); }
        .comp-cv { background: var(--accent); }
        .comp-val {
          font-size: 0.85rem;
          font-weight: 600;
          color: var(--text-primary);
          width: 30px;
          text-align: right;
        }
        .result-timestamp {
          font-size: 0.7rem;
          color: var(--text-muted);
          text-align: right;
        }
        @media (max-width: 768px) {
          .form-grid { grid-template-columns: 1fr; }
          .result-stats { grid-template-columns: repeat(2, 1fr); }
        }
      `}</style>
    </div>
  );
}
