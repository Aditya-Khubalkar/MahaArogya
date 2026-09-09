"use client";

import { useRole, AVAILABLE_ROLES } from "@/lib/roles";

export default function RoleSwitcher() {
  const { role, setRole } = useRole();

  return (
    <div className="role-switcher">
      <select
        value={role}
        onChange={(e) => setRole(e.target.value as any)}
        className="role-select"
      >
        {AVAILABLE_ROLES.map((r) => (
          <option key={r.id} value={r.id}>
            {r.title}
          </option>
        ))}
      </select>

      <style jsx>{`
        .role-switcher {
          margin-bottom: 20px;
          padding: 0 20px;
        }

        .role-select {
          width: 100%;
          padding: 8px 12px;
          border-radius: 8px;
          background: rgba(30, 41, 59, 0.8);
          border: 1px solid var(--surface-border);
          color: var(--text-primary);
          font-size: 0.85rem;
          cursor: pointer;
          outline: none;
        }
        
        .role-select:focus {
          border-color: var(--primary);
        }
      `}</style>
    </div>
  );
}
