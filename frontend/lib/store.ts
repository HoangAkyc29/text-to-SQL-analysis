"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { ChatMessage, Session } from "@/lib/types";

const now = () => new Date().toISOString();
const makeSession = (): Session => {
  const id = crypto.randomUUID();
  return { id, title: "New analysis", createdAt: now(), updatedAt: now(), messages: [], attachments: [] };
};

type ConsoleState = {
  sessions: Session[];
  activeSessionId: string | null;
  sidebarOpen: boolean;
  detailOpen: boolean;
  createSession: () => string;
  selectSession: (id: string) => void;
  removeSession: (id: string) => void;
  addMessage: (sessionId: string, message: ChatMessage) => void;
  patchMessage: (sessionId: string, messageId: string, patch: Partial<ChatMessage>) => void;
  addAttachment: (sessionId: string, attachment: Session["attachments"][number]) => void;
  patchAttachment: (sessionId: string, name: string, status: Session["attachments"][number]["status"]) => void;
  setSidebarOpen: (open: boolean) => void;
  setDetailOpen: (open: boolean) => void;
};

export const useConsoleStore = create<ConsoleState>()(
  persist(
    (set) => ({
      sessions: [],
      activeSessionId: null,
      sidebarOpen: false,
      detailOpen: true,
      createSession: () => {
        const session = makeSession();
        set((state) => ({ sessions: [session, ...state.sessions], activeSessionId: session.id }));
        return session.id;
      },
      selectSession: (id) => set({ activeSessionId: id, sidebarOpen: false }),
      removeSession: (id) =>
        set((state) => {
          const sessions = state.sessions.filter((session) => session.id !== id);
          return { sessions, activeSessionId: state.activeSessionId === id ? sessions[0]?.id ?? null : state.activeSessionId };
        }),
      addMessage: (sessionId, message) =>
        set((state) => ({
          sessions: state.sessions.map((session) => {
            if (session.id !== sessionId) return session;
            const firstUser = message.role === "user" && !session.messages.some((item) => item.role === "user");
            return {
              ...session,
              title: firstUser ? message.content.slice(0, 48) : session.title,
              updatedAt: now(),
              messages: [...session.messages, message],
            };
          }),
        })),
      patchMessage: (sessionId, messageId, patch) =>
        set((state) => ({
          sessions: state.sessions.map((session) =>
            session.id === sessionId
              ? { ...session, updatedAt: now(), messages: session.messages.map((item) => item.id === messageId ? { ...item, ...patch } : item) }
              : session,
          ),
        })),
      addAttachment: (sessionId, attachment) =>
        set((state) => ({ sessions: state.sessions.map((s) => s.id === sessionId ? { ...s, attachments: [...s.attachments, attachment] } : s) })),
      patchAttachment: (sessionId, name, status) =>
        set((state) => ({ sessions: state.sessions.map((s) => s.id === sessionId ? { ...s, attachments: s.attachments.map((a) => a.name === name ? { ...a, status } : a) } : s) })),
      setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),
      setDetailOpen: (detailOpen) => set({ detailOpen }),
    }),
    {
      name: "agent-console-sessions",
      partialize: (state) => ({ sessions: state.sessions, activeSessionId: state.activeSessionId, detailOpen: state.detailOpen }),
      onRehydrateStorage: () => (state) => {
        if (state && !state.activeSessionId && state.sessions[0]) state.selectSession(state.sessions[0].id);
      },
    },
  ),
);

export function ensureSession(): string {
  const state = useConsoleStore.getState();
  return state.activeSessionId ?? state.createSession();
}
