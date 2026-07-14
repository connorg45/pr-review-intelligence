import { Link } from "react-router-dom";

interface StatCardProps {
  label: string;
  value: string;
  detail: string;
  to?: string;
  tone?: "default" | "high";
}

export function StatCard({ label, value, detail, to, tone = "default" }: StatCardProps) {
  const content = (
    <>
      <div className="flex items-center justify-between gap-4">
        <p className="metric-label">{label}</p>
        {to ? (
          <span aria-hidden="true" className="metric-arrow">→</span>
        ) : (
          <span className="h-1.5 w-1.5 rounded-full bg-slate-500" aria-hidden="true" />
        )}
      </div>
      <div className="mt-4">
        <p className={`metric-value ${tone === "high" ? "metric-value--high" : ""}`}>{value}</p>
        <p className="mt-2 max-w-[15rem] text-sm leading-5 text-slate-400">{detail}</p>
      </div>
    </>
  );

  if (to) {
    return (
      <Link to={to} className="metric-cell group block">
        {content}
      </Link>
    );
  }

  return (
    <section className="metric-cell metric-cell--static">
      {content}
    </section>
  );
}
