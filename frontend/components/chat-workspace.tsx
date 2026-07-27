"use client";

import { motion } from "framer-motion";
import {
  AlertCircle,
  Bot,
  Check,
  Download,
  File,
  LoaderCircle,
  Paperclip,
  RotateCcw,
  Send,
  Sparkles,
  Square,
  UserRound,
  X,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { ResultInspector } from "@/components/result-inspector";
import { Badge, Button, Card, Textarea } from "@/components/ui";
import { ensureSession, useConsoleStore } from "@/lib/store";
import type {
  AnalysisEvent,
  AnalysisJob,
  Artifact,
  ChatMessage,
  ChatResponse,
  ClarificationQuestion,
  WorkflowStep,
} from "@/lib/types";
import { api, cn } from "@/lib/utils";

const suggestions = [
  "Summarize recent performance and highlight anomalies",
  "Compare key trends across the available periods",
  "Create an executive-ready chart with key findings",
];

type StreamState = {
  analysisId: string;
  assistantId: string;
  sessionId: string;
  steps: WorkflowStep[];
  message: string;
};

export function ChatWorkspace() {
  const sessions = useConsoleStore((s) => s.sessions);
  const activeId = useConsoleStore((s) => s.activeSessionId);
  const detailOpen = useConsoleStore((s) => s.detailOpen);
  const { addMessage, patchMessage, addAttachment, patchAttachment, setDetailOpen } =
    useConsoleStore();
  const session = sessions.find((item) => item.id === activeId);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const abortRef = useRef<AbortController | null>(null);
  const streamRef = useRef<EventSource | null>(null);
  const streamState = useRef<StreamState | null>(null);
  const latestResponse = [...(session?.messages ?? [])]
    .reverse()
    .find((item) => item.response)?.response;

  useEffect(() => {
    return () => {
      streamRef.current?.close();
      abortRef.current?.abort();
    };
  }, []);

  const finishAssistant = (
    sessionId: string,
    assistantId: string,
    response: ChatResponse,
    content: string,
  ) => {
    patchMessage(sessionId, assistantId, {
      pending: false,
      content,
      response,
    });
    if (response.artifacts?.length || response.steps?.length || response.result) {
      setDetailOpen(true);
    }
    setBusy(false);
    streamRef.current?.close();
    streamRef.current = null;
    streamState.current = null;
    abortRef.current = null;
  };

  const openEventStream = (sessionId: string, assistantId: string, analysisId: string) => {
    streamRef.current?.close();
    streamState.current = {
      analysisId,
      assistantId,
      sessionId,
      steps: [],
      message: "Agents are working…",
    };
    const source = new EventSource(`/api/bff/analyses/${encodeURIComponent(analysisId)}/events`);
    streamRef.current = source;

    const onPayload = async (event: MessageEvent, eventTypeHint?: string) => {
      let payload: AnalysisEvent;
      try {
        payload = JSON.parse(String(event.data)) as AnalysisEvent;
      } catch {
        return;
      }
      const eventType = String(payload.event_type || eventTypeHint || "progress");
      const data = (payload.data ?? {}) as Record<string, unknown>;
      const state = streamState.current;
      if (!state) return;

      if (eventType === "progress" || eventType === "stage_completed" || eventType === "agent_action") {
        const step: WorkflowStep = {
          id: String(payload.sequence ?? crypto.randomUUID()),
          type: eventType,
          label: String(data.stage ?? data.message ?? eventType),
          message: String(data.message ?? data.status ?? ""),
          status: "running",
        };
        state.steps = [...state.steps, step];
        state.message = step.label || state.message;
        patchMessage(sessionId, assistantId, {
          pending: true,
          content: state.message,
          response: {
            session_id: sessionId,
            analysis_id: analysisId,
            workflow_status: "running",
            steps: state.steps,
          },
        });
        return;
      }

      if (eventType === "interaction_requested") {
        const request = (data.request as Record<string, unknown> | undefined) ?? {};
        const questions = (request.questions as ClarificationQuestion[] | undefined) ?? [];
        finishAssistant(
          sessionId,
          assistantId,
          {
            session_id: sessionId,
            analysis_id: analysisId,
            workflow_status: "awaiting_clarification",
            message: String(data.prompt ?? "Your input is needed to continue."),
            clarification: {
              reason: String(request.reason ?? ""),
              questions,
            },
            pending_interaction: {
              interaction_id: String(data.interaction_id ?? ""),
              revision: Number(data.revision ?? 1),
              kind: String(data.kind ?? "clarification"),
              request,
            },
            steps: state.steps,
          },
          String(data.prompt ?? "Your input is needed to continue."),
        );
        return;
      }

      if (eventType === "artifact_created") {
        return;
      }

      if (eventType === "completed" || eventType === "failed" || eventType === "cancelled") {
        const job = await api<AnalysisJob>(`/api/bff/analyses/${encodeURIComponent(analysisId)}`);
        const content =
          job.result_message ||
          (typeof data.message === "string" ? data.message : null) ||
          (eventType === "completed"
            ? "Analysis complete."
            : eventType === "cancelled"
              ? "Analysis cancelled."
              : "The analysis could not be completed.");
        const artifacts = (job.artifacts ?? []).map((item) => ({
          ...item,
          url: item.url ?? item.download_url,
          file_name: item.file_name ?? item.name,
        }));
        finishAssistant(
          sessionId,
          assistantId,
          {
            session_id: sessionId,
            analysis_id: analysisId,
            trace_id: job.trace_id ?? job.legacy_analysis_id ?? undefined,
            workflow_status: job.status,
            outcome: job.outcome ?? undefined,
            message: content,
            artifacts,
            steps: state.steps,
            error:
              eventType === "failed"
                ? {
                    code: job.safe_error?.code ?? "ANALYSIS_FAILED",
                    detail: job.safe_error?.message ?? "Analysis failed",
                    retryable: Boolean(job.safe_error?.retryable),
                  }
                : undefined,
          },
          content,
        );
      }
    };

    [
      "queued",
      "started",
      "progress",
      "stage_completed",
      "agent_action",
      "interaction_requested",
      "interaction_answered",
      "artifact_created",
      "warning",
      "completed",
      "failed",
      "cancelled",
      "retry_scheduled",
      "message",
    ].forEach((name) => {
      source.addEventListener(name, (event) => {
        void onPayload(event as MessageEvent, name);
      });
    });
    source.onerror = () => {
      if (!streamState.current) return;
      finishAssistant(
        sessionId,
        assistantId,
        {
          session_id: sessionId,
          analysis_id: analysisId,
          workflow_status: "error",
          error: { code: "SSE_DISCONNECTED", detail: "Live updates disconnected.", retryable: true },
          steps: streamState.current.steps,
        },
        "Live updates disconnected. You can retry the request.",
      );
    };
  };

  const send = async (content = draft) => {
    const text = content.trim();
    if (!text || busy) return;

    // Resume pending clarification via /interactions — do not start a new analysis.
    const pendingAssistant = [...(session?.messages ?? [])]
      .reverse()
      .find(
        (item) =>
          item.response?.pending_interaction?.interaction_id &&
          (item.response.workflow_status === "awaiting_clarification" ||
            item.response.workflow_status === "awaiting_interaction" ||
            Boolean(item.response.clarification)),
      );
    if (pendingAssistant?.response) {
      const questions = pendingAssistant.response.clarification?.questions ?? [];
      const question =
        questions[0] ??
        ({
          id: "open_clarify",
          prompt: pendingAssistant.content || "Clarification",
        } as ClarificationQuestion);
      setDraft("");
      await clarify(question, text, pendingAssistant.response);
      return;
    }

    const sessionId = activeId ?? ensureSession();
    setDraft("");
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
      createdAt: new Date().toISOString(),
    };
    const assistantId = crypto.randomUUID();
    addMessage(sessionId, userMessage);
    addMessage(sessionId, {
      id: assistantId,
      role: "assistant",
      content: "",
      createdAt: new Date().toISOString(),
      pending: true,
    });
    setBusy(true);
    abortRef.current = new AbortController();
    try {
      await api("/api/bff/sessions", {
        method: "POST",
        body: JSON.stringify({ session_id: sessionId, title: text.slice(0, 80) }),
        signal: abortRef.current.signal,
      }).catch(() => undefined);
      const job = await api<AnalysisJob & { created?: boolean }>("/api/bff/analyses", {
        method: "POST",
        headers: { "Idempotency-Key": crypto.randomUUID() },
        body: JSON.stringify({ session_id: sessionId, message: text }),
        signal: abortRef.current.signal,
      });
      patchMessage(sessionId, assistantId, {
        pending: true,
        content: "Queued for analysis…",
        response: {
          session_id: sessionId,
          analysis_id: job.analysis_id,
          workflow_status: job.status,
        },
      });
      openEventStream(sessionId, assistantId, job.analysis_id);
    } catch (error) {
      const cancelled = error instanceof DOMException && error.name === "AbortError";
      finishAssistant(
        sessionId,
        assistantId,
        {
          session_id: sessionId,
          workflow_status: "error",
          error: {
            detail: error instanceof Error ? error.message : "unknown_error",
            retryable: true,
          },
        },
        cancelled ? "Request cancelled." : "I couldn’t complete that request. You can retry or rephrase.",
      );
    }
  };

  const clarify = async (question: ClarificationQuestion, value: string, response?: ChatResponse) => {
    if (!activeId || busy) return;
    const pending = response?.pending_interaction;
    const analysisId = response?.analysis_id;
    if (!pending?.interaction_id || !analysisId) {
      return;
    }
    setBusy(true);
    const assistantId = crypto.randomUUID();
    addMessage(activeId, {
      id: crypto.randomUUID(),
      role: "user",
      content: value,
      createdAt: new Date().toISOString(),
    });
    addMessage(activeId, {
      id: assistantId,
      role: "assistant",
      content: "",
      createdAt: new Date().toISOString(),
      pending: true,
    });
    try {
      if (value === "cancel") {
        await api(`/api/bff/analyses/${encodeURIComponent(analysisId)}/cancel`, {
          method: "POST",
          body: "{}",
        });
      } else if (value === "rephrase") {
        const job = await api<AnalysisJob>(`/api/bff/analyses/${encodeURIComponent(analysisId)}/rephrase`, {
          method: "POST",
          headers: { "Idempotency-Key": crypto.randomUUID() },
          body: JSON.stringify({ message: question.prompt }),
        });
        openEventStream(activeId, assistantId, job.analysis_id);
        return;
      } else {
        await api(`/api/bff/analyses/${encodeURIComponent(analysisId)}/interactions`, {
          method: "POST",
          body: JSON.stringify({
            interaction_id: pending.interaction_id,
            expected_revision: pending.revision ?? 1,
            idempotency_key: crypto.randomUUID(),
            response: {
              answers: [
                {
                  question_id: question.id,
                  selected_option_id: question.options?.some((option) => option.id === value)
                    ? value
                    : "other",
                  other_text: question.options?.some((option) => option.id === value)
                    ? undefined
                    : value,
                  evidence: value,
                },
              ],
            },
          }),
        });
      }
      openEventStream(activeId, assistantId, analysisId);
    } catch (error) {
      finishAssistant(
        activeId,
        assistantId,
        {
          session_id: activeId,
          analysis_id: analysisId,
          workflow_status: "error",
          error: {
            detail: error instanceof Error ? error.message : "clarification_failed",
          },
        },
        "That response could not be applied. Please try again.",
      );
    }
  };

  const cancelActive = async () => {
    const analysisId = streamState.current?.analysisId;
    abortRef.current?.abort();
    streamRef.current?.close();
    if (analysisId) {
      await api(`/api/bff/analyses/${encodeURIComponent(analysisId)}/cancel`, {
        method: "POST",
        body: "{}",
      }).catch(() => undefined);
    }
    if (streamState.current) {
      finishAssistant(
        streamState.current.sessionId,
        streamState.current.assistantId,
        {
          session_id: streamState.current.sessionId,
          analysis_id: analysisId,
          workflow_status: "cancelled",
          message: "Cancellation requested.",
          steps: streamState.current.steps,
        },
        "Cancellation requested.",
      );
    } else {
      setBusy(false);
    }
  };

  const upload = async (file: File) => {
    const sessionId = activeId ?? ensureSession();
    addAttachment(sessionId, { name: file.name, size: file.size, status: "uploading" });
    const body = new FormData();
    body.set("file", file);
    try {
      await api(`/api/bff/attachments?session_id=${encodeURIComponent(sessionId)}`, {
        method: "POST",
        body,
      });
      patchAttachment(sessionId, file.name, "ready");
    } catch {
      patchAttachment(sessionId, file.name, "error");
    }
  };

  return (
    <div className="flex h-full min-h-0">
      <section className="flex min-w-0 flex-1 flex-col">
        <div className="scrollbar-thin flex-1 overflow-y-auto px-4 py-6 sm:px-7">
          {!session?.messages.length ? (
            <EmptyState onSelect={setDraft} />
          ) : (
            <div className="mx-auto max-w-3xl space-y-6">
              {session.messages.map((message) => (
                <MessageBubble
                  key={message.id}
                  message={message}
                  sessionId={session.id}
                  onClarify={(question, value) =>
                    void clarify(question, value, message.response)
                  }
                  onRetry={() =>
                    void send(
                      [...session.messages].reverse().find((item) => item.role === "user")
                        ?.content ?? "",
                    )
                  }
                />
              ))}
            </div>
          )}
        </div>
        <div className="shrink-0 border-t border-[var(--border)] bg-[color-mix(in_srgb,var(--panel)_88%,transparent)] p-3 backdrop-blur-xl sm:p-5">
          <div className="mx-auto max-w-3xl">
            {session?.attachments.length ? (
              <div className="mb-2 flex flex-wrap gap-2">
                {session.attachments.map((attachment) => (
                  <Badge
                    key={attachment.name}
                    tone={
                      attachment.status === "ready"
                        ? "success"
                        : attachment.status === "error"
                          ? "danger"
                          : "accent"
                    }
                  >
                    <File className="mr-1 size-3" />
                    {attachment.name}
                    {attachment.status === "uploading" && (
                      <LoaderCircle className="ml-1 size-3 animate-spin" />
                    )}
                  </Badge>
                ))}
              </div>
            ) : null}
            <div className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-2 shadow-lg shadow-slate-900/5 focus-within:border-indigo-500/50">
              <Textarea
                className="min-h-14 border-0 bg-transparent p-2 shadow-none focus:ring-0"
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();
                    void send();
                  }
                }}
                placeholder="Ask the agent to analyze, compare, explain, or visualize…"
                aria-label="Message"
              />
              <div className="flex items-center justify-between">
                <div>
                  <input
                    ref={fileRef}
                    type="file"
                    className="hidden"
                    accept=".csv,.xlsx,.xls,.pdf,.txt,.json,.parquet"
                    onChange={(event) => {
                      const file = event.target.files?.[0];
                      if (file) void upload(file);
                      event.currentTarget.value = "";
                    }}
                  />
                  <Button
                    size="icon"
                    variant="ghost"
                    onClick={() => fileRef.current?.click()}
                    aria-label="Attach a file"
                  >
                    <Paperclip className="size-4" />
                  </Button>
                </div>
                {busy ? (
                  <Button variant="danger" onClick={() => void cancelActive()}>
                    <Square className="size-3 fill-current" />
                    Cancel
                  </Button>
                ) : (
                  <Button onClick={() => void send()} disabled={!draft.trim()}>
                    <Send className="size-4" />
                    Send
                  </Button>
                )}
              </div>
            </div>
            <p className="mt-2 text-center text-[10px] text-[var(--subtle)]">
              Agent output can be incomplete. Review decisions and artifacts before acting.
            </p>
          </div>
        </div>
      </section>
      {detailOpen && latestResponse && (
        <ResultInspector
          response={latestResponse}
          sessionId={activeId ?? ""}
          onClose={() => setDetailOpen(false)}
        />
      )}
    </div>
  );
}

