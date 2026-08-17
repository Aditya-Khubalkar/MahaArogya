"use client";

interface TriageBadgeProps {
  category: string;
  size?: "sm" | "md" | "lg";
}

const TRIAGE_MAP: Record<string, { className: string; label: string }> = {
  EMERGENCY: { className: "badge-emergency", label: "Emergency" },
  URGENT: { className: "badge-urgent", label: "Urgent" },
  PRIORITY: { className: "badge-priority", label: "Priority" },
  ROUTINE: { className: "badge-routine", label: "Routine" },
};

export default function TriageBadge({ category, size = "sm" }: TriageBadgeProps) {
  const info = TRIAGE_MAP[category] ?? { className: "badge-neutral", label: category };
  const fontSize = size === "lg" ? "0.9rem" : size === "md" ? "0.8rem" : "0.75rem";
  const padding = size === "lg" ? "6px 14px" : size === "md" ? "5px 12px" : "4px 10px";

  return (
    <span className={`badge ${info.className}`} style={{ fontSize, padding }}>
      ● {info.label}
    </span>
  );
}
