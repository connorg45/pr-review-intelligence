export function formatDateTime(value: string | null | undefined) {
  if (!value) {
    return "Not available";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "Not available";
  }
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

export function formatRelativeScore(value: number | null | undefined) {
  if (value === null || value === undefined) {
    return "Pending";
  }
  return `${value}/100`;
}

export function formatState(state: string, mergedAt?: string | null) {
  if (mergedAt) {
    return "merged";
  }
  return state;
}

export function formatCompactNumber(value: number | null | undefined) {
  if (value === null || value === undefined) {
    return "0";
  }
  return new Intl.NumberFormat("en-US", { notation: "compact", maximumFractionDigits: 1 }).format(value);
}

export function formatLabel(value: string | null | undefined) {
  if (!value) {
    return "Not available";
  }

  return value
    .replace(/[._-]+/g, " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

export function formatEventType(value: string) {
  const labels: Record<string, string> = {
    "analysis.completed": "Risk updated",
    "sync.started": "Sync started",
    "sync.completed": "Sync completed",
    "sync.failed": "Sync failed",
  };

  return labels[value] || formatLabel(value);
}

export function formatSourceType(value: string) {
  return value === "demo" ? "Sample" : formatLabel(value);
}
