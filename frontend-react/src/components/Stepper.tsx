import { STEP_LABELS } from "../constants";

type Props = { current: number };

export function Stepper({ current }: Props) {
  return (
    <ul className="co-stepper" aria-label="Étapes du parcours">
      {STEP_LABELS.map((s, i) => {
        const n = i + 1;
        const cls = n === current ? "current" : n < current ? "done" : "";
        return (
          <li key={s.short} className={cls}>
            {n}. {s.short}
          </li>
        );
      })}
    </ul>
  );
}

export function StepPill({ n }: { n: number }) {
  return <span className="step-pill">Étape {n} / 4</span>;
}
