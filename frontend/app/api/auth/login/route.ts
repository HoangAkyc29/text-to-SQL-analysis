import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { assertSameOrigin, AUTH_COOKIE, BACKEND_URL, PROFILE_COOKIE } from "@/lib/server-bff";

const credentialsSchema = z.object({
  username: z.string().trim().min(1).max(128),
  password: z.string().min(1).max(1024),
});

export async function POST(request: NextRequest) {
  try {
    assertSameOrigin(request);
    const credentials = credentialsSchema.parse(await request.json());
    const upstream = await fetch(`${BACKEND_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(credentials),
      cache: "no-store",
      signal: AbortSignal.timeout(20_000),
    });
    const data = await upstream.json().catch(() => ({}));
    if (!upstream.ok || typeof data.access_token !== "string") {
      return NextResponse.json({ detail: data.detail ?? "invalid_credentials" }, { status: upstream.status || 401 });
    }
    const profile = { role: data.role ?? "analyst", display_name: data.display_name ?? credentials.username };
    const response = NextResponse.json({ user: profile });
    const cookieOptions = {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict" as const,
      path: "/",
      maxAge: 60 * 60 * 8,
    };
    response.cookies.set(AUTH_COOKIE, data.access_token, cookieOptions);
    response.cookies.set(PROFILE_COOKIE, Buffer.from(JSON.stringify(profile)).toString("base64url"), cookieOptions);
    return response;
  } catch (error) {
    const detail = error instanceof z.ZodError ? "invalid_credentials_shape" : error instanceof Error ? error.message : "login_failed";
    return NextResponse.json({ detail }, { status: detail === "cross_origin_request" ? 403 : 400 });
  }
}
