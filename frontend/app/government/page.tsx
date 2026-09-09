"use client";

import { useEffect, useState } from "react";
import { getGovtOverview } from "@/lib/api";
import StatCard from "@/components/StatCard";

export default function GovernmentPage() {
  const [overview, setOverview] = useState<any>(null);

  useEffect(() => {
    getGovtOverview().then(setOverview).catch(console.error);
  }, []);

  return (
    <div className="animate-in">
      <div className="page-header">
        <h1>Government State Overview</h1>
        <p>State-level healthcare metrics and alerts</p>
      </div>

      <div className="stats-grid" style={{ marginBottom: "24px" }}>
        <StatCard 
          icon="🏥" 
          label="Total Hospitals" 
          value={overview?.total_hospitals || 0} 
          subtitle="Active in network" 
          color="var(--accent)" 
        />
        <StatCard 
          icon="🚨" 
          label="Active Emergencies" 
          value={overview?.active_emergencies || 0} 
          subtitle="Requires attention" 
          color="var(--emergency)" 
          pulse={overview?.active_emergencies > 0}
        />
        <StatCard 
          icon="👥" 
          label="Total Patients" 
          value={overview?.total_patients_today?.toLocaleString() || 0} 
          subtitle="Served today" 
          color="var(--primary)" 
        />
        <StatCard 
          icon="📦" 
          label="Supply Alerts" 
          value={overview?.critical_supplies_alerts || 0} 
          subtitle="Critical shortages" 
          color="var(--urgent)" 
        />
      </div>

      <div className="glass-card" style={{ padding: "24px", textAlign: "center" }}>
        <h3 style={{ marginBottom: "16px" }}>State Average Occupancy Rate</h3>
        <div style={{ 
          fontSize: "3rem", 
          fontWeight: "bold", 
          color: (overview?.avg_occupancy_rate || 0) > 80 ? "var(--urgent)" : "var(--routine)" 
        }}>
          {overview?.avg_occupancy_rate || 0}%
        </div>
        <p style={{ color: "var(--text-muted)", marginTop: "8px" }}>
          Aggregated across all connected facilities
        </p>
      </div>
    </div>
  );
}
