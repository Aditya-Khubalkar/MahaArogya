import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "@/components/Sidebar";

import { RoleProvider } from "@/lib/roles";

export const metadata: Metadata = {
  title: "MahaArogya — Sanjeevani Grid Dashboard",
  description: "AI-powered healthcare routing subsystem dashboard for Maharashtra's public health infrastructure.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <RoleProvider>
          <div className="app-layout">
            <Sidebar />
            <main className="main-content">
              {children}
            </main>
          </div>
        </RoleProvider>
      </body>
    </html>
  );
}