function EmptyState({ onSelect }: { onSelect: (value: string) => void }) {
  return (
    <motion.div
      className="mx-auto flex h-full max-w-2xl flex-col items-center justify-center py-16 text-center"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="relative mb-6">
        <div className="absolute inset-0 rounded-3xl bg-indigo-500/30 blur-2xl" />
        <div className="relative grid size-16 place-items-center rounded-3xl bg-gradient-to-br from-indigo-500 to-violet-600 text-white shadow-xl">
          <Sparkles className="size-7" />
        </div>
      </div>
      <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">
        What would you like to understand?
      </h2>
      <p className="mt-3 max-w-lg text-sm leading-6 text-[var(--subtle)]">
        Describe your goal in plain language. The agent will plan the work, ask for decisions when
        needed, and return reviewable results.
      </p>
      <div className="mt-8 grid w-full gap-3 sm:grid-cols-3">
        {suggestions.map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => onSelect(suggestion)}
            className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-4 text-left text-sm leading-5 shadow-sm transition hover:-translate-y-1 hover:border-indigo-500/40 hover:shadow-lg"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </motion.div>
  );
}

function MessageBubble({
  message,
  sessionId,
  onClarify,
  onRetry,
}: {
  message: ChatMessage;
  sessionId: string;
  onClarify: (question: ClarificationQuestion, value: string) => void;
  onRetry: () => void;
}) {
  const isUser = message.role === "user";
  const confirmation = message.response?.confirmation;
  return (
    <motion.article
      className={cn("flex gap-3", isUser && "flex-row-reverse")}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <span
        className={cn(
          "grid size-8 shrink-0 place-items-center rounded-xl",
          isUser ? "bg-[var(--muted)]" : "bg-indigo-500/10 text-indigo-500",
        )}
      >
        {isUser ? <UserRound className="size-4" /> : <Bot className="size-4" />}
      </span>
      <div className={cn("max-w-[88%]", isUser && "text-right")}>
        <div
          className={cn(
            "inline-block rounded-2xl px-4 py-3 text-left text-sm leading-6",
            isUser ? "bg-[var(--accent)] text-white" : "border border-[var(--border)] bg-[var(--panel)]",
          )}
        >
          {message.pending ? (
            <span className="flex items-center gap-2 text-[var(--subtle)]">
              <LoaderCircle className="size-4 animate-spin" />
              {message.content || "Agents are working…"}
            </span>
          ) : (
            message.content
          )}
        </div>
        {!!message.response?.artifacts?.length && (
          <div className="mt-2 flex flex-wrap gap-2 text-left">
            {message.response.artifacts.map((raw, index) => {
              const artifact = typeof raw === "string" ? { name: raw, url: raw } : raw;
              const href = artifactDownloadHref(artifact, message.response!, sessionId);
              const label =
                artifact.name ?? artifact.file_name ?? artifact.artifact_id ?? `Artifact ${index + 1}`;
              return (
                <a
                  key={`${label}-${index}`}
                  href={href}
                  download
                  className="inline-flex items-center gap-2 rounded-xl border border-[var(--border)] bg-[var(--panel)] px-3 py-2 text-xs font-medium hover:border-indigo-500/40"
                >
                  <Download className="size-3.5 text-indigo-500" />
                  {label}
                </a>
              );
            })}
          </div>
        )}
        {message.response?.error && (
          <Card className="mt-2 flex items-start gap-3 border-red-500/20 p-3 text-left">
            <AlertCircle className="mt-0.5 size-4 shrink-0 text-red-500" />
            <div className="text-xs">
              <p className="font-medium text-red-500">
                {message.response.error.code ?? "Request failed"}
              </p>
              <p className="mt-1 text-[var(--subtle)]">{message.response.error.detail}</p>
              {message.response.error.retryable && (
                <Button className="mt-2" size="sm" variant="secondary" onClick={onRetry}>
                  <RotateCcw className="size-3" />
                  Retry
                </Button>
              )}
            </div>
          </Card>
        )}
        {message.response?.clarification?.questions.map((question) => (
          <ClarificationCard
            key={question.id}
            question={question}
            onSelect={(value) => onClarify(question, value)}
          />
        ))}
        {confirmation && (
          <ClarificationCard
            question={{
              id: confirmation.id ?? "confirmation",
              prompt:
                confirmation.prompt ??
                confirmation.message ??
                "Continue with this action?",
              options: [
                {
                  id: "confirm",
                  label: confirmation.confirm_label ?? "Confirm and continue",
                },
                { id: "cancel", label: confirmation.cancel_label ?? "Cancel" },
                { id: "rephrase", label: "Rephrase request" },
              ],
            }}
            onSelect={(value) =>
              onClarify(
                {
                  id: confirmation.id ?? "confirmation",
                  prompt: confirmation.prompt ?? "Confirm action",
                },
                value,
              )
            }
          />
        )}
      </div>
    </motion.article>
  );
}

