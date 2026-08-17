export function InsightGrid({
  insights,
}: {
  insights: { eyebrow: string; title: string; detail: string }[];
}) {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {insights.map((item) => (
        <article
          key={item.title}
          className="relative overflow-hidden rounded-xl border border-emerald-900/10 bg-gradient-to-br from-white to-emerald-50/60 p-5 shadow-sm"
        >
          <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-brand-700">
            {item.eyebrow}
          </p>
          <h3 className="mt-1.5 text-base font-semibold leading-snug text-slate-900">{item.title}</h3>
          <p className="mt-2 text-sm leading-relaxed text-slate-600">{item.detail}</p>
        </article>
      ))}
    </div>
  );
}
