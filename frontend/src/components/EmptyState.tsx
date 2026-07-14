import type { ReactNode } from "react";

interface EmptyStateProps {
  title: string;
  description: string;
  action?: ReactNode;
}

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className="empty-state px-6 py-12 text-center">
      <p className="font-mono text-[11px] uppercase tracking-[0.12em] text-slate-400">No data</p>
      <h3 className="mt-4 text-xl font-semibold tracking-tight text-slate-100">{title}</h3>
      <p className="mx-auto mt-3 max-w-lg text-sm leading-6 text-slate-400">{description}</p>
      {action ? <div className="mt-6 flex justify-center">{action}</div> : null}
    </div>
  );
}
