"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Activity, Archive, Check, CheckCircle2, Database, ExternalLink, HeartPulse, History, RefreshCw, Search, Server, ShieldCheck, SlidersHorizontal, X } from "lucide-react";
import { useTheme } from "next-themes";
import { useState } from "react";
import { Badge, Button, Card, Input, Skeleton } from "@/components/ui";
import { useConsoleStore } from "@/lib/store";
import type { DomainRule, Health as HealthType } from "@/lib/types";
import { api, cn, formatDate } from "@/lib/utils";

function PageFrame({ icon: Icon, title, description, children, action }: { icon: typeof Activity; title: string; description: string; children: React.ReactNode; action?: React.ReactNode }) {
  return <div className="scrollbar-thin h-full overflow-y-auto p-5 sm:p-8"><div className="mx-auto max-w-5xl"><div className="mb-7 flex flex-wrap items-start justify-between gap-4"><div className="flex gap-4"><span className="grid size-11 shrink-0 place-items-center rounded-2xl bg-indigo-500/10 text-indigo-500"><Icon className="size-5" /></span><div><h2 className="text-2xl font-semibold tracking-tight">{title}</h2><p className="mt-1 text-sm text-[var(--subtle)]">{description}</p></div></div>{action}</div>{children}</div></div>;
}

export function HistoryPanel({ onOpen }: { onOpen: (id: string) => void }) {
  const sessions = useConsoleStore((s) => s.sessions);
  const [query, setQuery] = useState("");
  const filtered = sessions.filter((session) => `${session.title} ${session.messages.map((m) => m.content).join(" ")}`.toLowerCase().includes(query.toLowerCase()));
  return <PageFrame icon={History} title="Analysis history" description="Resume previous conversations and review completed work."><div className="relative mb-5"><Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-[var(--subtle)]" /><Input className="pl-10" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search sessions…" /></div><div className="space-y-3">{filtered.length ? filtered.map((session) => <Card key={session.id} className="flex flex-wrap items-center gap-4 p-4"><span className="grid size-10 place-items-center rounded-xl bg-[var(--muted)]"><Archive className="size-4" /></span><div className="min-w-0 flex-1"><p className="truncate font-medium">{session.title}</p><p className="mt-1 text-xs text-[var(--subtle)]">{session.messages.length} messages · {formatDate(session.updatedAt)}</p></div><Badge tone={session.messages.some((m) => m.response?.error) ? "warning" : "success"}>{session.messages.some((m) => m.pending) ? "running" : "saved"}</Badge><Button variant="secondary" size="sm" onClick={() => onOpen(session.id)}>Open<ExternalLink className="size-3" /></Button></Card>) : <Empty label="No matching sessions" />}</div></PageFrame>;
}

export function DomainRulesPanel() {
  const queryClient = useQueryClient();
  const [status, setStatus] = useState("candidate");
  const rules = useQuery({ queryKey: ["domain-rules", status], queryFn: () => api<DomainRule[]>(`/api/bff/domain-rules?status=${status}&limit=100`) });
  const review = useMutation({
    mutationFn: ({ id, action }: { id: string; action: "confirm" | "reject" | "stale" }) => api(`/api/bff/domain-rules/${encodeURIComponent(id)}/review`, { method: "POST", body: JSON.stringify({ action }) }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["domain-rules"] }),
  });
  return <PageFrame icon={ShieldCheck} title="Domain rule queue" description="Human review keeps learned business context accurate and auditable." action={<Button variant="secondary" size="sm" onClick={() => rules.refetch()}><RefreshCw className={cn("size-3.5", rules.isFetching && "animate-spin")} />Refresh</Button>}><div className="mb-5 flex gap-2">{["candidate", "confirmed", "rejected"].map((item) => <Button key={item} variant={status === item ? "primary" : "secondary"} size="sm" onClick={() => setStatus(item)} className="capitalize">{item}</Button>)}</div>{rules.isLoading ? <div className="space-y-3"><Skeleton className="h-32" /><Skeleton className="h-32" /></div> : rules.error ? <ErrorState message={(rules.error as Error).message} retry={() => rules.refetch()} /> : <div className="grid gap-4 lg:grid-cols-2">{rules.data?.length ? rules.data.map((rule) => { const id = rule.rule_id ?? rule.id ?? ""; return <Card key={id} className="p-5"><div className="flex items-center justify-between"><Badge tone={rule.status === "confirmed" ? "success" : rule.status === "rejected" ? "danger" : "warning"}>{rule.status ?? "candidate"}</Badge>{rule.confidence != null && <span className="text-xs text-[var(--subtle)]">{Math.round(rule.confidence * 100)}% confidence</span>}</div><h3 className="mt-4 font-semibold">{rule.title ?? "Proposed domain rule"}</h3><p className="mt-2 text-sm leading-6 text-[var(--subtle)]">{rule.statement ?? rule.description ?? "No description supplied."}</p><p className="mt-3 text-[10px] text-[var(--subtle)]">Source: {rule.source_trace_id ?? "system"} · {formatDate(rule.created_at)}</p>{status === "candidate" && <div className="mt-4 flex gap-2"><Button size="sm" onClick={() => review.mutate({ id, action: "confirm" })}><Check className="size-3.5" />Confirm</Button><Button variant="danger" size="sm" onClick={() => review.mutate({ id, action: "reject" })}><X className="size-3.5" />Reject</Button></div>}</Card>; }) : <Empty label={`No ${status} rules`} />}</div>}</PageFrame>;
}

