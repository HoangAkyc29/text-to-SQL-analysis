import { NextRequest, NextResponse } from "next/server";
import { AUTH_COOKIE, PROFILE_COOKIE } from "@/lib/server-bff";

export async function GET(request: NextRequest) {
  const token = request.cookies.get(AUTH_COOKIE)?.value;
  if (!token) return NextResponse.json({ detail: "unauthenticated" }, { status: 401 });
  let profile: Record<string, unknown> = {};
  try {
    profile = JSON.parse(Buffer.from(request.cookies.get(PROFILE_COOKIE)?.value ?? "", "base64url").toString());
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
    const response = NextResponse.json({ detail: "session_expired" }, { status: 401 });
    response.cookies.delete(AUTH_COOKIE);
    response.cookies.delete(PROFILE_COOKIE);
    return response;
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
