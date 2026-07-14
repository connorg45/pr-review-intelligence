import type { ReactNode } from "react";

interface SectionCardProps {
  title: string;
  eyebrow?: string;
  actions?: ReactNode;
  children: ReactNode;
  variant?: "plain" | "surface";
  contentClassName?: string;
}

export function SectionCard({ title, eyebrow, actions, children, variant = "plain", contentClassName = "p-4 sm:p-5" }: SectionCardProps) {
  return (
    <section className={`section-surface ${variant === "surface" ? "section-surface--raised" : ""}`}>
      <div className="section-header flex items-center justify-between gap-4 px-1 py-4 sm:px-0">
        <div>
          {eyebrow ? <p className="section-eyebrow">{eyebrow}</p> : null}
          <h2 className="mt-1 text-[17px] font-semibold leading-6 tracking-tight text-slate-100">{title}</h2>
        </div>
        {actions}
      </div>
      <div className={contentClassName}>{children}</div>
    </section>
  );
}
