"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Overview" },
  { href: "/risk", label: "Risk Analysis" },
  { href: "/data-quality", label: "Data Quality" },
  { href: "/facilities", label: "Health System" },
  { href: "/metadata", label: "Metadata" },
  { href: "/map", label: "Map" },
];

export function Nav() {
  const pathname = usePathname();

  return (
    <header className="border-b border-brand-800/20 bg-brand-900 text-white shadow-lg">
      <div className="mx-auto flex max-w-[1400px] flex-col gap-4 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <div>
          <Link href="/" className="text-xl font-semibold tracking-tight">
            EnviroLens
          </Link>
          <p className="mt-0.5 text-sm text-brand-200">
            Verdania air pollution &amp; respiratory health intelligence
          </p>
        </div>
        <nav className="flex flex-wrap gap-1">
          {links.map(({ href, label }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                  active
                    ? "bg-brand-700 text-white"
                    : "text-brand-100 hover:bg-brand-800 hover:text-white"
                }`}
              >
                {label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
