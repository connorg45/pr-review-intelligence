import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { fetchEvents } from "../api";
import { EmptyState } from "../components/EmptyState";
import { LoadingState } from "../components/LoadingState";
import { PageHeader } from "../components/PageHeader";
import { SectionCard } from "../components/SectionCard";
import type { EventItem } from "../types";
import { formatDateTime, formatEventType } from "../utils/format";
import { pullRequestQueueUrl } from "../utils/routes";

function ActivityRow({ event }: { event: EventItem }) {
  const destination = event.pull_request_id
    ? `/pull-requests/${event.pull_request_id}`
    : event.repository_name
      ? pullRequestQueueUrl({ search: event.repository_name })
      : null;

  const content = (
    <>
      <div>
        <p aria-hidden="true" className="mb-1 text-[10px] uppercase tracking-[0.1em] text-slate-400 xl:hidden">Type</p>
        <span className="sr-only">Type: </span>
        <p className="inline font-mono text-[11px] uppercase tracking-[0.1em] text-slate-400">{formatEventType(event.event_type)}</p>
      </div>
      <div className="min-w-0">
        <p aria-hidden="true" className="mb-1 text-[10px] uppercase tracking-[0.1em] text-slate-400 xl:hidden">Repository</p>
        <span className="sr-only">Repository: </span>
        <p className="inline truncate font-mono text-xs text-slate-400">{event.repository_name || "System"}</p>
      </div>
      <div>
        <p aria-hidden="true" className="mb-1 text-[10px] uppercase tracking-[0.1em] text-slate-400 xl:hidden">PR</p>
        <span className="sr-only">Pull request: </span>
        <p className="inline font-mono text-xs text-slate-400">{event.pull_request_number ? `#${event.pull_request_number}` : "—"}</p>
      </div>
      <div className="col-span-2 xl:col-span-1">
        <p aria-hidden="true" className="mb-1 text-[10px] uppercase tracking-[0.1em] text-slate-400 xl:hidden">Message</p>
        <span className="sr-only">Message: </span>
        <p className="text-sm leading-6 text-slate-200">{event.message}</p>
      </div>
      <div className="relative col-span-2 pr-8 xl:col-span-1 xl:pr-5">
        <p aria-hidden="true" className="mb-1 text-[10px] uppercase tracking-[0.1em] text-slate-400 xl:hidden">Time</p>
        <span className="sr-only">Time: </span>
        <p className="inline text-xs text-slate-400">{formatDateTime(event.created_at)}</p>
        {destination ? <span aria-hidden="true" className="absolute right-0 top-1/2 -translate-y-1/2 text-slate-700 transition group-hover:translate-x-0.5 group-hover:text-slate-200">→</span> : null}
      </div>
    </>
  );

  const rowClass = "grid grid-cols-2 gap-4 px-4 py-4 text-sm text-slate-300 xl:grid-cols-[minmax(8rem,0.65fr)_minmax(9rem,0.8fr)_minmax(4rem,0.35fr)_minmax(16rem,1.8fr)_minmax(8rem,0.65fr)] xl:items-center";

  return destination ? (
    <Link to={destination} className={`${rowClass} data-row-link group`}>
      {content}
    </Link>
  ) : (
    <div className={rowClass}>{content}</div>
  );
}

export function ActivityPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["events"],
    queryFn: () => fetchEvents(120),
  });

  return (
    <div className="page-stack space-y-8">
      <PageHeader
        title="Activity and Events"
        description="Review repository syncs, failures, risk updates, and recent changes in one audit log."
      />

      <SectionCard title="Event Log" eyebrow="Recent system activity" variant="surface">
        {isLoading ? <LoadingState label="Loading activity" /> : null}
        {isError ? <EmptyState title="Could not load events" description="We couldn't load the activity log. Try again in a moment." /> : null}
        {!isLoading && !isError && data && data.length === 0 ? (
          <EmptyState
            title="No events recorded"
            description="Repository sync and risk updates will appear here."
            action={
              <Link to="/settings" className="btn btn-secondary">
                Open sync settings <span aria-hidden="true" className="ml-2">→</span>
              </Link>
            }
          />
        ) : null}
        {!isLoading && !isError && data && data.length > 0 ? (
          <div className="data-shell">
            <div aria-hidden="true" className="hidden grid-cols-[minmax(8rem,0.65fr)_minmax(9rem,0.8fr)_minmax(4rem,0.35fr)_minmax(16rem,1.8fr)_minmax(8rem,0.65fr)] gap-4 bg-white/[0.025] px-4 py-3 text-xs uppercase tracking-[0.1em] text-slate-400 xl:grid">
              <span>Type</span>
              <span>Repository</span>
              <span>PR</span>
              <span>Message</span>
              <span>Time</span>
            </div>
            <ul className="divide-y divide-white/5" aria-label="Recent activity">
              {data.map((event) => (
                <li key={event.id}><ActivityRow event={event} /></li>
              ))}
            </ul>
          </div>
        ) : null}
      </SectionCard>
    </div>
  );
}
