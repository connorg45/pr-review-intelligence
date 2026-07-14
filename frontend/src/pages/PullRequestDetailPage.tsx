import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { Link, useParams } from "react-router-dom";
import { analyzePullRequest, fetchConfig, fetchPullRequest } from "../api";
import { EmptyState } from "../components/EmptyState";
import { LoadingState } from "../components/LoadingState";
import { PageHeader } from "../components/PageHeader";
import { RiskBadge } from "../components/RiskBadge";
import { SectionCard } from "../components/SectionCard";
import { StateBadge } from "../components/StateBadge";
import { formatCompactNumber, formatDateTime, formatEventType, formatLabel, formatRelativeScore, formatState } from "../utils/format";
import { pullRequestQueueUrl } from "../utils/routes";

function MetaBlock({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="meta-block">
      <p className="font-mono text-[11px] uppercase tracking-[0.1em] text-slate-400">{label}</p>
      <p className="mt-2 text-sm text-slate-200">{value}</p>
    </div>
  );
}

export function PullRequestDetailPage() {
  const { id = "" } = useParams();
  const queryClient = useQueryClient();
  const { data, isLoading, isError } = useQuery({
    queryKey: ["pull-request", id],
    queryFn: () => fetchPullRequest(id),
    enabled: Boolean(id),
  });
  const { data: config } = useQuery({
    queryKey: ["config"],
    queryFn: fetchConfig,
  });

  const analyzeMutation = useMutation({
    mutationFn: () => analyzePullRequest(Number(id)),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["pull-request", id] }),
        queryClient.invalidateQueries({ queryKey: ["pull-requests"] }),
        queryClient.invalidateQueries({ queryKey: ["dashboard"] }),
        queryClient.invalidateQueries({ queryKey: ["events"] }),
      ]);
    },
  });

  if (isLoading) {
    return <LoadingState label="Loading pull request detail" />;
  }

  if (isError || !data) {
    return <EmptyState title="Pull request not found" description="The requested PR detail could not be loaded." />;
  }

  const displayState = formatState(data.state, data.merged_at);
  const topRecommendation = data.analysis_result?.reviewer_recommendations[0];
  const riskPercent = Math.max(0, Math.min(data.risk_score ?? 0, 100));
  const riskTone = data.risk_level ?? "unknown";

  return (
    <div className="page-stack space-y-8">
      <PageHeader
        title={data.title}
        description={`${data.repository_name || "Unknown repository"} · PR #${data.github_pr_number} · Review risk, ownership, file scope, and score history.`}
        actions={
          <>
            {data.url ? (
              <a
                href={data.url}
                target="_blank"
                rel="noreferrer"
                className="btn btn-secondary"
              >
                Open on GitHub
              </a>
            ) : null}
            <button
              onClick={() => analyzeMutation.mutate()}
              disabled={!config?.app.write_operations_enabled || analyzeMutation.isPending}
              title={!config?.app.write_operations_enabled ? "This public deployment is read-only." : undefined}
              className="btn btn-primary"
            >
              {!config?.app.write_operations_enabled
                ? "Read-only demo"
                : analyzeMutation.isPending
                  ? "Checking risk..."
                  : "Refresh risk score"}
            </button>
          </>
        }
      />

      <section className="detail-overview">
        <div className="grid gap-6 2xl:grid-cols-[1.3fr_0.7fr]">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <Link
                to={pullRequestQueueUrl({ search: data.repository_name || "" })}
                className="rounded-full border border-white/10 px-3 py-1 font-mono text-[11px] uppercase tracking-[0.08em] text-slate-400 transition hover:border-[var(--accent)]/40 hover:text-slate-100"
              >
                {data.repository_name || "unknown-repository"}
                <span aria-hidden="true" className="ml-2">→</span>
              </Link>
              {data.url ? (
                <a
                  href={data.url}
                  target="_blank"
                  rel="noreferrer"
                  className="rounded-full border border-white/10 px-3 py-1 font-mono text-[11px] uppercase tracking-[0.08em] text-slate-400 transition hover:border-[var(--accent)]/40 hover:text-slate-100"
                >
                  PR #{data.github_pr_number} <span aria-hidden="true">↗</span>
                </a>
              ) : (
                <span className="font-mono text-[11px] uppercase tracking-[0.08em] text-slate-500">PR #{data.github_pr_number}</span>
              )}
              <StateBadge state={displayState} />
              <RiskBadge level={data.risk_level} />
            </div>
            <div className="mt-5 grid gap-px overflow-hidden rounded-xl border border-white/5 bg-white/[0.05] sm:grid-cols-2 xl:grid-cols-4">
              <MetaBlock label="Author" value={data.author} />
              <MetaBlock label="Created" value={formatDateTime(data.created_at)} />
              <MetaBlock label="Updated" value={formatDateTime(data.updated_at)} />
              <MetaBlock label="First review" value={formatDateTime(data.first_review_at)} />
            </div>
          </div>

          <div className={`risk-snapshot risk-${riskTone}`}>
            <p className="font-mono text-[11px] uppercase tracking-[0.1em] text-slate-400">Risk snapshot</p>
            <div className="mt-5 flex items-end justify-between gap-4">
              <div>
                <p className="font-mono text-4xl font-semibold text-slate-50">{formatRelativeScore(data.risk_score)}</p>
                <p className="mt-2 text-sm text-slate-400">Current risk score</p>
              </div>
              <RiskBadge level={data.risk_level} />
            </div>
            <div className="risk-meter mt-5" aria-label={`Risk score ${riskPercent} out of 100`} role="meter" aria-valuemin={0} aria-valuemax={100} aria-valuenow={riskPercent}>
              <div className={`risk-meter-fill risk-${riskTone}`} style={{ width: `${riskPercent}%` }} />
            </div>
            <div className="mt-6 grid gap-3 md:grid-cols-2">
              <MetaBlock label="Files changed" value={String(data.changed_files_count)} />
              <MetaBlock label="Total lines" value={formatCompactNumber(data.additions + data.deletions)} />
              <MetaBlock label="Score status" value={formatLabel(data.analysis_status)} />
              <MetaBlock label="Last synced" value={formatDateTime(data.last_synced_at)} />
            </div>
            {topRecommendation ? (
              <div className="mt-5 border-t border-white/5 pt-4">
                <p className="font-mono text-[11px] uppercase tracking-[0.1em] text-slate-400">Suggested reviewer</p>
                <div className="mt-3 flex items-center justify-between gap-4">
                  <p className="font-semibold text-slate-100">{topRecommendation.reviewer}</p>
                  <span className="rounded-full border border-white/10 px-3 py-1 font-mono text-[11px] text-slate-400">
                    match {topRecommendation.score}
                  </span>
                </div>
                <p className="mt-3 text-sm leading-6 text-slate-400">{topRecommendation.reasons[0]}</p>
              </div>
            ) : null}
          </div>
        </div>
      </section>

      <div className="grid gap-6 2xl:grid-cols-[1.1fr_0.9fr]">
        <SectionCard title="Why This Score" eyebrow="Risk factors">
          {data.analysis_result ? (
            <div className="divide-y divide-white/5">
              {data.analysis_result.reasons.map((reason, index) => (
                <div key={reason} className="risk-reason-row py-4">
                  <div className="flex items-start gap-4">
                    <span className="mt-0.5 flex h-7 w-7 items-center justify-center rounded-lg border border-white/10 font-mono text-[11px] text-[var(--accent)]">
                      {index + 1}
                    </span>
                    <p className="text-sm leading-6 text-slate-300">{reason}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState title="Risk score pending" description="This pull request has not been scored yet." />
          )}
        </SectionCard>

        <SectionCard title="Suggested Reviewers" eyebrow="Based on repository history">
          {data.analysis_result ? (
            <div className="divide-y divide-white/5">
              {data.analysis_result.reviewer_recommendations.map((reviewer) => (
                <div key={reviewer.reviewer} className="reviewer-row py-4">
                  <div className="flex items-center justify-between gap-4">
                    <p className="font-semibold text-slate-100">{reviewer.reviewer}</p>
                    <span className="rounded-full border border-white/10 px-3 py-1 font-mono text-[11px] text-slate-400">
                      match {reviewer.score}
                    </span>
                  </div>
                  <div className="mt-3 space-y-2">
                    {reviewer.reasons.map((reason) => (
                      <p key={reason} className="text-sm leading-6 text-slate-400">
                        {reason}
                      </p>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState title="No reviewer suggestions yet" description="Run the risk check to see reviewer suggestions." />
          )}
        </SectionCard>
      </div>

      <div className="grid gap-6 2xl:grid-cols-[1.25fr_0.75fr]">
        <SectionCard title="Changed Files" eyebrow="File-level scope" variant="surface">
          {data.files.length === 0 ? (
            <EmptyState title="No changed files stored" description="Run a fresh sync or reset sample data to restore file-level scope for this pull request." />
          ) : (
            <div className="data-shell overflow-x-auto">
              <table className="min-w-[34rem] text-left text-sm">
                <thead className="bg-white/[0.025] text-xs uppercase tracking-[0.1em] text-slate-400">
                  <tr>
                    <th className="px-4 py-3">Path</th>
                    <th className="px-4 py-3">Type</th>
                    <th className="px-4 py-3">Delta</th>
                  </tr>
                </thead>
                <tbody>
                  {data.files.map((file) => (
                    <tr key={file.id} className="border-t border-white/5 text-slate-300">
                      <td className="px-4 py-4">
                        {data.url ? (
                          <a
                            href={`${data.url.replace(/\/$/, "")}/files`}
                            target="_blank"
                            rel="noreferrer"
                            className="break-all font-mono text-xs leading-5 text-slate-300 underline decoration-slate-600 underline-offset-4 transition hover:text-slate-50"
                            aria-label={`Open ${file.path} in the GitHub pull request files view`}
                          >
                            {file.path} <span aria-hidden="true">↗</span>
                          </a>
                        ) : (
                          <p className="break-all font-mono text-xs leading-5 text-slate-300">{file.path}</p>
                        )}
                        <div className="mt-2 flex flex-wrap gap-2">
                          {file.is_sensitive ? (
                            <span className="rounded-full border border-rose-400/20 bg-rose-500/10 px-2.5 py-1 text-[10px] uppercase tracking-[0.08em] text-rose-300">
                              Sensitive
                            </span>
                          ) : null}
                          {file.is_test_file ? (
                            <span className="rounded-full border border-emerald-400/20 bg-emerald-500/10 px-2.5 py-1 text-[10px] uppercase tracking-[0.08em] text-emerald-300">
                              Test
                            </span>
                          ) : null}
                        </div>
                      </td>
                      <td className="px-4 py-4 text-xs uppercase tracking-[0.08em] text-slate-400">{file.change_type}</td>
                      <td className="px-4 py-4 font-mono text-xs text-slate-400">
                        +{file.additions} / -{file.deletions}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </SectionCard>

        <div className="space-y-5">
          <SectionCard title="PR Profile" eyebrow="Metadata snapshot">
            <div className="grid gap-3">
              <MetaBlock
                label="Repository"
                value={
                  <Link to={pullRequestQueueUrl({ search: data.repository_name || "" })} className="underline decoration-slate-600 underline-offset-4 transition hover:text-slate-50">
                    {data.repository_name || "Unknown repository"} <span aria-hidden="true">→</span>
                  </Link>
                }
              />
              <MetaBlock label="Merged at" value={formatDateTime(data.merged_at)} />
              <MetaBlock
                label="GitHub pull request"
                value={
                  data.url ? (
                    <a href={data.url} target="_blank" rel="noreferrer" className="underline decoration-slate-600 underline-offset-4 transition hover:text-slate-50">
                      Open on GitHub <span aria-hidden="true">↗</span>
                    </a>
                  ) : (
                    "Not available"
                  )
                }
              />
            </div>
          </SectionCard>

          <SectionCard title="Activity Timeline" eyebrow="Risk and sync events">
            {data.activity.length === 0 ? (
              <EmptyState title="No activity recorded" description="Risk and sync events for this PR will appear here after a sync or score refresh." />
            ) : (
              <div className="activity-timeline">
                {data.activity.map((event) => (
                  <div key={event.id} className="timeline-item py-3 pl-6">
                    <div className="flex items-center justify-between gap-4">
                      <p className="font-mono text-[11px] uppercase tracking-[0.1em] text-slate-400">{formatEventType(event.event_type)}</p>
                      <p className="text-xs text-slate-500">{formatDateTime(event.created_at)}</p>
                    </div>
                    <p className="mt-3 text-sm leading-6 text-slate-300">{event.message}</p>
                  </div>
                ))}
              </div>
            )}
          </SectionCard>
        </div>
      </div>

      <SectionCard title="Risk History" eyebrow="Previous scores">
        {data.analysis_history.length === 0 ? (
          <EmptyState title="No risk history yet" description="Refresh the risk score to store the first snapshot for this pull request." />
        ) : (
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {data.analysis_history.map((entry) => (
              <div key={entry.id} className="rounded-xl border border-white/5 bg-white/[0.02] p-4">
                <div className="flex items-center justify-between gap-4">
                  <RiskBadge level={entry.risk_level} />
                  <span className="font-mono text-xs text-slate-500">{formatRelativeScore(entry.risk_score)}</span>
                </div>
                <p className="mt-4 text-sm text-slate-300">Stored at {formatDateTime(entry.analyzed_at)}</p>
              </div>
            ))}
          </div>
        )}
      </SectionCard>

      <div className="pt-2">
        <Link to="/pull-requests" className="btn btn-secondary">
          <span aria-hidden="true" className="mr-2">←</span> Back to pull requests
        </Link>
      </div>
    </div>
  );
}
