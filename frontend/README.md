# Axiom Agent frontend

Next.js App Router frontend and same-origin BFF for the interactive agent platform.

## Development

```bash
pnpm install
cp .env.example .env.local
pnpm dev
```

`CHAT_GATEWAY_URL` is server-only. The browser communicates exclusively with `/api/auth/*` and `/api/bff/*`; backend JWTs are kept in HttpOnly, same-site cookies.

## Verification

```bash
pnpm typecheck
pnpm lint
pnpm test
pnpm build
pnpm test:e2e
```

Playwright starts the development server automatically. End-to-end specs mock backend responses and cover login validation plus the authenticated chat path.
