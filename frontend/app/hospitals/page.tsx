"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { getHospitals } from "@/lib/api";

const MapComponent = dynamic(() => import("@/components/MapComponent"), { ssr: false });

export default function HospitalsPage() {
  const [hospitals, setHospitals] = useState<any[]>([]);

  useEffect(() => {
    getHospitals().then(setHospitals).catch(console.error);
  }, []);

  return (
    <div className="animate-in">
      <div className="page-header">
        <h1>Hospital Finder</h1>
        <p>Interactive map of healthcare facilities</p>
      </div>
      <div className="glass-card" style={{ padding: "16px" }}>
        <MapComponent hospitals={hospitals} />
      </div>
    </div>
  );
}
