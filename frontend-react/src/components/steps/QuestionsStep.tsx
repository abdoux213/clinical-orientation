import type { ConsultationState, InterruptPayload } from "../../types";
import { StepPill } from "../Stepper";

type Props = {
  state: ConsultationState | null;
  threadId: string | null;
  interrupt: InterruptPayload | null | undefined;
  patientAnswer: string;
  loading: boolean;
  onPatientAnswerChange: (v: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  onRefresh: () => void;
  onContinuePhysician: () => void;
};

export function QuestionsStep({
  state,
  threadId,
  interrupt,
  patientAnswer,
  loading,
  onPatientAnswerChange,
  onSubmit,
  onRefresh,
  onContinuePhysician,
}: Props) {
  const nAns = state?.patient_answers?.length ?? 0;
  const pct = Math.min(nAns / 5, 1) * 100;

  return (
    <section className="screen">
      <StepPill n={2} />
      <h2 className="screen-title">Questions au patient</h2>
      <button type="button" className="secondary" onClick={onRefresh}>
        Actualiser l’état
      </button>
      <div className="metrics">
        <div className="metric">
          <span className="metric-label">Questions</span>
          <span className="metric-value">{nAns} / 5</span>
        </div>
        <div className="metric">
          <span className="metric-label">Statut</span>
          <span className="metric-value">{nAns < 5 ? "En cours" : "Terminé"}</span>
        </div>
        <div className="metric">
          <span className="metric-label">Thread</span>
          <span className="metric-value">{threadId ? `${threadId.slice(0, 8)}…` : "—"}</span>
        </div>
      </div>
      <div className="progress-bar" role="progressbar" aria-valuenow={nAns} aria-valuemin={0} aria-valuemax={5}>
        <div className="progress-fill" style={{ width: `${pct}%` }} />
        <span className="progress-label">{nAns} réponse(s) sur 5</span>
      </div>
      {state?.patient_answers && state.patient_answers.length > 0 && (
        <details className="history">
          <summary>Historique des réponses</summary>
          <ol>
            {state.patient_answers.map((a, i) => (
              <li key={i}>{a}</li>
            ))}
          </ol>
        </details>
      )}
      {interrupt?.type === "patient_question" && (
        <form onSubmit={onSubmit}>
          <p className="form-label">Question de l’agent diagnostic</p>
          <div className="question-card">{String(interrupt.question ?? "")}</div>
          <textarea
            value={patientAnswer}
            onChange={(e) => onPatientAnswerChange(e.target.value)}
            placeholder="Réponse du patient"
            rows={4}
          />
          <button type="submit" className="primary btn-block" disabled={loading || !patientAnswer.trim()}>
            {loading ? "Envoi…" : "Envoyer la réponse"}
          </button>
        </form>
      )}
      {interrupt?.type !== "patient_question" && state?.diagnostic_summary && (
        <>
          <div className="success">Les 5 questions sont terminées. Passez à la revue médecin.</div>
          <button type="button" className="primary btn-block" onClick={onContinuePhysician}>
            Continuer vers la revue médecin →
          </button>
        </>
      )}
      {interrupt?.type !== "patient_question" && !state?.diagnostic_summary && (
        <div className="warning">
          Aucune question en attente. Vérifiez que l’API tourne ou actualisez l’état.
        </div>
      )}
    </section>
  );
}
