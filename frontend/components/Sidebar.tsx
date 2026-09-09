"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { checkHealth } from "@/lib/api";

import RoleSwitcher from "@/components/RoleSwitcher";

import { useRole } from "@/lib/roles";

const allNavItems = [
  { href: "/", label: "Dashboard", icon: "📊", roles: ["public", "reception", "nurse", "doctor", "hospital_admin", "hospital_head", "district_officer", "government"] },
  { href: "/conversation", label: "Conversation", icon: "💬", roles: ["public"] },
  { href: "/hospitals", label: "Hospital Finder", icon: "🗺️", roles: ["public", "reception"] },
  { href: "/opd", label: "OPD Tokens", icon: "🎫", roles: ["public"] },
  { href: "/reception", label: "Reception", icon: "🏥", roles: ["reception", "hospital_admin"] },
  { href: "/live-queue", label: "Live Queue", icon: "⏱️", roles: ["public", "reception", "nurse", "doctor", "hospital_admin"] },
  { href: "/nurse-ward", label: "Nurse Ward", icon: "🛏️", roles: ["nurse", "hospital_admin", "doctor"] },
  { href: "/doctor-queue", label: "Doctor Queue", icon: "👨‍⚕️", roles: ["doctor", "hospital_admin"] },
  { href: "/cctv", label: "CCTV Monitor", icon: "📹", roles: ["hospital_admin", "hospital_head", "district_officer", "government"] },
  { href: "/admin", label: "Admin Overview", icon: "🏢", roles: ["hospital_admin", "hospital_head"] },
  { href: "/government", label: "State Overview", icon: "🏛️", roles: ["district_officer", "government"] },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [healthy, setHealthy] = useState<boolean | null>(null);
  const { role } = useRole();

  useEffect(() => {
    let mounted = true;
    const ping = async () => {
      try {
        await checkHealth();
        if (mounted) setHealthy(true);
      } catch {
        if (mounted) setHealthy(false);
      }
    };
    ping();
    const iv = setInterval(ping, 15000);
    return () => { mounted = false; clearInterval(iv); };
  }, []);

  const navItems = allNavItems.filter((item) => item.roles.includes(role));

  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="sidebar-brand">
        <div className="brand-icon">🏥</div>
        <div className="brand-text">
          <span className="brand-name">MahaArogya</span>
          <span className="brand-sub">Sanjeevani Grid</span>
        </div>
      </div>

      <div style={{ marginTop: '20px' }}>
        <RoleSwitcher />
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`nav-item ${pathname === item.href ? "nav-item-active" : ""}`}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </Link>
        ))}
      </nav>

      {/* Health Indicator */}
      <div className="sidebar-footer">
        <div className="health-indicator">
          <div className={`health-dot ${healthy === true ? "healthy" : healthy === false ? "unhealthy" : "checking"}`} />
          <span className="health-text">
            {healthy === true ? "Backend Online" : healthy === false ? "Backend Offline" : "Checking..."}
          </span>
        </div>
        <div className="version-text">v1.0.0 · AI Subsystem</div>
      </div>

      <style jsx>{`
        .sidebar {
          position: fixed;
          top: 0;
          left: 0;
          bottom: 0;
          width: var(--sidebar-width);
          background: rgba(10, 15, 30, 0.95);
          backdrop-filter: blur(20px);
          border-right: 1px solid var(--surface-border);
          display: flex;
          flex-direction: column;
          z-index: 100;
          overflow-y: auto;
        }

        .sidebar-brand {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 24px 20px;
          border-bottom: 1px solid var(--surface-border);
        }

        .brand-icon {
          font-size: 1.75rem;
          width: 44px;
          height: 44px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: var(--primary-dim);
          border-radius: var(--radius-lg);
        }

        .brand-text {
          display: flex;
          flex-direction: column;
        }

        .brand-name {
          font-size: 1.1rem;
          font-weight: 700;
          color: var(--text-primary);
          letter-spacing: -0.02em;
        }

        .brand-sub {
          font-size: 0.7rem;
          color: var(--primary);
          font-weight: 500;
          letter-spacing: 0.05em;
          text-transform: uppercase;
        }

        .sidebar-nav {
          flex: 1;
          padding: 12px 10px;
          display: flex;
          flex-direction: column;
          gap: 2px;
        }

        .sidebar-nav :global(.nav-item) {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 11px 14px;
          border-radius: var(--radius-md);
          color: var(--text-secondary);
          font-size: 0.9rem;
          font-weight: 500;
          text-decoration: none;
          transition: all var(--transition-fast);
        }

        .sidebar-nav :global(.nav-item:hover) {
          color: var(--text-primary);
          background: rgba(148, 163, 184, 0.08);
          text-decoration: none;
        }

        .sidebar-nav :global(.nav-item-active) {
          color: var(--primary);
          background: var(--primary-dim);
        }

        .sidebar-nav :global(.nav-item-active:hover) {
          background: var(--primary-dim);
        }

        .nav-icon {
          font-size: 1.15rem;
          width: 28px;
          text-align: center;
        }

        .sidebar-footer {
          padding: 16px 20px;
          border-top: 1px solid var(--surface-border);
        }

        .health-indicator {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 8px;
        }

        .health-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          flex-shrink: 0;
        }

        .health-dot.healthy {
          background: var(--primary);
          animation: pulse-glow 2s ease-in-out infinite;
        }

        .health-dot.unhealthy {
          background: var(--emergency);
        }

        .health-dot.checking {
          background: var(--text-muted);
          animation: pulse-glow 1s ease-in-out infinite;
        }

        .health-text {
          font-size: 0.8rem;
          color: var(--text-secondary);
        }

        .version-text {
          font-size: 0.7rem;
          color: var(--text-muted);
        }

        @media (max-width: 768px) {
          .sidebar {
            transform: translateX(-100%);
          }
        }
      `}</style>
    </aside>
  );
}
