import { NextRequest, NextResponse } from "next/server";
import { assertSameOrigin, clearSessionCookies } from "@/lib/server-bff";

export async function POST(request: NextRequest) {
  try {
    assertSameOrigin(request);
  } catch {
    return NextResponse.json({ detail: "cross_origin_request" }, { status: 403 });
  }
  return clearSessionCookies(NextResponse.json({ ok: true }));
}
