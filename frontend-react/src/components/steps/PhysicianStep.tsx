import type { ConsultationState, InterruptPayload } from "../../types";
import { StepPill } from "../Stepper";

type Props = {
  state: ConsultationState | null;
  interrupt: InterruptPayload | null | undefined;
  physicianText: string;
  loading: boolean;
  onPhysicianTextChange: (v: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  onGoToReport: () => void;
};

export function PhysicianStep({
  state,
  interrupt,
  physicianText,
  loading,
  onPhysicianTextChange,
  onSubmit,
  onGoToReport,
}: Props) {
  const hasTreatment = Boolean(state?.physician_treatment);
  const hasReport = Boolean(state?.final_report);

  return (
    <section className="screen">
      <StepPill n={3} />
      <h2 className="screen-title">Revue du médecin traitant</h2>
      <p className="muted">Human-in-the-loop — validation humaine avant le rapport final.</p>

      {interrupt?.type === "physician_review" && interrupt.message && (
        <div className="info">{String(interrupt.message)}</div>
      )}

      <div className="two-col">
        <div className="panel">
          <h3>Synthèse clinique préliminaire</h3>
          <p>{state?.diagnostic_summary ?? "—"}</p>
        </div>
        <div className="panel">
          <h3>Recommandation intermédiaire</h3>
          <p>{state?.interim_care ?? "—"}</p>
        </div>
      </div>

      {hasTreatment && !hasReport && (
        <div className="warning">
          <p>Conduite enregistrée. Si le rapport n’apparaît pas, passez à l’étape suivante.</p>
          <button type="button" className="primary btn-block" onClick={onGoToReport}>
            Poursuivre vers le rapport
          </button>
        </div>
      )}

      {hasTreatment && hasReport && (
        <button type="button" className="primary btn-block" onClick={onGoToReport}>
          Voir le rapport final
        </button>
      )}

      {!hasTreatment && (
        <form onSubmit={onSubmit} className="physician-form">
          <label htmlFor="phy">Traitement ou conduite à tenir (avis du médecin)</label>
          <textarea
            id="phy"
            value={physicianText}
            onChange={(e) => onPhysicianTextChange(e.target.value)}
            placeholder="Ex. : surveillance à domicile, consultation si aggravation…"
            rows={5}
          />
          <button type="submit" className="primary btn-block" disabled={loading || !physicianText.trim()}>
            {loading ? "Génération…" : "Valider et générer le rapport"}
          </button>
        </form>
      )}
    </section>
  );
}
