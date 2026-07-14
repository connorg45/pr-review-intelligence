type PullRequestQueueFilters = {
  state?: string;
  risk?: string;
  search?: string;
  sort?: string;
  order?: string;
};

export function pullRequestQueueUrl(filters: PullRequestQueueFilters = {}) {
  const params = new URLSearchParams();

  Object.entries(filters).forEach(([key, value]) => {
    if (value && value !== "all") {
      params.set(key, value);
    }
  });

  const query = params.toString();
  return query ? `/pull-requests?${query}` : "/pull-requests";
}
