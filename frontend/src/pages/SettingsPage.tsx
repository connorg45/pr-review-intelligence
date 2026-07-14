import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { fetchConfig, resetDemo, syncRepository } from "../api";
import { EmptyState } from "../components/EmptyState";
import { LoadingState } from "../components/LoadingState";
import { PageHeader } from "../components/PageHeader";
import { SectionCard } from "../components/SectionCard";
import type { SyncResponse } from "../types";
import { formatLabel, formatSourceType } from "../utils/format";
import { pullRequestQueueUrl } from "../utils/routes";

const repoSegmentPattern = /^[A-Za-z0-9_.-]+$/;

type FeedbackState =
  | {
      tone: "success" | "error";
      message: string;
    }
  | null;

function feedbackClass(tone: "success" | "error") {
  return tone === "success"
    ? "border-emerald-400/15 bg-emerald-500/10 text-emerald-100"
    : "border-rose-400/15 bg-rose-500/10 text-rose-100";
}

export function SettingsPage() {
  const queryClient = useQueryClient();
  const [owner, setOwner] = useState("");
  const [name, setName] = useState("");
  const [limit, setLimit] = useState(12);
  const [feedback, setFeedback] = useState<FeedbackState>(null);
  const [lastSyncResult, setLastSyncResult] = useState<SyncResponse | null>(null);
  const hasInitializedLimit = useRef(false);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["config"],
    queryFn: fetchConfig,
  });

  useEffect(() => {
    if (data?.app.default_sync_limit && !hasInitializedLimit.current) {
      setLimit(data.app.default_sync_limit);
      hasInitializedLimit.current = true;
    }
  }, [data?.app.default_sync_limit]);

  const ownerTrimmed = owner.trim();
  const nameTrimmed = name.trim();
  const ownerValid = ownerTrimmed.length > 0 && repoSegmentPattern.test(ownerTrimmed);
  const nameValid = nameTrimmed.length > 0 && repoSegmentPattern.test(nameTrimmed);
  const syncBlockedReason =
    !data?.app.write_operations_enabled
      ? "This public deployment is read-only. Run a trusted local instance to sync repositories."
      : !data?.github.configured
      ? "GitHub access is not configured for this deployment."
      : !ownerTrimmed || !nameTrimmed
        ? "Enter both a repository owner and repository name."
        : !ownerValid || !nameValid
          ? "Owner and repository names can only include letters, numbers, '.', '_' or '-'."
          : limit < 1 || limit > 50
            ? "Recent PR limit must be between 1 and 50."
          : null;

  const demoMutation = useMutation({
    mutationFn: resetDemo,
    onSuccess: async () => {
      setFeedback({ tone: "success", message: "Sample data reset complete. Repositories, pull requests, risk scores, and events are ready." });
      setLastSyncResult(null);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["dashboard"] }),
        queryClient.invalidateQueries({ queryKey: ["pull-requests"] }),
        queryClient.invalidateQueries({ queryKey: ["events"] }),
        queryClient.invalidateQueries({ queryKey: ["config"] }),
        queryClient.invalidateQueries({ queryKey: ["pull-request"] }),
      ]);
    },
    onError: (error: Error) => {
      setFeedback({ tone: "error", message: error.message });
    },
  });

  const syncMutation = useMutation({
    mutationFn: () => syncRepository({ source_type: "github", owner: ownerTrimmed, name: nameTrimmed, limit }),
    onSuccess: async (result) => {
      setFeedback({ tone: "success", message: result.message || "GitHub sync complete." });
      setLastSyncResult(result);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["dashboard"] }),
        queryClient.invalidateQueries({ queryKey: ["pull-requests"] }),
        queryClient.invalidateQueries({ queryKey: ["events"] }),
        queryClient.invalidateQueries({ queryKey: ["config"] }),
      ]);
    },
    onError: (error: Error) => {
      setFeedback({ tone: "error", message: error.message });
    },
  });

  const resetDisabled = !data?.app.write_operations_enabled || demoMutation.isPending || syncMutation.isPending;
  const syncDisabled = Boolean(syncBlockedReason) || syncMutation.isPending || demoMutation.isPending;

  return (
    <div className="page-stack space-y-8">
      <PageHeader
        title="Settings and Sync"
        description="Manage sample data, check the GitHub connection, and sync a repository."
      />

      {feedback ? (
        <div className={`rounded-xl border px-4 py-3 text-sm ${feedbackClass(feedback.tone)}`}>
          <span className="font-mono text-[11px] uppercase tracking-[0.1em] opacity-80">{feedback.tone}</span>
          <p className="mt-1">{feedback.message}</p>
        </div>
      ) : null}

      {isLoading ? <LoadingState label="Loading settings" /> : null}
      {isError ? <EmptyState title="Settings unavailable" description="We couldn't load these settings. Try again in a moment." /> : null}

      {!isLoading && !isError && data ? (
        <div className="grid gap-6 xl:grid-cols-[1.16fr_0.84fr]">
          <div className="xl:order-2">
          <SectionCard title="Sample Dataset" eyebrow="Sample data">
            <div className="space-y-4">
              <div className="border-t border-white/5 pt-4">
                <p className="text-sm leading-6 text-slate-300">
                  Sample data provides realistic repositories, pull requests, sync runs, and event history without requiring a GitHub token.
                </p>
                <div className="mt-4 grid gap-3 md:grid-cols-2">
                  <div className="rounded-xl border border-white/5 bg-[#0c131c] p-3">
                    <p className="font-mono text-[11px] uppercase tracking-[0.1em] text-slate-400">Sample data</p>
                    <p className="mt-2 text-sm text-slate-200">{data.app.auto_seed_demo ? "Enabled" : "Manual only"}</p>
                  </div>
                  <div className="rounded-xl border border-white/5 bg-[#0c131c] p-3">
                    <p className="font-mono text-[11px] uppercase tracking-[0.1em] text-slate-400">Current repos</p>
                    <p className="mt-2 text-sm text-slate-200">{data.repositories.length}</p>
                  </div>
                </div>
              </div>
              <div className="rounded-xl border border-amber-400/15 bg-amber-500/10 p-4 text-sm leading-6 text-amber-100/90">
                {data.app.write_operations_enabled
                  ? "Resetting sample data only replaces sample repositories. Repositories synced from GitHub remain untouched."
                  : "This public demo is read-only. Sample data is refreshed by the deployment process."}
              </div>
              <button
                onClick={() => demoMutation.mutate()}
                disabled={resetDisabled}
                className="btn btn-secondary"
              >
                {!data.app.write_operations_enabled
                  ? "Read-only demo"
                  : demoMutation.isPending
                    ? "Resetting sample data..."
                    : "Reset Sample Dataset"}
              </button>
            </div>
          </SectionCard>
          </div>

          <div className="xl:order-1">
          <SectionCard title="Repository Sync" eyebrow="GitHub connection" variant="surface">
            <div className="grid gap-4 md:grid-cols-2">
              <label className="text-sm text-slate-400">
                <span className="mb-2 block text-xs uppercase tracking-[0.1em] text-slate-400">Owner</span>
                <input
                  value={owner}
                  onChange={(event) => setOwner(event.target.value)}
                  placeholder="acme"
                  className="form-control"
                />
              </label>
              <label className="text-sm text-slate-400">
                <span className="mb-2 block text-xs uppercase tracking-[0.1em] text-slate-400">Repository</span>
                <input
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                  placeholder="example-repo"
                  className="form-control"
                />
              </label>
              <label className="text-sm text-slate-400">
                <span className="mb-2 block text-xs uppercase tracking-[0.1em] text-slate-400">Recent PR limit</span>
                <input
                  type="number"
                  min={1}
                  max={50}
                  value={limit}
                  onChange={(event) => setLimit(Number(event.target.value))}
                  className="form-control"
                />
              </label>
              <div className="rounded-xl border border-white/5 bg-white/[0.02] p-4">
                <p className="font-mono text-[11px] uppercase tracking-[0.1em] text-slate-400">Connection status</p>
                <p className="mt-2 text-sm text-slate-300">
                  {data.github.configured ? "GitHub access is connected." : "GitHub access is not configured in this deployment."}
                </p>
              </div>
            </div>

            <div className="mt-5 grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
              <div className="rounded-xl border border-white/5 bg-white/[0.02] p-4">
                <p className="font-mono text-[11px] uppercase tracking-[0.1em] text-slate-400">Sync behavior</p>
                <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-300">
                  <li>Fetches recent pull requests and changed files for one repo at a time.</li>
                  <li>Updates existing pull requests instead of creating duplicates.</li>
                  <li>Refreshes risk scores only when pull request content changes.</li>
                </ul>
              </div>
              <div className="rounded-xl border border-white/5 bg-[#0c131c] p-4">
                <p className="font-mono text-[11px] uppercase tracking-[0.1em] text-slate-400">Validation</p>
                <p className="mt-3 text-sm leading-6 text-slate-300">{syncBlockedReason || "Repository details and sync limit look valid."}</p>
              </div>
            </div>

            <button
              onClick={() => syncMutation.mutate()}
              disabled={syncDisabled}
              className="btn btn-primary mt-5"
            >
              {syncMutation.isPending ? "Syncing repository..." : "Run GitHub Sync"}
            </button>

            {lastSyncResult?.sync_run ? (
              <div className="mt-5 rounded-xl border border-white/5 bg-white/[0.02] p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p className="font-mono text-[11px] uppercase tracking-[0.1em] text-slate-400">Latest sync result</p>
                    <h3 className="mt-2 text-lg font-semibold text-slate-100">{lastSyncResult.repository?.full_name}</h3>
                  </div>
                  <span className="rounded-full border border-white/10 px-3 py-1 font-mono text-[11px] uppercase tracking-[0.08em] text-slate-300">
                    {formatLabel(lastSyncResult.sync_run.status)}
                  </span>
                </div>
                <div className="mt-4 grid gap-3 md:grid-cols-4">
                  <div className="rounded-xl border border-white/5 bg-[#0c131c] p-3">
                    <p className="text-xs uppercase tracking-[0.1em] text-slate-400">Processed</p>
                    <p className="mt-2 text-lg font-semibold text-slate-50">{lastSyncResult.processed_prs ?? 0}</p>
                  </div>
                  <div className="rounded-xl border border-white/5 bg-[#0c131c] p-3">
                    <p className="text-xs uppercase tracking-[0.1em] text-slate-400">Updated</p>
                    <p className="mt-2 text-lg font-semibold text-slate-50">{lastSyncResult.changed_prs ?? 0}</p>
                  </div>
                  <div className="rounded-xl border border-white/5 bg-[#0c131c] p-3">
                    <p className="text-xs uppercase tracking-[0.1em] text-slate-400">Rescored</p>
                    <p className="mt-2 text-lg font-semibold text-slate-50">{lastSyncResult.reanalyzed_prs ?? 0}</p>
                  </div>
                  <div className="rounded-xl border border-white/5 bg-[#0c131c] p-3">
                    <p className="text-xs uppercase tracking-[0.1em] text-slate-400">Unchanged</p>
                    <p className="mt-2 text-lg font-semibold text-slate-50">{lastSyncResult.unchanged_prs ?? 0}</p>
                  </div>
                </div>
              </div>
            ) : null}
          </SectionCard>
          </div>
        </div>
      ) : null}

      {!isLoading && !isError && data ? (
        <SectionCard title="Tracked Repositories" eyebrow="Synced and sample data">
          {data.repositories.length === 0 ? (
            <EmptyState title="No repositories stored" description="Reset sample data or run a GitHub sync to populate this list." />
          ) : (
            <div className="divide-y divide-white/5">
              {data.repositories.map((repository) => (
                <Link key={repository.id} to={pullRequestQueueUrl({ search: repository.full_name })} className="subtle-link-row group -mx-2 block rounded-xl px-2 py-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-mono text-xs uppercase tracking-[0.1em] text-slate-400">{formatSourceType(repository.source_type)}</p>
                    <span className="font-mono text-[10px] uppercase tracking-[0.1em] text-slate-500 transition group-hover:text-[var(--accent)]">
                      {repository.stats.total_prs} PRs →
                    </span>
                  </div>
                  <h3 className="mt-2 text-lg font-semibold text-slate-100">{repository.full_name}</h3>
                  <div className="mt-4 grid grid-cols-3 gap-3 border-t border-white/5 pt-3 text-sm">
                    <div>
                      <p className="text-slate-500">Open</p>
                      <p className="mt-1 font-semibold text-slate-50">{repository.stats.open_prs}</p>
                    </div>
                    <div>
                      <p className="text-slate-500">High</p>
                      <p className="mt-1 font-semibold text-slate-50">{repository.stats.high_risk_prs}</p>
                    </div>
                    <div>
                      <p className="text-slate-500">Avg risk</p>
                      <p className="mt-1 font-semibold text-slate-50">{repository.stats.average_risk_score}/100</p>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </SectionCard>
      ) : null}
    </div>
  );
}
