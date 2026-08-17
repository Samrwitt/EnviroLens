import { ApiErrorBanner } from "@/components/ApiErrorBanner";
import { PageHeader } from "@/components/PageHeader";
import { WeightExplorer } from "@/components/WeightExplorer";
import { api, ApiError } from "@/lib/api";

export default async function ExplorerPage() {
  try {
    const data = await api.dashboard();
    return (
      <div>
        <PageHeader
          title="Weight laboratory"
          description="AP-EHRI v1.0 is a documented weighted sum. Change the policy emphasis — more weight on poverty, less on proximity — and watch community ranks move. This is a scenario tool; published scores in PostgreSQL stay on methodology 1.0."
        />
        <WeightExplorer
          communities={data.explorer ?? []}
          defaultWeights={data.default_weights ?? {}}
        />
      </div>
    );
  } catch (err) {
    const msg = err instanceof ApiError ? err.message : "Could not load explorer data.";
    return (
      <div>
        <PageHeader title="Weight laboratory" description="Interactive AP-EHRI scenario testing." />
        <ApiErrorBanner message={msg} />
      </div>
    );
  }
}
