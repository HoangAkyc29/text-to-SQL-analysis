import { NextRequest, NextResponse } from "next/server";
import { assertSameOrigin, authHeaders, backendPath, parseUpstream, upstreamError } from "@/lib/server-bff";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type Context = { params: Promise<{ path: string[] }> };

async function proxy(request: NextRequest, context: Context) {
  try {
    assertSameOrigin(request);
    const { path } = await context.params;
    const target = backendPath(path, request.nextUrl.search);
    const headers = authHeaders(request);
    const contentType = request.headers.get("content-type");
    const accept = request.headers.get("accept");
    if (contentType) headers.set("content-type", contentType);
    if (accept) headers.set("accept", accept);
    const isStream = accept?.includes("text/event-stream");
    const hasBody = !["GET", "HEAD"].includes(request.method);
    const upstream = await fetch(target, {
      method: request.method,
      headers,
      body: hasBody ? await request.arrayBuffer() : undefined,
      cache: "no-store",
      redirect: "manual",
      signal: isStream ? undefined : AbortSignal.timeout(125_000),
    });
    return parseUpstream(upstream);
  } catch (error) {
    const detail = error instanceof Error ? error.message : "proxy_failed";
    const status = detail === "cross_origin_request" ? 403 : detail.includes("path") ? 400 : 502;
    return upstreamError(status, detail);
  }
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
export function OPTIONS() {
  return new NextResponse(null, { status: 204, headers: { Allow: "GET,POST,PUT,PATCH,DELETE,OPTIONS" } });
}
