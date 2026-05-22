import type { ConsultationState } from "./types";

/** Même logique que le frontend Streamlit (`infer_step`). */
export function inferStep(threadId: string | null, state: ConsultationState | null): number {
  if (!threadId || !state) return 1;
  const intr = state.interrupt ?? {};
  if (state.final_report) return 4;
  if (state.physician_treatment) return 4;
  if (intr.type === "physician_review") return 3;
  if (state.diagnostic_summary && intr.type !== "patient_question") return 3;
  if (intr.type === "patient_question") return 2;
  const n = state.patient_answers?.length ?? 0;
  if (n < 5) return 2;
  if (state.diagnostic_summary) return 3;
  return 2;
}
