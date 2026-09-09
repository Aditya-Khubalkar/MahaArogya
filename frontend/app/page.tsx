"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import StatCard from "@/components/StatCard";
import TriageBadge from "@/components/TriageBadge";
import { checkHealth, type HealthStatus, getDashboardStats } from "@/lib/api";
import { useRole } from "@/lib/roles";

interface ActivityItem {
  id: string;
  type: string;
  message: string;
  time: string;
  badge: string;
}

export default function DashboardPage() {
  const { role } = useRole();
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    checkHealth().then(setHealth).catch(() => setHealth(null));
    getDashboardStats().then(setStats).catch(console.error);
  }, []);

  const activities: ActivityItem[] = stats?.recent_activity || [];
  const triageBreakdown = stats?.triage_distribution || [
    { category: "ROUTINE", count: 0, pct: 0, color: "var(--routine)" },
    { category: "PRIORITY", count: 0, pct: 0, color: "var(--priority)" },
    { category: "URGENT", count: 0, pct: 0, color: "var(--urgent)" },
    { category: "EMERGENCY", count: 0, pct: 0, color: "var(--emergency)" },
  ];

  return (
    <div>
      <div className="page-header animate-in">
        <h1>Dashboard</h1>
        <p>MahaArogya AI Subsystem — Real-time overview</p>
      </div>

      {/* Stats Row */}
      <div className="stats-grid">
        <div className="animate-in animate-in-delay-1">
          <StatCard
            icon="💚"
            label="System Status"
            value={health ? "Online" : "Checking..."}
            subtitle={health?.gpu_detected ?? ""}
            color="var(--primary)"
            pulse={!!health}
          />
        </div>
        <div className="animate-in animate-in-delay-2">
          <StatCard icon="💬" label="Active Sessions" value={stats?.active_sessions || 0} subtitle="Conversations today" color="var(--accent)" />
        </div>
        <div className="animate-in animate-in-delay-3">
          <StatCard icon="🎫" label="OPD Tokens Issued" value={stats?.opd_tokens_issued || 0} subtitle="Today" color="var(--priority)" />
        </div>
        <div className="animate-in animate-in-delay-4">
          <StatCard icon="⚡" label="Avg Latency" value={stats?.avg_latency || "0.0s"} subtitle="Per conversation turn" color="var(--urgent)" />
        </div>
      </div>

      <div className="content-grid">
        {/* Triage Distribution */}
        <div className="glass-card animate-in animate-in-delay-2">
          <h3 style={{ marginBottom: 20 }}>Triage Distribution</h3>
          <div className="triage-bars">
            {triageBreakdown.map((item: any) => (
              <div key={item.category} className="triage-row">
                <div className="triage-row-header">
                  <TriageBadge category={item.category} />
                  <span className="triage-count">{item.count} patients</span>
                </div>
                <div className="triage-bar-track">
                  <div
                    className="triage-bar-fill"
                    style={{ width: `${item.pct}%`, background: item.color }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="glass-card animate-in animate-in-delay-3">
          <h3 style={{ marginBottom: 20 }}>Recent Activity</h3>
          <div className="activity-list">
            {activities.map((a) => (
              <div key={a.id} className="activity-item">
                <div className="activity-dot" />
                <div className="activity-content">
                  <p className="activity-message">{a.message}</p>
                  <div className="activity-meta">
                    <TriageBadge category={a.badge} size="sm" />
                    <span className="activity-time">{a.time}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions animate-in animate-in-delay-4">
        <h3 style={{ marginBottom: 16, marginTop: 32 }}>Quick Actions</h3>
        <div className="action-grid">
          {[
            { href: "/conversation", icon: "💬", label: "Start Conversation", desc: "Begin patient intake", roles: ["public"] },
            { href: "/opd", icon: "🎫", label: "Issue OPD Token", desc: "Generate appointment token", roles: ["public"] },
            { href: "/reception", icon: "🏥", label: "Patient Check-in", desc: "Reception desk workflow", roles: ["reception", "hospital_admin"] },
            { href: "/live-queue", icon: "⏱️", label: "Live Queue", desc: "View waiting list", roles: ["public", "reception", "nurse", "doctor", "hospital_admin"] },
            { href: "/hospitals", icon: "🗺️", label: "Hospital Finder", desc: "Find nearest hospital", roles: ["public", "reception"] },
            { href: "/cctv", icon: "📹", label: "CCTV Monitor", desc: "Ward bed occupancy", roles: ["hospital_admin", "hospital_head", "district_officer", "government"] },
            { href: "/nurse-ward", icon: "🛏️", label: "Nurse Ward", desc: "Patient monitoring", roles: ["nurse", "hospital_admin", "doctor"] },
            { href: "/doctor-queue", icon: "👨‍⚕️", label: "Doctor Queue", desc: "Consultation workflow", roles: ["doctor", "hospital_admin"] },
          ].filter(action => action.roles.includes(role)).map((action) => (
            <Link key={action.href} href={action.href} className="action-card glass-card glass-card-interactive">
              <span className="action-icon">{action.icon}</span>
              <span className="action-label">{action.label}</span>
              <span className="action-desc">{action.desc}</span>
            </Link>
          ))}
        </div>
      </div>

      <style jsx>{`
        .triage-bars {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        .triage-row-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 6px;
        }
        .triage-count {
          font-size: 0.8rem;
          color: var(--text-secondary);
        }
        .triage-bar-track {
          height: 8px;
          background: var(--bg-tertiary);
          border-radius: var(--radius-full);
          overflow: hidden;
        }
        .triage-bar-fill {
          height: 100%;
          border-radius: var(--radius-full);
          transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .activity-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
          max-height: 340px;
          overflow-y: auto;
          padding-right: 4px;
        }
        .activity-item {
          display: flex;
          gap: 12px;
          align-items: flex-start;
        }
        .activity-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: var(--text-muted);
          margin-top: 6px;
          flex-shrink: 0;
        }
        .activity-content { flex: 1; min-width: 0; }
        .activity-message {
          font-size: 0.85rem;
          color: var(--text-primary);
          margin-bottom: 6px;
          line-height: 1.4;
        }
        .activity-meta {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .activity-time {
          font-size: 0.7rem;
          color: var(--text-muted);
        }

        .action-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: var(--space-md);
        }
        .action-grid :global(.action-card) {
          display: flex;
          flex-direction: column;
          align-items: center;
          text-align: center;
          gap: 8px;
          padding: 24px 16px;
          text-decoration: none;
          cursor: pointer;
        }
        .action-grid :global(.action-card:hover) {
          text-decoration: none;
        }
        :global(.action-icon) {
          font-size: 2rem;
        }
        :global(.action-label) {
          font-size: 0.9rem;
          font-weight: 600;
          color: var(--text-primary);
        }
        :global(.action-desc) {
          font-size: 0.75rem;
          color: var(--text-muted);
        }

        @media (max-width: 768px) {
          .action-grid { grid-template-columns: repeat(2, 1fr); }
        }
      `}</style>
    </div>
  );
}
