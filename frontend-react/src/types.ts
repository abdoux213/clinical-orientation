export type InterruptPayload = {
  type?: string;
  question?: string;
  question_index?: number;
  diagnostic_summary?: string;
  interim_care?: string;
  message?: string;
  [key: string]: unknown;
};

export type ConsultationState = {
  patient_case?: string | null;
  question_count?: number;
  current_question?: string | null;
  patient_answers?: string[];
  diagnostic_summary?: string | null;
  interim_care?: string | null;
  physician_treatment?: string | null;
  final_report?: string | null;
  next?: string | null;
  interrupt?: InterruptPayload | null;
  messages?: string[];
};

export type StartConsultationResponse = {
  thread_id: string;
  state: ConsultationState;
};

export type SessionStartResponse = {
  session_id: string;
};

export type ReportResponse = {
  thread_id: string;
  final_report: string;
  disclaimer?: string;
};
