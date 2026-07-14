import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { fetchDashboard } from "../api";
import { EmptyState } from "../components/EmptyState";
import { LoadingState } from "../components/LoadingState";
import { PageHeader } from "../components/PageHeader";
import { RiskBadge } from "../components/RiskBadge";
import { SectionCard } from "../components/SectionCard";
import { StatCard } from "../components/StatCard";
import type { RiskLevel } from "../types";
import { formatDateTime, formatEventType, formatRelativeScore, formatSourceType } from "../utils/format";
import { pullRequestQueueUrl } from "../utils/routes";

const riskBarTone: Record<RiskLevel, string> = {
  low: "bg-emerald-400",
  medium: "bg-amber-400",
  high: "bg-rose-400",
};

export function DashboardPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["dashboard"],
    queryFn: fetchDashboard,
  });

  if (isLoading) {
    return <LoadingState label="Loading dashboard" />;
  }

  if (isError || !data) {
    return <EmptyState title="Dashboard unavailable" description="We couldn't load the review dashboard. Try again in a moment." />;
  }

  const maxRiskCount = Math.max(...data.risk_distribution.map((item) => item.count), 1);
  const maxTrendScore = Math.max(...data.trend.map((item) => item.avg_risk_score), 1);

  return (
    <div className="page-stack space-y-8">
      <PageHeader
        title="Review Radar"
        description="Track risky pull requests, reviewer workload, and repository activity in one place."
        actions={
          <>
            <Link
              to="/pull-requests"
              className="btn btn-primary"
            >
              Review PR Queue
            </Link>
            <Link
              to="/settings"
              className="btn btn-secondary"
            >
              Sync & Data Settings
            </Link>
          </>
        }
      />

      <div className="metric-strip grid gap-px sm:grid-cols-2 xl:grid-cols-5">
        <StatCard label="Total PRs" value={String(data.summary.total_prs)} detail="Across all tracked repositories." to={pullRequestQueueUrl()} />
        <StatCard label="Open PRs" value={String(data.summary.open_prs)} detail="Current review workload that still needs attention." to={pullRequestQueueUrl({ state: "open" })} />
        <StatCard label="High Risk" value={String(data.summary.high_risk_prs)} detail="Pull requests with the highest review risk." to={pullRequestQueueUrl({ risk: "high" })} tone="high" />
        <StatCard label="Average Risk" value={formatRelativeScore(data.summary.avg_risk_score)} detail="Overall risk across tracked pull requests." to={pullRequestQueueUrl({ sort: "risk_score", order: "desc" })} />
        <StatCard
          label="Time To First Review"
          value={data.summary.avg_time_to_first_review_hours !== null ? `${data.summary.avg_time_to_first_review_hours}h` : "N/A"}
          detail="Average time between PR creation and first recorded review."
        />
      </div>

      <div className="grid gap-6 2xl:grid-cols-[1.65fr_1fr]">
        <SectionCard title="High-Risk Pull Requests" eyebrow="Immediate attention" variant="surface">
          {data.high_risk_prs.length === 0 ? (
            <EmptyState
              title="No high-risk pull requests"
              description="Sync a repository or load sample data to review the latest changes."
              action={
                <Link to="/settings" className="btn btn-secondary">
                  Open data settings <span aria-hidden="true" className="ml-2">→</span>
                </Link>
              }
            />
          ) : (
            <div className="data-shell">
              <div aria-hidden="true" className="hidden grid-cols-[minmax(0,1.7fr)_minmax(9rem,0.8fr)_minmax(8rem,0.65fr)_minmax(8rem,0.7fr)_auto] gap-4 bg-white/[0.025] px-4 py-3 text-xs uppercase tracking-[0.1em] text-slate-400 min-[1380px]:grid">
                <span>PR</span>
                <span>Repository</span>
                <span>Risk</span>
                <span>Updated</span>
                <span>Action</span>
              </div>
              <ul className="divide-y divide-white/5" aria-label="High-risk pull requests">
                {data.high_risk_prs.map((pullRequest) => (
                  <li key={pullRequest.id}>
                    <Link
                      to={`/pull-requests/${pullRequest.id}`}
                      className="data-row-link group grid grid-cols-2 items-center gap-4 px-4 py-4 text-sm text-slate-300 min-[1380px]:grid-cols-[minmax(0,1.7fr)_minmax(9rem,0.8fr)_minmax(8rem,0.65fr)_minmax(8rem,0.7fr)_auto]"
                    >
                      <div className="col-span-2 min-w-0 min-[1380px]:col-span-1">
                        <p className="font-mono text-xs text-slate-500">#{pullRequest.github_pr_number}</p>
                        <p className="mt-1 truncate font-medium text-slate-100">{pullRequest.title}</p>
                        <p className="mt-1 text-xs text-slate-400">{pullRequest.author}</p>
                      </div>
                      <div>
                        <p aria-hidden="true" className="mb-1 text-[10px] uppercase tracking-[0.1em] text-slate-400 min-[1380px]:hidden">Repository</p>
                        <span className="sr-only">Repository: </span>
                        <p className="inline truncate font-mono text-xs text-slate-400">{pullRequest.repository_name}</p>
                      </div>
                      <div>
                        <p aria-hidden="true" className="mb-1 text-[10px] uppercase tracking-[0.1em] text-slate-400 min-[1380px]:hidden">Risk</p>
                        <span className="sr-only">Risk: </span>
                        <div className="inline-flex flex-wrap items-center gap-2">
                          <RiskBadge level={pullRequest.risk_level} />
                          <span className="font-mono text-xs text-slate-400">{formatRelativeScore(pullRequest.risk_score)}</span>
                        </div>
                      </div>
                      <div>
                        <p aria-hidden="true" className="mb-1 text-[10px] uppercase tracking-[0.1em] text-slate-400 min-[1380px]:hidden">Updated</p>
                        <span className="sr-only">Updated: </span>
                        <p className="inline text-xs text-slate-400">{formatDateTime(pullRequest.updated_at)}</p>
                      </div>
                      <span className="justify-self-end text-lg text-slate-500 transition group-hover:translate-x-1 group-hover:text-[var(--accent)]" aria-hidden="true">→</span>
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </SectionCard>

        <div className="space-y-5">
          <SectionCard title="Risk Distribution" eyebrow="Current mix">
            <div className="space-y-4">
              {data.risk_distribution.map((item) => (
                <Link key={item.level} to={pullRequestQueueUrl({ risk: item.level })} className="group -mx-2 block rounded-xl px-2 py-2 transition hover:bg-white/[0.03]">
                  <div className="mb-2 flex items-center justify-between text-sm text-slate-300">
                    <div className="flex items-center gap-3">
                      <RiskBadge level={item.level} />
                      <span className="capitalize">{item.level} risk</span>
                    </div>
                    <span className="font-mono text-xs text-slate-500 transition group-hover:text-slate-300">{item.count} PRs →</span>
                  </div>
                  <div className="h-1.5 rounded-full bg-white/[0.05]">
                    <div
                      className={`h-1.5 rounded-full ${riskBarTone[item.level]} transition group-hover:brightness-110`}
                      style={{ width: `${(item.count / maxRiskCount) * 100}%` }}
                    />
                  </div>
                </Link>
              ))}
            </div>
          </SectionCard>

          <SectionCard title="Seven-Day Risk Trend" eyebrow="Daily average">
            <div className="risk-trend-grid flex h-48 items-end gap-3 rounded-xl px-2 pt-2">
              {data.trend.length === 0 ? (
                <p className="text-sm text-slate-400">Not enough history yet.</p>
              ) : (
                data.trend.map((item, index) => (
                  <div key={item.date} className="flex h-full flex-1 flex-col items-center gap-3">
                    <div className="flex min-h-0 w-full flex-1 items-end">
                      <div
                        className="chart-bar risk-trend-bar w-full"
                        style={{ height: `${Math.max((item.avg_risk_score / maxTrendScore) * 100, 18)}%`, animationDelay: `${index * 45}ms` }}
                        title={`${item.date}: average risk ${item.avg_risk_score}`}
                      />
                    </div>
                    <div className="text-center">
                      <p className="font-mono text-[11px] text-slate-500">{item.date.slice(5)}</p>
                      <p className="text-xs text-slate-300">{item.avg_risk_score}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </SectionCard>
        </div>
      </div>

      <div className="grid gap-6 2xl:grid-cols-[1.15fr_1fr]">
        <SectionCard title="Repository Overview" eyebrow="Repo health">
          {data.repositories.length === 0 ? (
            <EmptyState
              title="No repositories yet"
              description="Connect a repository or load sample data to begin."
              action={
                <Link to="/settings" className="btn btn-secondary">
                  Add a repository <span aria-hidden="true" className="ml-2">→</span>
                </Link>
              }
            />
          ) : (
            <div className="divide-y divide-white/5">
              {data.repositories.map((repository) => (
                <Link key={repository.id} to={pullRequestQueueUrl({ search: repository.full_name })} className="subtle-link-row group -mx-2 block rounded-xl px-2 py-4">
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div>
                      <p className="font-mono text-xs uppercase tracking-[0.1em] text-slate-400">{formatSourceType(repository.source_type)}</p>
                      <h3 className="mt-2 text-lg font-semibold text-slate-100">{repository.full_name}</h3>
                    </div>
                    <span className="font-mono text-[11px] text-slate-500 transition group-hover:text-[var(--accent)]">
                      {repository.stats.total_prs} PRs →
                    </span>
                  </div>
                  <div className="mt-4 grid grid-cols-3 gap-3 border-t border-white/5 pt-3 text-sm">
                    <div>
                      <p className="text-slate-500">Open</p>
                      <p className="mt-1 font-semibold text-slate-50">{repository.stats.open_prs}</p>
                    </div>
                    <div>
                      <p className="text-slate-500">High Risk</p>
                      <p className="mt-1 font-semibold text-slate-50">{repository.stats.high_risk_prs}</p>
                    </div>
                    <div>
                      <p className="text-slate-500">Avg Risk</p>
                      <p className="mt-1 font-semibold text-slate-50">{formatRelativeScore(repository.stats.average_risk_score)}</p>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </SectionCard>

        <SectionCard title="Recent Activity" eyebrow="Audit trail" actions={<Link className="text-link" to="/activity">View all →</Link>}>
          {data.recent_events.length === 0 ? (
            <EmptyState
              title="No recent events"
              description="Repository sync and risk updates will appear here."
              action={
                <Link to="/settings" className="btn btn-secondary">
                  Open sync settings <span aria-hidden="true" className="ml-2">→</span>
                </Link>
              }
            />
          ) : (
            <div className="divide-y divide-white/5">
              {data.recent_events.map((event) => {
                const destination = event.pull_request_id
                  ? `/pull-requests/${event.pull_request_id}`
                  : event.repository_name
                    ? pullRequestQueueUrl({ search: event.repository_name })
                    : null;
                const content = (
                  <>
                    <div className="flex items-center justify-between gap-4">
                      <p className="font-mono text-[11px] uppercase tracking-[0.1em] text-slate-400">{formatEventType(event.event_type)}</p>
                      <p className="text-xs text-slate-500">{formatDateTime(event.created_at)}</p>
                    </div>
                    <p className="mt-3 text-sm leading-6 text-slate-200">{event.message}</p>
                    <div className="mt-2 flex items-center justify-between gap-3">
                      <p className="font-mono text-xs text-slate-500">{event.repository_name || "System"}</p>
                      {destination ? <span aria-hidden="true" className="text-sm text-slate-600 transition group-hover:translate-x-0.5 group-hover:text-slate-200">Open →</span> : null}
                    </div>
                  </>
                );

                return destination ? (
                  <Link key={event.id} to={destination} className="subtle-link-row group -mx-2 block rounded-xl px-2 py-4">
                    {content}
                  </Link>
                ) : (
                  <div key={event.id} className="py-4">
                    {content}
                  </div>
                );
              })}
            </div>
          )}
        </SectionCard>
      </div>
    </div>
  );
}