export function HealthPanel() {
  const health = useQuery({ queryKey: ["health"], queryFn: () => api<HealthType>("/api/bff/health/ready"), refetchInterval: 30_000 });
  const data = health.data;
  const services = [{ name: "Redis state", ok: data?.redis, icon: Database }, { name: "Mongo memory", ok: data?.mongo, icon: Database }, ...Object.entries(data?.agents ?? {}).map(([name, state]) => ({ name: `Agent ${name}`, ok: state === "ok", icon: Server }))];
  return <PageFrame icon={HeartPulse} title="System health" description="Live readiness across the agent platform and its dependencies." action={<Button variant="secondary" size="sm" onClick={() => health.refetch()}><RefreshCw className={cn("size-3.5", health.isFetching && "animate-spin")} />Check now</Button>}><Card className={cn("mb-6 overflow-hidden p-6", data?.ok ? "border-emerald-500/20" : "border-amber-500/20")}><div className="flex items-center gap-4"><span className={cn("grid size-12 place-items-center rounded-full", data?.ok ? "bg-emerald-500/10 text-emerald-500" : "bg-amber-500/10 text-amber-500")}><Activity /></span><div><h3 className="text-lg font-semibold">{health.isLoading ? "Checking platform…" : data?.ok ? "All core systems operational" : "Some systems need attention"}</h3><p className="text-sm text-[var(--subtle)]">Last checked {new Date().toLocaleTimeString()}</p></div></div></Card><div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{services.map(({ name, ok, icon: Icon }) => <Card className="p-5" key={name}><div className="flex items-center justify-between"><span className="grid size-9 place-items-center rounded-xl bg-[var(--muted)]"><Icon className="size-4" /></span><Badge tone={ok ? "success" : "danger"}>{ok ? "Operational" : "Unavailable"}</Badge></div><p className="mt-4 font-medium">{name}</p><p className="mt-1 text-xs text-[var(--subtle)]">{ok ? "Responding normally" : "Readiness check failed"}</p></Card>)}</div></PageFrame>;
}

export function SettingsPanel() {
  const { theme, setTheme } = useTheme();
  const detailOpen = useConsoleStore((s) => s.detailOpen);
  const setDetailOpen = useConsoleStore((s) => s.setDetailOpen);
  return <PageFrame icon={SlidersHorizontal} title="Settings" description="Personalize the workspace without changing platform policy."><div className="space-y-4"><Card className="p-5"><h3 className="font-semibold">Appearance</h3><p className="mt-1 text-sm text-[var(--subtle)]">Choose how the console looks on this device.</p><div className="mt-4 flex flex-wrap gap-2">{["light", "dark", "system"].map((item) => <Button key={item} size="sm" variant={theme === item ? "primary" : "secondary"} onClick={() => setTheme(item)} className="capitalize">{item}</Button>)}</div></Card><Card className="p-5"><h3 className="font-semibold">Analysis details</h3><p className="mt-1 text-sm text-[var(--subtle)]">Automatically open the workflow and result inspector.</p><label className="mt-4 flex cursor-pointer items-center gap-3 text-sm"><input type="checkbox" checked={detailOpen} onChange={(e) => setDetailOpen(e.target.checked)} className="size-4 accent-indigo-500" />Show details panel</label></Card><Card className="p-5"><div className="flex items-center gap-3"><CheckCircle2 className="size-5 text-emerald-500" /><div><h3 className="font-semibold">Privacy defaults active</h3><p className="mt-1 text-sm text-[var(--subtle)]">Credentials are HttpOnly, logs are sanitized, and model chain-of-thought is never displayed.</p></div></div></Card></div></PageFrame>;
}

function Empty({ label }: { label: string }) { return <Card className="col-span-full grid min-h-40 place-items-center border-dashed text-sm text-[var(--subtle)]">{label}</Card>; }
function ErrorState({ message, retry }: { message: string; retry: () => void }) { return <Card className="p-5 text-sm"><p className="text-red-500">{message}</p><Button className="mt-3" size="sm" variant="secondary" onClick={retry}>Try again</Button></Card>; }
