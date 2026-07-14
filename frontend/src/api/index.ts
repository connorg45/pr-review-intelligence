import { api } from "./client";
import type { ConfigPayload, PullRequestDetail, PullRequestListResponse, SummaryPayload, SyncResponse } from "../types";

export async function fetchDashboard() {
  const response = await api.get<SummaryPayload>("/dashboard/summary");
  return response.data;
}

export async function fetchPullRequests(params: Record<string, string>) {
  const response = await api.get<PullRequestListResponse>("/pull-requests", { params });
  return response.data;
}

export async function fetchPullRequest(id: string) {
  const response = await api.get<{ item: PullRequestDetail }>(`/pull-requests/${id}`);
  return response.data.item;
}

export async function fetchEvents(limit = 100) {
  const response = await api.get<{ items: SummaryPayload["recent_events"] }>("/events", { params: { limit } });
  return response.data.items;
}

export async function fetchRepositories() {
  const response = await api.get<{ items: SummaryPayload["repositories"] }>("/repositories");
  return response.data.items;
}

export async function fetchConfig() {
  const response = await api.get<ConfigPayload>("/config");
  return response.data;
}

export async function resetDemo() {
  const response = await api.post("/demo/reset");
  return response.data;
}

export async function syncRepository(payload: {
  source_type: string;
  owner?: string;
  name?: string;
  limit?: number;
}) {
  const response = await api.post<SyncResponse>("/repositories/sync", payload);
  return response.data;
}

export async function analyzePullRequest(id: number) {
  const response = await api.post(`/pull-requests/${id}/analyze`);
  return response.data;
}
