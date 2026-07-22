"use client";

import { useQuery } from "@tanstack/react-query";
import { AnimatePresence, motion } from "framer-motion";
import { Activity, Bot, ChevronDown, Clock3, HeartPulse, History, LogOut, Menu, MessageSquareText, Moon, Plus, Settings, ShieldCheck, Sun, Trash2, X } from "lucide-react";
import { useTheme } from "next-themes";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ChatWorkspace } from "@/components/chat-workspace";
import { DomainRulesPanel, HealthPanel, HistoryPanel, SettingsPanel } from "@/components/secondary-panels";
import { Badge, Button } from "@/components/ui";
import { ensureSession, useConsoleStore } from "@/lib/store";
import type { User } from "@/lib/types";
import { api, cn, formatDate } from "@/lib/utils";

type View = "chat" | "history" | "rules" | "health" | "settings";

export function ConsoleShell() {
  const router = useRouter();
  const { theme, setTheme } = useTheme();
  const [view, setView] = useState<View>("chat");
  const [profileOpen, setProfileOpen] = useState(false);
  const sessions = useConsoleStore((s) => s.sessions);
  const activeId = useConsoleStore((s) => s.activeSessionId);
  const sidebarOpen = useConsoleStore((s) => s.sidebarOpen);
  const { createSession, selectSession, removeSession, setSidebarOpen } = useConsoleStore();
  const { data } = useQuery({ queryKey: ["me"], queryFn: () => api<{ user: User }>("/api/auth/me"), retry: false });

  useEffect(() => { ensureSession(); }, []);
  const navigate = (next: View) => { setView(next); setSidebarOpen(false); };
  const newChat = () => { createSession(); setView("chat"); };
  const logout = async () => { await api("/api/auth/logout", { method: "POST" }); router.replace("/login"); router.refresh(); };

  const sidebar = (
    <aside className="flex h-full w-[285px] shrink-0 flex-col border-r border-[var(--border)] bg-[var(--panel-soft)]">
      <div className="flex h-16 items-center justify-between px-4">
        <button className="flex items-center gap-3 text-left" onClick={() => navigate("chat")}><span className="grid size-9 place-items-center rounded-xl bg-[var(--accent)] text-white shadow-lg shadow-indigo-500/20"><Bot className="size-5" /></span><div><p className="font-semibold leading-4">Axiom</p><p className="text-[10px] uppercase tracking-[.16em] text-[var(--subtle)]">Agent console</p></div></button>
        <Button className="lg:hidden" size="icon" variant="ghost" onClick={() => setSidebarOpen(false)} aria-label="Close navigation"><X className="size-5" /></Button>
      </div>
      <div className="px-3"><Button className="w-full justify-start" onClick={newChat}><Plus className="size-4" />New analysis</Button></div>
      <nav className="mt-4 space-y-1 px-3" aria-label="Primary navigation">
        {([
          ["chat", MessageSquareText, "Workspace"],
          ["history", History, "History"],
          ["rules", ShieldCheck, "Domain rules"],
          ["health", HeartPulse, "System health"],
          ["settings", Settings, "Settings"],
        ] as const).map(([id, Icon, label]) => <button key={id} onClick={() => navigate(id)} className={cn("flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition", view === id ? "bg-[var(--muted)] text-[var(--foreground)]" : "text-[var(--subtle)] hover:bg-[var(--muted)]")}><Icon className="size-4" />{label}</button>)}
      </nav>
      <div className="mt-5 flex items-center justify-between px-5 text-[11px] font-semibold uppercase tracking-wider text-[var(--subtle)]"><span>Recent sessions</span><Clock3 className="size-3.5" /></div>
      <div className="scrollbar-thin mt-2 flex-1 space-y-1 overflow-y-auto px-3">
        {sessions.map((session) => <div key={session.id} className={cn("group relative rounded-xl", activeId === session.id && view === "chat" && "bg-[var(--muted)]")}><button className="w-full px-3 py-2.5 pr-9 text-left" onClick={() => { selectSession(session.id); setView("chat"); }}><p className="truncate text-sm font-medium">{session.title}</p><p className="mt-1 text-[11px] text-[var(--subtle)]">{formatDate(session.updatedAt)}</p></button><button className="absolute right-2 top-3 rounded-md p-1 text-[var(--subtle)] opacity-0 hover:bg-red-500/10 hover:text-red-500 group-hover:opacity-100 focus:opacity-100" onClick={() => removeSession(session.id)} aria-label={`Delete ${session.title}`}><Trash2 className="size-3.5" /></button></div>)}
      </div>
      <div className="border-t border-[var(--border)] p-3">
        <div className="relative">
          <button onClick={() => setProfileOpen(!profileOpen)} className="flex w-full items-center gap-3 rounded-xl p-2 hover:bg-[var(--muted)]"><span className="grid size-9 place-items-center rounded-full bg-gradient-to-br from-indigo-500 to-cyan-500 text-xs font-semibold text-white">{(data?.user.display_name ?? "U").slice(0, 2).toUpperCase()}</span><div className="min-w-0 flex-1 text-left"><p className="truncate text-sm font-medium">{data?.user.display_name ?? "Analyst"}</p><p className="truncate text-xs text-[var(--subtle)]">{data?.user.role ?? "Loading…"}</p></div><ChevronDown className="size-4 text-[var(--subtle)]" /></button>
          {profileOpen && <div className="absolute bottom-14 left-0 w-full rounded-xl border border-[var(--border)] bg-[var(--panel)] p-1 shadow-xl"><button onClick={logout} className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-red-500 hover:bg-red-500/10"><LogOut className="size-4" />Sign out</button></div>}
        </div>
      </div>
    </aside>
  );

  return (
    <div className="flex h-screen overflow-hidden">
      <div className="hidden lg:block">{sidebar}</div>
      <AnimatePresence>{sidebarOpen && <><motion.div className="fixed inset-0 z-40 bg-slate-950/45 backdrop-blur-sm lg:hidden" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setSidebarOpen(false)} /><motion.div className="fixed inset-y-0 left-0 z-50 lg:hidden" initial={{ x: -300 }} animate={{ x: 0 }} exit={{ x: -300 }}>{sidebar}</motion.div></>}</AnimatePresence>
      <main className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-16 shrink-0 items-center justify-between border-b border-[var(--border)] bg-[color-mix(in_srgb,var(--panel)_88%,transparent)] px-4 backdrop-blur-xl sm:px-6">
          <div className="flex items-center gap-3"><Button className="lg:hidden" size="icon" variant="ghost" onClick={() => setSidebarOpen(true)} aria-label="Open navigation"><Menu className="size-5" /></Button><div><h1 className="text-sm font-semibold capitalize">{view === "chat" ? sessions.find((s) => s.id === activeId)?.title ?? "Workspace" : view.replace("-", " ")}</h1><div className="mt-0.5 flex items-center gap-1.5 text-[11px] text-[var(--subtle)]"><Activity className="size-3 text-emerald-500" />Secure workspace</div></div></div>
          <div className="flex items-center gap-2"><Badge tone="success" className="hidden sm:inline-flex"><span className="mr-1 size-1.5 rounded-full bg-emerald-500" />Connected</Badge><Button size="icon" variant="ghost" onClick={() => setTheme(theme === "dark" ? "light" : "dark")} aria-label="Toggle color theme">{theme === "dark" ? <Sun className="size-4" /> : <Moon className="size-4" />}</Button></div>
        </header>
        <div className="min-h-0 flex-1">{view === "chat" && <ChatWorkspace />}{view === "history" && <HistoryPanel onOpen={(id) => { selectSession(id); setView("chat"); }} />}{view === "rules" && <DomainRulesPanel />}{view === "health" && <HealthPanel />}{view === "settings" && <SettingsPanel />}</div>
      </main>
    </div>
  );
}
