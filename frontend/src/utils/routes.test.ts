import { describe, expect, it } from "vitest";
import { pullRequestQueueUrl } from "./routes";

describe("route helpers", () => {
  it("returns the base queue when no filters are active", () => {
    expect(pullRequestQueueUrl()).toBe("/pull-requests");
    expect(pullRequestQueueUrl({ state: "all", risk: "all" })).toBe("/pull-requests");
  });

  it("builds encoded, shareable queue filters", () => {
    expect(pullRequestQueueUrl({ search: "acme/payments api", risk: "high" })).toBe(
      "/pull-requests?search=acme%2Fpayments+api&risk=high",
    );
  });
});
