import { NextRequest, NextResponse } from "next/server";

/** Secure/__Host cookies only when COOKIE_SECURE=1 (real HTTPS). NODE_ENV=production alone is not enough — local Docker serves HTTP on :13000. */
export const COOKIE_SECURE = process.env.COOKIE_SECURE === "1";
export const AUTH_COOKIE = COOKIE_SECURE ? "__Host-agent_session" : "agent_session";
export const PROFILE_COOKIE = COOKIE_SECURE ? "__Host-agent_profile" : "agent_profile";
export const BACKEND_URL = (
  process.env.BACKEND_URL ??
  process.env.CHAT_GATEWAY_URL ??
  "http://127.0.0.1:18300"
).replace(/\/$/, "");

export function authCookieOptions() {
  return {
    httpOnly: true,
    secure: COOKIE_SECURE,
    sameSite: "lax" as const,
    path: "/",
    maxAge: 60 * 60 * 8,
  };
}

export function clearSessionCookies(response: NextResponse) {
  for (const name of [
    AUTH_COOKIE,
    PROFILE_COOKIE,
    "agent_session",
    "agent_profile",
    "__Host-agent_session",
    "__Host-agent_profile",
  ]) {
    response.cookies.delete(name);
  }
  return response;
}

const allowedRoots = new Set([
  "analyses",
  "analysis",
  "artifacts",
  "attachments",
  "chat",
  "domain-rules",
  "events",
  "feedback",
  "health",
  "sessions",
]);

export function assertSameOrigin(request: NextRequest) {
  if (["GET", "HEAD", "OPTIONS"].includes(request.method)) return;
  // Browsers set this for real same-origin navigations/fetches.
  const fetchSite = request.headers.get("sec-fetch-site");
  if (fetchSite === "same-origin") return;
  const origin = request.headers.get("origin");
  if (!origin) return;
  // Prefer Host / X-Forwarded-Host over nextUrl.origin: inside Docker the
  // app listens on :3000 while the public mapped port may be :13000, so
  // nextUrl.origin can disagree with the browser Origin and false-reject.
  const hostHeader =
    request.headers.get("x-forwarded-host")?.split(",")[0]?.trim() ||
    request.headers.get("host");
  if (!hostHeader) throw new Error("cross_origin_request");
  let originHost: string;
  try {
    originHost = new URL(origin).host;
  } catch {
    throw new Error("cross_origin_request");
  }
  const normalize = (host: string) =>
    host.toLowerCase().replace(/^127\.0\.0\.1(?=:|$)/, "localhost");
  if (normalize(originHost) !== normalize(hostHeader)) {
    throw new Error("cross_origin_request");
  }
}

export function backendPath(parts: string[], search = "") {
  if (!parts.length || !allowedRoots.has(parts[0])) throw new Error("unsupported_proxy_path");
  if (parts.some((part) => !/^[A-Za-z0-9._~-]+$/.test(part) || part === "..")) throw new Error("invalid_proxy_path");
  return `${BACKEND_URL}/${parts.map(encodeURIComponent).join("/")}${search}`;
}

export function sessionToken(request: NextRequest): string | undefined {
  return (
    request.cookies.get(AUTH_COOKIE)?.value ||
    request.cookies.get("agent_session")?.value ||
    request.cookies.get("__Host-agent_session")?.value
  );
}

export function authHeaders(request: NextRequest, extra?: HeadersInit) {
  const token = sessionToken(request);
  const headers = new Headers(extra);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  headers.delete("cookie");
  headers.delete("host");
  return headers;
}

export function upstreamError(status: number, detail: string) {
  return NextResponse.json({ detail }, { status });
}

export async function parseUpstream(response: Response) {
  const contentType = response.headers.get("content-type") ?? "application/json";
  const headers = new Headers({ "content-type": contentType, "cache-control": "no-store" });
  if (response.headers.has("content-disposition")) headers.set("content-disposition", response.headers.get("content-disposition")!);
  return new NextResponse(response.body, { status: response.status, headers });
}
