import { EXAMPLES } from "../../constants";
import { StepPill } from "../Stepper";

type Props = {
  patientCase: string;
  exampleKey: string;
  loading: boolean;
  onPatientCaseChange: (v: string) => void;
  onExampleChange: (k: string) => void;
  onStart: () => void;
};

export function IntakeStep({
  patientCase,
  exampleKey,
  loading,
  onPatientCaseChange,
  onExampleChange,
  onStart,
}: Props) {
  return (
    <section className="screen">
      <StepPill n={1} />
      <h2 className="screen-title">Cas initial patient</h2>
      <div className="co-card">
        Décrivez le motif d’orientation clinique préliminaire (symptômes, durée, contexte).{" "}
        <strong>Minimum 10 caractères.</strong>
      </div>
      <div className="field-row">
        <label htmlFor="ex">Exemple pédagogique</label>
        <select id="ex" value={exampleKey} onChange={(e) => onExampleChange(e.target.value)}>
          <option value="">—</option>
          {Object.keys(EXAMPLES).map((k) => (
            <option key={k} value={k}>
              {k}
            </option>
          ))}
        </select>
      </div>
      <textarea
        value={patientCase}
        onChange={(e) => onPatientCaseChange(e.target.value)}
        placeholder="Ex. : Toux sèche depuis 3 jours, fatigue légère…"
        rows={8}
        aria-label="Description du cas patient"
      />
      <button type="button" className="primary btn-block" disabled={loading} onClick={onStart}>
        {loading ? "Démarrage…" : "Démarrer la consultation"}
      </button>
    </section>
  );
}
