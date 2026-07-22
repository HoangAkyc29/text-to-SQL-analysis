import { NextRequest, NextResponse } from "next/server";
import { assertSameOrigin, AUTH_COOKIE, PROFILE_COOKIE } from "@/lib/server-bff";

export async function POST(request: NextRequest) {
  try {
    assertSameOrigin(request);
  } catch {
    return NextResponse.json({ detail: "cross_origin_request" }, { status: 403 });
  }
  const response = NextResponse.json({ ok: true });
  response.cookies.delete(AUTH_COOKIE);
  response.cookies.delete(PROFILE_COOKIE);
  return response;
}
