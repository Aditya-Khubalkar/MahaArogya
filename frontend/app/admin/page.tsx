"use client";

import { useEffect, useState } from "react";
import { getAdminOverview } from "@/lib/api";
import StatCard from "@/components/StatCard";

export default function AdminPage() {
  const [overview, setOverview] = useState<any>(null);

  useEffect(() => {
    getAdminOverview().then(setOverview).catch(console.error);
  }, []);

  const occupancyPercent = overview ? Math.round((overview.occupied_beds / overview.total_beds) * 100) : 0;

  return (
    <div className="animate-in">
      <div className="page-header">
        <h1>Admin Overview</h1>
        <p>Hospital management and occupancy metrics</p>
      </div>

      <div className="stats-grid" style={{ marginBottom: "24px" }}>
        <StatCard 
          icon="🛏️" 
          label="Total Beds" 
          value={overview?.total_beds || 0} 
          subtitle="Capacity" 
          color="var(--accent)" 
        />
        <StatCard 
          icon="📊" 
          label="Occupancy Rate" 
          value={`${occupancyPercent}%`} 
          subtitle={`${overview?.occupied_beds || 0} occupied`} 
          color={occupancyPercent > 80 ? "var(--urgent)" : "var(--routine)"} 
        />
        <StatCard 
          icon="🚨" 
          label="ICU Occupancy" 
          value={`${overview?.icu_occupied || 0}/${overview?.icu_total || 0}`} 
          subtitle="Critical care" 
          color="var(--emergency)" 
        />
        <StatCard 
          icon="⏱️" 
          label="Avg Wait Time" 
          value={`${overview?.avg_wait_time_min || 0} min`} 
          subtitle="Across departments" 
          color="var(--priority)" 
        />
      </div>

      <div className="glass-card">
        <h3 style={{ marginBottom: "16px" }}>Occupancy Gauge</h3>
        <div style={{ height: "24px", width: "100%", backgroundColor: "var(--bg-tertiary)", borderRadius: "12px", overflow: "hidden" }}>
          <div style={{ 
            height: "100%", 
            width: `${occupancyPercent}%`, 
            backgroundColor: occupancyPercent > 80 ? "var(--urgent)" : "var(--routine)",
            transition: "width 1s ease"
          }} />
        </div>
        <p style={{ marginTop: "8px", fontSize: "0.85rem", color: "var(--text-muted)", textAlign: "right" }}>
          {occupancyPercent}% capacity reached
        </p>
      </div>
    </div>
  );
}
