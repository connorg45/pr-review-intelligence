import { describe, expect, it } from "vitest";
import { formatCompactNumber, formatDateTime, formatEventType, formatLabel, formatRelativeScore, formatSourceType, formatState } from "./format";

describe("format helpers", () => {
  it("formats valid timestamps and rejects invalid timestamps", () => {
    expect(formatDateTime("not-a-date")).toBe("Not available");
    expect(formatDateTime(null)).toBe("Not available");
    expect(formatDateTime("2026-07-09T19:30:00Z")).not.toBe("Not available");
  });

  it("preserves a zero risk score", () => {
    expect(formatRelativeScore(0)).toBe("0/100");
    expect(formatRelativeScore(null)).toBe("Pending");
  });

  it("uses merged state when a merge timestamp exists", () => {
    expect(formatState("closed", "2026-07-09T19:30:00Z")).toBe("merged");
    expect(formatState("open", null)).toBe("open");
  });

  it("formats missing and large counts", () => {
    expect(formatCompactNumber(undefined)).toBe("0");
    expect(formatCompactNumber(1250)).toBe("1.3K");
  });

  it("turns internal status values into product labels", () => {
    expect(formatEventType("analysis.completed")).toBe("Risk updated");
    expect(formatEventType("sync.started")).toBe("Sync started");
    expect(formatLabel("analysis_pending")).toBe("Analysis Pending");
    expect(formatSourceType("demo")).toBe("Sample");
  });
});
