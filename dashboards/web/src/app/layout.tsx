import type { Metadata } from "next";
import { Nav } from "@/components/Nav";
import "./globals.css";

export const metadata: Metadata = {
  title: "EnviroLens",
  description: "Environmental health data and risk intelligence — Verdania MVP",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased">
        <Nav />
        <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6">{children}</main>
        <footer className="border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-500">
          EnviroLens — synthetic aggregate data only. Risk scores support public-health planning,
          not clinical diagnosis.
        </footer>
      </body>
    </html>
  );
}
