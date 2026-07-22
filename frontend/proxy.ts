import { NextRequest, NextResponse } from "next/server";
import { AUTH_COOKIE } from "@/lib/server-bff";

export function proxy(request: NextRequest) {
  const authenticated = Boolean(request.cookies.get(AUTH_COOKIE)?.value);
  const isLogin = request.nextUrl.pathname === "/login";
  if (!authenticated && !isLogin) return NextResponse.redirect(new URL("/login", request.url));
  if (authenticated && isLogin) return NextResponse.redirect(new URL("/", request.url));
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
