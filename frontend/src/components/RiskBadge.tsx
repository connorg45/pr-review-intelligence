import type { RiskLevel } from "../types";

const toneMap: Record<string, string> = {
  low: "bg-emerald-500/12 text-emerald-300 border-emerald-400/20",
  medium: "bg-amber-500/12 text-amber-300 border-amber-400/20",
  high: "bg-rose-500/12 text-rose-300 border-rose-400/20",
  unknown: "bg-slate-500/10 text-slate-300 border-slate-400/20",
};

export function RiskBadge({ level }: { level: RiskLevel | null | "unknown" }) {
  const resolved = level ?? "unknown";
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.08em] ${toneMap[resolved]}`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current opacity-80" aria-hidden="true" />
      {resolved}
    </span>
  );
}
