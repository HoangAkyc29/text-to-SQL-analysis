import { describe, expect, it, vi } from "vitest";
import { api, safeLogValue } from "@/lib/utils";

describe("safeLogValue", () => {
  it("redacts authorization and secret values", () => {
    const value = safeLogValue({ authorization: "Bearer abc.def.ghi", password: "not-for-display" });
    expect(value).not.toContain("abc.def.ghi");
    expect(value).not.toContain("not-for-display");
    expect(value).toContain("[REDACTED]");
  });
});

describe("api", () => {
  it("returns parsed JSON for successful responses", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ ok: true }), { status: 200, headers: { "Content-Type": "application/json" } })));
    await expect(api<{ ok: boolean }>("/api/test")).resolves.toEqual({ ok: true });
    vi.unstubAllGlobals();
  });

  it("throws backend detail on errors", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: "denied" }), { status: 403, headers: { "Content-Type": "application/json" } })));
    await expect(api("/api/test")).rejects.toThrow("denied");
    vi.unstubAllGlobals();
  });
});
