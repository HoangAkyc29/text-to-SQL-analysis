export type User = {
  sub: string;
  role: string;
  display_name?: string;
  store_ids?: number[] | null;
};

export type ClarificationOption = { id: string; label: string; description?: string };
export type ClarificationQuestion = {
  id: string;
  prompt: string;
  type?: "single" | "multiple" | "text";
  options?: ClarificationOption[];
  required?: boolean;
};
export type Clarification = {
  reason?: string;
  questions: ClarificationQuestion[];
};

export type WorkflowStep = {
  id?: string;
  step_id?: string;
  type?: string;
  step_type?: string;
  status?: string;
  label?: string;
  message?: string;
  started_at?: string;
  completed_at?: string;
  metadata?: Record<string, unknown>;
};

export type Artifact = {
  artifact_id?: string;
  file_name?: string;
  name?: string;
  url?: string;
  download_url?: string;
  path?: string;
  mime_type?: string;
  type?: string;
  size?: number;
  rows?: Record<string, unknown>[];
  columns?: string[];
  chart?: { title?: string; x?: string[]; series?: { name: string; data: number[] }[] };
};

export type PendingInteraction = {
  interaction_id: string;
  revision?: number;
  kind?: string;
  request?: Record<string, unknown>;
};

export type AnalysisJob = {
  analysis_id: string;
  session_id: string;
  status: string;
  outcome?: string | null;
  result_message?: string | null;
  progress?: number;
  current_stage?: string | null;
  pending_interaction?: PendingInteraction | null;
  artifacts?: Artifact[];
  legacy_analysis_id?: string | null;
  trace_id?: string | null;
  safe_error?: { code?: string; message?: string; retryable?: boolean } | null;
};

export type AnalysisEvent = {
  event_id?: string;
  analysis_id?: string;
  sequence?: number;
  event_type: string;
  data?: Record<string, unknown>;
};

export type ChatResponse = {
  session_id: string;
  workflow_status?: string;
  message?: string;
  user_message?: string;
  route?: string;
  analysis_id?: string;
  trace_id?: string;
  outcome?: string;
  clarification?: Clarification;
  confirmation?: {
    id?: string;
    prompt?: string;
    message?: string;
    confirm_label?: string;
    cancel_label?: string;
  };
  pending_interaction?: PendingInteraction;
  steps?: WorkflowStep[];
  artifacts?: (Artifact | string)[];
  result?: Record<string, unknown>;
  error?: { code?: string; detail?: string; retryable?: boolean };
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  createdAt: string;
  response?: ChatResponse;
  pending?: boolean;
};

export type Session = {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  messages: ChatMessage[];
  attachments: { name: string; size?: number; status: "uploading" | "ready" | "error" }[];
};

export type DomainRule = {
  rule_id?: string;
  id?: string;
  title?: string;
  statement?: string;
  description?: string;
  status?: "candidate" | "confirmed" | "rejected" | "stale";
  confidence?: number;
  source_trace_id?: string;
  created_at?: string;
};

export type Health = {
  ok: boolean;
  redis?: boolean;
  mongo?: boolean;
  agents?: Record<string, string>;
};
