"use client";

import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { useEffect } from "react";

// Fix leaflet icon issue in Next.js
const icon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

export default function MapComponent({ hospitals }: { hospitals: any[] }) {
  useEffect(() => {
    // Leaflet needs this to reset the map size sometimes
    setTimeout(() => {
      window.dispatchEvent(new Event("resize"));
    }, 200);
  }, []);

  return (
    <MapContainer center={[19.0760, 72.8777]} zoom={11} style={{ height: "500px", width: "100%", borderRadius: "8px" }}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {hospitals.map((h, i) => (
        <Marker key={i} position={[h.latitude, h.longitude]} icon={icon}>
          <Popup>
            <strong>{h.name}</strong><br />
            {h.city}<br />
            Load: {h.current_load_percent}%
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
