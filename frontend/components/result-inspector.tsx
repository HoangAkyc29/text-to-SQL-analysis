"use client";

import { AgGridReact } from "ag-grid-react";
import * as echarts from "echarts";
import { CheckCircle2, ChevronRight, Clock3, Code2, Download, FileBarChart, PanelRightClose, Table2, ThumbsDown, ThumbsUp } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { Badge, Button } from "@/components/ui";
import type { Artifact, ChatResponse, WorkflowStep } from "@/lib/types";
import { api, cn, safeLogValue } from "@/lib/utils";

export function ResultInspector({ response, sessionId, onClose }: { response: ChatResponse; sessionId: string; onClose: () => void }) {
  const [tab, setTab] = useState<"workflow" | "results" | "logs">("workflow");
  return <aside className="hidden h-full w-[430px] shrink-0 flex-col border-l border-[var(--border)] bg-[var(--panel-soft)] xl:flex">
    <div className="flex h-14 items-center justify-between border-b border-[var(--border)] px-4"><div><p className="text-sm font-semibold">Analysis details</p><p className="text-[10px] text-[var(--subtle)]">{response.analysis_id ?? response.trace_id ?? "Current run"}</p></div><Button variant="ghost" size="icon" onClick={onClose} aria-label="Close details"><PanelRightClose className="size-4" /></Button></div>
    <div className="grid grid-cols-3 border-b border-[var(--border)] px-2 pt-2">{(["workflow", "results", "logs"] as const).map((item) => <button key={item} onClick={() => setTab(item)} className={cn("border-b-2 px-2 py-2 text-xs font-semibold capitalize transition", tab === item ? "border-indigo-500 text-indigo-500" : "border-transparent text-[var(--subtle)]")}>{item}</button>)}</div>
    <div className="scrollbar-thin flex-1 overflow-y-auto p-4">{tab === "workflow" && <WorkflowTimeline response={response} />}{tab === "results" && <Results response={response} sessionId={sessionId} />}{tab === "logs" && <SanitizedLogs response={response} />}</div>
  </aside>;
}

function WorkflowTimeline({ response }: { response: ChatResponse }) {
  const steps: WorkflowStep[] = response.steps?.length ? response.steps : inferredSteps(response);
  return <div><div className="mb-5 flex items-center justify-between"><p className="text-xs font-semibold uppercase tracking-wider text-[var(--subtle)]">Agent workflow</p><Badge tone={response.workflow_status === "error" ? "danger" : response.clarification ? "warning" : "success"}>{response.workflow_status ?? "complete"}</Badge></div><div className="relative space-y-0 before:absolute before:bottom-5 before:left-[15px] before:top-5 before:w-px before:bg-[var(--border)]">{steps.map((step, index) => { const done = step.status !== "running" && step.status !== "pending"; return <div className="relative flex gap-3 pb-6" key={step.id ?? step.step_id ?? index}><span className={cn("z-10 grid size-8 shrink-0 place-items-center rounded-full border-4 border-[var(--panel-soft)]", done ? "bg-emerald-500 text-white" : "bg-indigo-500 text-white")} >{done ? <CheckCircle2 className="size-4" /> : <Clock3 className="size-4" />}</span><div className="min-w-0 pt-1"><p className="text-sm font-medium">{step.label ?? humanize(step.type ?? step.step_type ?? `Step ${index + 1}`)}</p><p className="mt-1 text-xs leading-5 text-[var(--subtle)]">{step.message ?? (done ? "Completed successfully" : "In progress")}</p>{step.completed_at && <p className="mt-1 text-[10px] text-[var(--subtle)]">{new Date(step.completed_at).toLocaleTimeString()}</p>}</div></div>; })}</div></div>;
}

function Results({ response, sessionId }: { response: ChatResponse; sessionId: string }) {
  const artifacts = (response.artifacts ?? []).map((item) => typeof item === "string" ? ({ name: item, url: item } satisfies Artifact) : item);
  const tabular = artifacts.find((item) => item.rows?.length) ?? toTabular(response.result);
  const chart = artifacts.find((item) => item.chart)?.chart;
  const [reviewed, setReviewed] = useState<"positive" | "negative" | null>(null);
  const feedback = async (sentiment: "positive" | "negative") => {
    await api("/api/bff/feedback", { method: "POST", body: JSON.stringify({ session_id: sessionId, analysis_id: response.analysis_id ?? "", trace_id: response.trace_id ?? response.analysis_id ?? "", sentiment }) });
    setReviewed(sentiment);
  };
  return <div className="space-y-5">
    {chart && <div><p className="mb-2 flex items-center gap-2 text-sm font-semibold"><FileBarChart className="size-4 text-indigo-500" />Visualization</p><ChartView chart={chart} /></div>}
    {tabular?.rows?.length ? <div><p className="mb-2 flex items-center gap-2 text-sm font-semibold"><Table2 className="size-4 text-indigo-500" />Data preview</p><DataGrid rows={tabular.rows} /></div> : null}
    {artifacts.length > 0 && <div><p className="mb-2 text-sm font-semibold">Artifacts</p><div className="space-y-2">{artifacts.map((artifact, index) => <a className="flex items-center gap-3 rounded-xl border border-[var(--border)] bg-[var(--panel)] p-3 text-sm hover:border-indigo-500/40" key={artifact.artifact_id ?? artifact.name ?? index} href={artifactUrl(artifact, response, sessionId)} download><span className="grid size-8 place-items-center rounded-lg bg-indigo-500/10 text-indigo-500"><Download className="size-4" /></span><span className="min-w-0 flex-1 truncate">{artifact.name ?? artifact.file_name ?? artifact.artifact_id ?? `Artifact ${index + 1}`}</span><ChevronRight className="size-4 text-[var(--subtle)]" /></a>)}</div></div>}
    <div className="rounded-xl border border-[var(--border)] bg-[var(--panel)] p-4"><p className="text-sm font-medium">Was this result useful?</p><div className="mt-3 flex gap-2"><Button variant={reviewed === "positive" ? "primary" : "secondary"} size="sm" onClick={() => void feedback("positive")}><ThumbsUp className="size-3.5" />Helpful</Button><Button variant={reviewed === "negative" ? "danger" : "secondary"} size="sm" onClick={() => void feedback("negative")}><ThumbsDown className="size-3.5" />Needs work</Button></div></div>
  </div>;
}

