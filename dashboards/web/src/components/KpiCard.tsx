interface KpiCardProps {
  label: string;
  value: string | number;
  hint?: string;
  accent?: "default" | "warning" | "success";
}

const accents = {
  default: "border-l-brand-500",
  warning: "border-l-orange-500",
  success: "border-l-emerald-500",
};

export function KpiCard({ label, value, hint, accent = "default" }: KpiCardProps) {
  return (
    <article
      className={`rounded-lg border border-slate-200 bg-white p-5 shadow-sm border-l-4 ${accents[accent]}`}
    >
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-slate-900">{value}</p>
      {hint && <p className="mt-1 text-xs text-slate-400">{hint}</p>}
    </article>
  );
}
