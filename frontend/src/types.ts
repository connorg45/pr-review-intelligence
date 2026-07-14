export type RiskLevel = "low" | "medium" | "high";

export interface SummaryPayload {
  summary: {
    total_prs: number;
    open_prs: number;
    high_risk_prs: number;
    avg_risk_score: number;
    avg_time_to_first_review_hours: number | null;
  };
  risk_distribution: Array<{ level: RiskLevel; count: number }>;
  trend: Array<{ date: string; avg_risk_score: number; pr_count: number }>;
  high_risk_prs: PullRequestListItem[];
  recent_events: EventItem[];
  repositories: RepositoryItem[];
}

export interface RepositoryItem {
  id: number;
  owner: string;
  name: string;
  full_name: string;
  source_type: string;
  github_repo_id: number | null;
  created_at: string;
  updated_at: string;
  stats: {
    total_prs: number;
    open_prs: number;
    high_risk_prs: number;
    average_risk_score: number;
  };
}

export interface PullRequestListItem {
  id: number;
  repository_id: number;
  repository_name: string | null;
  github_pr_number: number;
  github_pr_id: number | null;
  title: string;
  author: string;
  state: string;
  url: string | null;
  additions: number;
  deletions: number;
  changed_files_count: number;
  created_at: string;
  updated_at: string;
  merged_at: string | null;
  first_review_at: string | null;
  risk_score: number | null;
  risk_level: RiskLevel | null;
  analysis_status: string;
  last_synced_at: string | null;
  risk_reasons_preview: string[];
}

export interface ReviewerRecommendation {
  reviewer: string;
  score: number;
  reasons: string[];
}

export interface AnalysisResult {
  id: number;
  engine_version: string;
  risk_score: number;
  risk_level: RiskLevel;
  reasons: string[];
  reviewer_recommendations: ReviewerRecommendation[];
  analyzed_at: string;
}

export interface PullRequestFileItem {
  id: number;
  path: string;
  additions: number;
  deletions: number;
  change_type: string;
  is_sensitive: boolean;
  is_test_file: boolean;
}

export interface EventItem {
  id: number;
  repository_id: number | null;
  repository_name: string | null;
  pull_request_id: number | null;
  pull_request_number: number | null;
  event_type: string;
  message: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface PullRequestDetail extends PullRequestListItem {
  analysis_result: AnalysisResult | null;
  files: PullRequestFileItem[];
  analysis_history: AnalysisResult[];
  activity: EventItem[];
}

export interface PullRequestListResponse {
  items: PullRequestListItem[];
  total: number;
  filters: {
    state: string;
    risk: string;
    search: string;
    sort: string;
    order: string;
  };
}

export interface ConfigPayload {
  github: {
    configured: boolean;
    api_base_url: string;
  };
  app: {
    demo_mode_available: boolean;
    default_sync_limit: number;
    auto_seed_demo: boolean;
    write_operations_enabled: boolean;
  };
  repositories: RepositoryItem[];
}

export interface SyncResponse {
  message: string;
  repository?: RepositoryItem;
  sync_run?: {
    id: number;
    repository_id: number;
    repository_name: string | null;
    source_type: string;
    status: string;
    started_at: string;
    completed_at: string | null;
    pr_count: number;
    metadata: Record<string, unknown>;
    error_message: string | null;
  };
  processed_prs?: number;
  changed_prs?: number;
  reanalyzed_prs?: number;
  unchanged_prs?: number;
  repositories?: RepositoryItem[];
  pull_requests?: PullRequestListItem[];
  created?: boolean;
}