function DataGrid({ rows }: { rows: Record<string, unknown>[] }) {
  const columnDefs = useMemo(() => Object.keys(rows[0] ?? {}).map((field) => ({ field, headerName: humanize(field), sortable: true, filter: true, resizable: true, flex: 1, minWidth: 110 })), [rows]);
  return <div className="h-64 overflow-hidden rounded-xl border border-[var(--border)]"><AgGridReact rowData={rows.slice(0, 500)} columnDefs={columnDefs} defaultColDef={{ suppressHeaderMenuButton: true }} /></div>;
}

function ChartView({ chart }: { chart: NonNullable<Artifact["chart"]> }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!ref.current) return;
    const instance = echarts.init(ref.current);
    instance.setOption({ backgroundColor: "transparent", tooltip: { trigger: "axis" }, grid: { left: 38, right: 14, top: 28, bottom: 32 }, xAxis: { type: "category", data: chart.x ?? [], axisLabel: { color: "#8791a5" } }, yAxis: { type: "value", axisLabel: { color: "#8791a5" }, splitLine: { lineStyle: { color: "#8791a522" } } }, series: (chart.series ?? []).map((series) => ({ ...series, type: "line", smooth: true, symbolSize: 6, areaStyle: { opacity: .08 } })), color: ["#6c63ff", "#19b5a5", "#f59e0b"] });
    const resize = () => instance.resize();
    window.addEventListener("resize", resize);
    return () => { window.removeEventListener("resize", resize); instance.dispose(); };
  }, [chart]);
  return <div ref={ref} className="h-60 rounded-xl border border-[var(--border)] bg-[var(--panel)]" role="img" aria-label={chart.title ?? "Analysis chart"} />;
}

function SanitizedLogs({ response }: { response: ChatResponse }) {
  return <div><div className="mb-3 flex items-center gap-2"><Code2 className="size-4 text-indigo-500" /><p className="text-sm font-semibold">Sanitized event payload</p></div><p className="mb-3 text-xs leading-5 text-[var(--subtle)]">Secrets and authorization values are removed before display. Hidden model reasoning is never exposed.</p><pre className="scrollbar-thin max-h-[60vh] overflow-auto rounded-xl bg-slate-950 p-4 text-[11px] leading-5 text-slate-300">{safeLogValue({ session_id: response.session_id, workflow_status: response.workflow_status, analysis_id: response.analysis_id, trace_id: response.trace_id, steps: response.steps, error: response.error })}</pre></div>;
}

function inferredSteps(response: ChatResponse): WorkflowStep[] {
  const all = ["Understand request", "Plan analysis", "Review data access", "Run analysis", "Synthesize result"];
  return all.map((label, index) => ({ id: String(index), label, status: response.workflow_status === "error" && index > 1 ? "pending" : "complete" }));
}
function humanize(value: string) { return value.replaceAll("_", " ").replace(/\b\w/g, (char) => char.toUpperCase()); }
function toTabular(result?: Record<string, unknown>): Artifact | undefined {
  if (!result) return undefined;
  const rows = Object.values(result).find((value) => Array.isArray(value) && value.every((item) => typeof item === "object")) as Record<string, unknown>[] | undefined;
  return rows ? { rows } : undefined;
}
function artifactUrl(artifact: Artifact, response: ChatResponse, sessionId: string) {
  const direct = artifact.url ?? artifact.download_url;
  if (direct?.startsWith("/")) return direct.startsWith("/api/") ? direct : `/api/bff${direct}`;
  const trace = response.trace_id ?? response.analysis_id;
  const name = artifact.file_name ?? artifact.name ?? artifact.artifact_id;
  return trace && name
    ? `/api/bff/artifacts/${encodeURIComponent(trace)}/${encodeURIComponent(name)}?session_id=${encodeURIComponent(sessionId)}`
    : "#";
}
