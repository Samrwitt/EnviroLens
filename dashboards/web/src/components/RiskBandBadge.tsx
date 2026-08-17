import { riskBandColor, riskBandLabel } from "@/lib/utils";

export function RiskBandBadge({ band }: { band: string }) {
  return (
    <span
      className={`inline-flex rounded-full border px-2.5 py-0.5 text-xs font-medium capitalize ${riskBandColor(band)}`}
    >
      {riskBandLabel(band)}
    </span>
  );
}