function ClarificationCard({
  question,
  onSelect,
}: {
  question: ClarificationQuestion;
  onSelect: (value: string) => void;
}) {
  const [custom, setCustom] = useState("");
  return (
    <Card className="mt-3 max-w-xl p-4 text-left">
      <div className="flex items-start gap-2">
        <span className="mt-0.5 grid size-6 place-items-center rounded-lg bg-amber-500/10 text-amber-500">
          <AlertCircle className="size-3.5" />
        </span>
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-amber-500">
            Your input is needed
          </p>
          <p className="mt-1 text-sm font-medium">{question.prompt}</p>
        </div>
      </div>
      {question.options?.length ? (
        <div className="mt-3 grid gap-2">
          {question.options.map((option) => (
            <button
              key={option.id}
              className="group flex items-center gap-3 rounded-xl border border-[var(--border)] p-3 text-left text-sm hover:border-indigo-500/50 hover:bg-indigo-500/5"
              onClick={() => onSelect(option.id)}
            >
              <span className="grid size-5 place-items-center rounded-full border border-[var(--border)] group-hover:border-indigo-500">
                <Check className="size-3 opacity-0 group-hover:opacity-100" />
              </span>
              <span>
                <span className="font-medium">{option.label}</span>
                {option.description && (
                  <span className="block text-xs text-[var(--subtle)]">{option.description}</span>
                )}
              </span>
            </button>
          ))}
        </div>
      ) : (
        <div className="mt-3 flex gap-2">
          <Textarea
            className="min-h-10"
            value={custom}
            onChange={(event) => setCustom(event.target.value)}
            placeholder="Add context or rephrase…"
          />
          <Button onClick={() => onSelect(custom)} disabled={!custom.trim()}>
            Continue
          </Button>
        </div>
      )}
      <div className="mt-3 flex justify-end">
        <Button size="sm" variant="ghost" onClick={() => onSelect("cancel")}>
          <X className="size-3" />
          Cancel request
        </Button>
      </div>
    </Card>
  );
}

function artifactDownloadHref(artifact: Artifact, response: ChatResponse, sessionId: string) {
  const direct = artifact.url ?? artifact.download_url;
  if (direct?.startsWith("/")) {
    return direct.startsWith("/api/") ? direct : `/api/bff${direct}`;
  }
  const trace = response.trace_id ?? response.analysis_id;
  const name = artifact.file_name ?? artifact.name ?? artifact.artifact_id;
  if (!trace || !name) return "#";
  return `/api/bff/artifacts/${encodeURIComponent(trace)}/${encodeURIComponent(name)}?session_id=${encodeURIComponent(sessionId)}`;
}
