import { useQuery } from "@tanstack/react-query";
import { useDeferredValue } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { fetchPullRequests } from "../api";
import { EmptyState } from "../components/EmptyState";
import { LoadingState } from "../components/LoadingState";
import { PageHeader } from "../components/PageHeader";
import { RiskBadge } from "../components/RiskBadge";
import { SectionCard } from "../components/SectionCard";
import { StateBadge } from "../components/StateBadge";
import { formatDateTime, formatLabel, formatRelativeScore, formatState } from "../utils/format";

function allowedParam(value: string | null, options: string[], fallback: string) {
  return value && options.includes(value) ? value : fallback;
}

export function PullRequestsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const state = allowedParam(searchParams.get("state"), ["all", "open", "closed"], "all");
  const risk = allowedParam(searchParams.get("risk"), ["all", "low", "medium", "high"], "all");
  const search = searchParams.get("search") || "";
  const sort = allowedParam(searchParams.get("sort"), ["updated_at", "risk_score", "created_at", "number"], "updated_at");
  const order = allowedParam(searchParams.get("order"), ["asc", "desc"], "desc");
  const deferredSearch = useDeferredValue(search);

  function updateFilter(key: string, value: string, defaultValue: string) {
    const next = new URLSearchParams(searchParams);
    if (!value || value === defaultValue) {
      next.delete(key);
    } else {
      next.set(key, value);
    }
    setSearchParams(next, { replace: true });
  }

  const { data, isLoading, isError } = useQuery({
    queryKey: ["pull-requests", state, risk, deferredSearch, sort, order],
    queryFn: () => fetchPullRequests({ state, risk, search: deferredSearch, sort, order }),
  });

  const hasFilters = state !== "all" || risk !== "all" || search.trim() !== "" || sort !== "updated_at" || order !== "desc";

  return (
    <div className="page-stack space-y-8">
      <PageHeader
        title="Pull Request Queue"
        description="Filter by status and risk, then open any pull request for the full review context."
      />

      <SectionCard title="Filters" eyebrow="Review queue controls" variant="surface">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-[1.6fr_repeat(4,minmax(0,1fr))]">
          <label className="text-sm text-slate-400">
            <span className="mb-2 block text-xs uppercase tracking-[0.1em] text-slate-400">Search</span>
            <input
              value={search}
              onChange={(event) => updateFilter("search", event.target.value, "")}
              placeholder="Title, author, repo, or #123"
              className="form-control"
            />
            <p className="mt-2 text-xs text-slate-500">Search matches PR title, author, repo name, and exact PR number.</p>
          </label>
          <label className="text-sm text-slate-400">
            <span className="mb-2 block text-xs uppercase tracking-[0.1em] text-slate-400">Status</span>
            <select value={state} onChange={(event) => updateFilter("state", event.target.value, "all")} className="form-control">
              <option value="all">All</option>
              <option value="open">Open</option>
              <option value="closed">Closed</option>
            </select>
          </label>
          <label className="text-sm text-slate-400">
            <span className="mb-2 block text-xs uppercase tracking-[0.1em] text-slate-400">Risk</span>
            <select value={risk} onChange={(event) => updateFilter("risk", event.target.value, "all")} className="form-control">
              <option value="all">All</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </label>
          <label className="text-sm text-slate-400">
            <span className="mb-2 block text-xs uppercase tracking-[0.1em] text-slate-400">Sort By</span>
            <select value={sort} onChange={(event) => updateFilter("sort", event.target.value, "updated_at")} className="form-control">
              <option value="updated_at">Updated</option>
              <option value="risk_score">Risk score</option>
              <option value="created_at">Created</option>
              <option value="number">PR number</option>
            </select>
          </label>
          <div className="flex flex-col justify-end gap-3">
            <label className="text-sm text-slate-400">
              <span className="mb-2 block text-xs uppercase tracking-[0.1em] text-slate-400">Order</span>
              <select value={order} onChange={(event) => updateFilter("order", event.target.value, "desc")} className="form-control">
                <option value="desc">Descending</option>
                <option value="asc">Ascending</option>
              </select>
            </label>
            <button
              onClick={() => {
                setSearchParams({}, { replace: true });
              }}
              disabled={!hasFilters}
              className="btn btn-ghost w-full"
            >
              Clear filters
            </button>
          </div>
        </div>
      </SectionCard>

      <SectionCard title="Pull Requests" eyebrow={data ? `${data.total} results` : "Current dataset"} variant="surface">
        {isLoading ? <LoadingState label="Loading pull requests" /> : null}
        {isError ? <EmptyState title="Could not load pull requests" description="We couldn't load the review queue. Try again in a moment." /> : null}
        {!isLoading && !isError && data && data.items.length === 0 ? (
          <EmptyState
            title="No pull requests match these filters"
            description="Try widening the filters or clear them to see the full queue."
            action={
              hasFilters ? (
                <button
                  onClick={() => setSearchParams({}, { replace: true })}
                  className="btn btn-secondary"
                >
                  Clear all filters
                </button>
              ) : (
                <Link to="/settings" className="btn btn-secondary">
                  Open data settings <span aria-hidden="true" className="ml-2">→</span>
                </Link>
              )
            }
          />
        ) : null}
        {!isLoading && !isError && data && data.items.length > 0 ? (
          <div className="data-shell">
            <div aria-hidden="true" className="hidden grid-cols-[minmax(15rem,1.8fr)_minmax(9rem,0.85fr)_minmax(6rem,0.55fr)_minmax(9rem,0.8fr)_minmax(4rem,0.35fr)_minmax(9rem,0.7fr)] gap-4 bg-white/[0.025] px-4 py-3 text-xs uppercase tracking-[0.1em] text-slate-400 2xl:grid">
              <span>PR</span>
              <span>Repository</span>
              <span>Status</span>
              <span>Risk</span>
              <span>Files</span>
              <span>Updated</span>
            </div>
            <ul className="divide-y divide-white/5" aria-label="Pull requests">
              {data.items.map((pullRequest) => (
                <li key={pullRequest.id}>
                  <Link
                    to={`/pull-requests/${pullRequest.id}`}
                    className="data-row-link group grid grid-cols-2 gap-4 px-4 py-4 text-sm text-slate-300 2xl:grid-cols-[minmax(15rem,1.8fr)_minmax(9rem,0.85fr)_minmax(6rem,0.55fr)_minmax(9rem,0.8fr)_minmax(4rem,0.35fr)_minmax(9rem,0.7fr)] 2xl:items-center"
                  >
                    <div className="col-span-2 min-w-0 2xl:col-span-1">
                      <div className="flex items-center gap-3">
                        <p className="font-mono text-xs text-slate-500">#{pullRequest.github_pr_number}</p>
                        <p className="text-xs text-slate-500">{pullRequest.author}</p>
                      </div>
                      <p className="mt-2 font-medium leading-6 text-slate-100 transition group-hover:text-white">{pullRequest.title}</p>
                      {pullRequest.risk_reasons_preview.length > 0 ? (
                        <p className="mt-2 line-clamp-2 text-xs leading-5 text-slate-400">{pullRequest.risk_reasons_preview[0]}</p>
                      ) : null}
                    </div>
                    <div className="min-w-0">
                      <p aria-hidden="true" className="mb-1 text-[10px] uppercase tracking-[0.1em] text-slate-400 2xl:hidden">Repository</p>
                      <span className="sr-only">Repository: </span>
                      <p className="inline truncate font-mono text-xs text-slate-300">{pullRequest.repository_name || "Unknown repository"}</p>
                      <p className="mt-2 text-xs text-slate-500">+{pullRequest.additions} / -{pullRequest.deletions}</p>
                    </div>
                    <div>
                      <p aria-hidden="true" className="mb-1 text-[10px] uppercase tracking-[0.1em] text-slate-400 2xl:hidden">Status</p>
                      <span className="sr-only">Status: </span>
                      <StateBadge state={formatState(pullRequest.state, pullRequest.merged_at)} />
                    </div>
                    <div>
                      <p aria-hidden="true" className="mb-1 text-[10px] uppercase tracking-[0.1em] text-slate-400 2xl:hidden">Risk</p>
                      <span className="sr-only">Risk: </span>
                      <div className="inline-flex flex-wrap items-center gap-3">
                        <RiskBadge level={pullRequest.risk_level} />
                        <div>
                          <span className="font-mono text-xs text-slate-400">{formatRelativeScore(pullRequest.risk_score)}</span>
                          <p className="mt-1 text-[11px] uppercase tracking-[0.1em] text-slate-400">{formatLabel(pullRequest.analysis_status)}</p>
                        </div>
                      </div>
                    </div>
                    <div>
                      <p aria-hidden="true" className="mb-1 text-[10px] uppercase tracking-[0.1em] text-slate-400 2xl:hidden">Files</p>
                      <span className="sr-only">Files changed: </span>
                      <p className="inline font-mono text-xs text-slate-400">{pullRequest.changed_files_count}</p>
                    </div>
                    <div className="relative pr-7">
                      <p aria-hidden="true" className="mb-1 text-[10px] uppercase tracking-[0.1em] text-slate-400 2xl:hidden">Updated</p>
                      <span className="sr-only">Updated: </span>
                      <p className="inline text-xs text-slate-300">{formatDateTime(pullRequest.updated_at)}</p>
                      {pullRequest.last_synced_at ? (
                        <p className="mt-2 text-[11px] uppercase tracking-[0.1em] text-slate-400">Synced {formatDateTime(pullRequest.last_synced_at)}</p>
                      ) : null}
                      <span aria-hidden="true" className="absolute right-0 top-1/2 -translate-y-1/2 text-lg text-slate-600 transition group-hover:translate-x-1 group-hover:text-[var(--accent)]">→</span>
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </SectionCard>
    </div>
  );
}
