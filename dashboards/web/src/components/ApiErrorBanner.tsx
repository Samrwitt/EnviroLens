interface ApiErrorBannerProps {
  message: string;
}

export function ApiErrorBanner({ message }: ApiErrorBannerProps) {
  return (
    <div
      role="alert"
      className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800"
    >
      <strong className="font-semibold">API unavailable.</strong> {message}
      <p className="mt-1 text-red-600">
        Ensure PostGIS and FastAPI are running, then start the backend with{" "}
        <code className="rounded bg-red-100 px-1">uvicorn api.main:app --reload</code>.
      </p>
    </div>
  );
}
