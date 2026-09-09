"use client";
import { createContext, useContext, useState, ReactNode } from "react";

export type Role = "public" | "reception" | "nurse" | "doctor" | "hospital_admin" | "hospital_head" | "district_officer" | "government";

export const AVAILABLE_ROLES = [
  { id: "public", title: "Public User" },
  { id: "reception", title: "Reception" },
  { id: "nurse", title: "Nurse" },
  { id: "doctor", title: "Doctor" },
  { id: "hospital_admin", title: "Hospital Admin" },
  { id: "hospital_head", title: "Hospital Head" },
  { id: "district_officer", title: "District Officer" },
  { id: "government", title: "Government Official" },
];

interface RoleContextType {
  role: Role;
  setRole: (role: Role) => void;
}

const RoleContext = createContext<RoleContextType | undefined>(undefined);

export function RoleProvider({ children }: { children: ReactNode }) {
  const [role, setRole] = useState<Role>("public");

  return (
    <RoleContext.Provider value={{ role, setRole }}>
      {children}
    </RoleContext.Provider>
  );
}

export function useRole() {
  const context = useContext(RoleContext);
  if (context === undefined) {
    throw new Error("useRole must be used within a RoleProvider");
  }
  return context;
}
