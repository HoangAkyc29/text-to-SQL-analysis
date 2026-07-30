import { NextRequest, NextResponse } from "next/server";
import { PROFILE_COOKIE, clearSessionCookies, sessionToken } from "@/lib/server-bff";

export async function GET(request: NextRequest) {
  const token = sessionToken(request);
  if (!token) return NextResponse.json({ detail: "unauthenticated" }, { status: 401 });
  let profile: Record<string, unknown> = {};
  try {
    const raw =
      request.cookies.get(PROFILE_COOKIE)?.value ??
      request.cookies.get("agent_profile")?.value ??
      request.cookies.get("__Host-agent_profile")?.value ??
      "";
    profile = JSON.parse(Buffer.from(raw, "base64url").toString());
  } catch {
    profile = {};
  }
  let claims: Record<string, unknown> = {};
  try {
    claims = JSON.parse(Buffer.from(token.split(".")[1] ?? "", "base64url").toString());
  } catch {
    return NextResponse.json({ detail: "invalid_session" }, { status: 401 });
  }
  if (typeof claims.exp === "number" && claims.exp * 1000 <= Date.now()) {
    return clearSessionCookies(NextResponse.json({ detail: "session_expired" }, { status: 401 }));
  }
  return NextResponse.json({
    user: {
      sub: claims.sub,
      role: profile.role ?? claims.role,
      display_name: profile.display_name ?? claims.sub,
      store_ids: claims.store_ids ?? null,
    },
  });
}
