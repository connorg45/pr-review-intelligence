import type { ReactNode } from "react";

interface PageHeaderProps {
  title: string;
  description: string;
  actions?: ReactNode;
}

export function PageHeader({ title, description, actions }: PageHeaderProps) {
  return (
    <div className="page-header flex flex-col gap-5 pb-7 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p className="page-kicker">Review workspace</p>
        <h1 className="page-heading mt-2">{title}</h1>
        <p className="mt-3 max-w-3xl text-[15px] leading-6 text-slate-400">{description}</p>
      </div>
      {actions ? <div className="grid w-full gap-2 sm:flex sm:w-auto sm:flex-wrap">{actions}</div> : null}
    </div>
  );
}
