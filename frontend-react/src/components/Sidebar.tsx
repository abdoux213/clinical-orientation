import { STEP_LABELS } from "../constants";

type Props = {
  apiBase: string;
  onApiBaseChange: (v: string) => void;
  onApiBlur: () => void;
  onCheckApi: () => void;
  healthMessage: string | null;
  healthOk: boolean | null;
  step: number;
  onReset: () => void;
};

export function Sidebar({
  apiBase,
  onApiBaseChange,
  onApiBlur,
  onCheckApi,
  healthMessage,
  healthOk,
  step,
  onReset,
}: Props) {
  return (
    <aside className="sidebar">
      <p className="sidebar-brand" aria-hidden>
        🩺
      </p>
      <h2>Console</h2>
      <label htmlFor="api-url">URL de l’API</label>
      <input
        id="api-url"
        type="text"
        value={apiBase}
        onChange={(e) => onApiBaseChange(e.target.value.replace(/\/$/, ""))}
        onBlur={onApiBlur}
        autoComplete="off"
      />
      <button type="button" className="secondary btn-block" onClick={onCheckApi}>
        Tester l’API
      </button>
      {healthMessage != null && (
        <p className={healthOk ? "health-ok" : "health-err"} role="status">
          {healthMessage}
        </p>
      )}
      <StepsNav step={step} />
      <button type="button" className="secondary btn-block" onClick={onReset}>
        Nouvelle consultation
      </button>
      <p className="muted sidebar-hint">
        Build : <code>VITE_API_URL</code>
      </p>
    </aside>
  );
}

function StepsNav({ step }: { step: number }) {
  return (
    <nav className="steps-nav" aria-label="Étapes">
      <h2>Parcours</h2>
      <ul>
        {STEP_LABELS.map((s, i) => {
          const n = i + 1;
          return (
            <li key={s.full} className={step === n ? "active" : n < step ? "done" : ""}>
              {step === n && "→ "}
              {n < step && "✓ "}
              {s.full}
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
