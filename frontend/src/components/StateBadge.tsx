const stateToneMap: Record<string, string> = {
  open: "border-sky-400/20 bg-sky-500/10 text-sky-300",
  closed: "border-slate-400/20 bg-slate-500/10 text-slate-300",
  merged: "border-emerald-400/20 bg-emerald-500/10 text-emerald-300",
};

export function StateBadge({ state }: { state: string }) {
  const tone = stateToneMap[state] || stateToneMap.closed;

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 font-mono text-[11px] uppercase tracking-[0.08em] ${tone}`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current opacity-80" aria-hidden="true" />
      {state}
    </span>
  );
}
