export function LoadingState({ label = "Loading data" }: { label?: string }) {
  return (
    <div className="loading-state px-6 py-14 text-center">
      <div className="mx-auto h-9 w-9 animate-spin rounded-full border-2 border-slate-700 border-t-[var(--accent)]" />
      <p className="mt-4 font-mono text-[11px] uppercase tracking-[0.12em] text-slate-400">{label}</p>
      <div className="mx-auto mt-5 h-1 w-36 overflow-hidden rounded-full bg-white/[0.05]">
        <div className="h-full w-1/2 animate-pulse rounded-full bg-[var(--accent)]/60" />
      </div>
    </div>
  );
}
