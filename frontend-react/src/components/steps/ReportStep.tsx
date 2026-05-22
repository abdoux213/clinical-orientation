import { StepPill } from "../Stepper";

type Props = {
  reportText: string | null;
  pdfAvailable: boolean;
  loading: boolean;
  onDownloadMd: () => void;
  onDownloadPdf: () => void;
  onReset: () => void;
  onBackPhysician: () => void;
};

export function ReportStep({
  reportText,
  pdfAvailable,
  loading,
  onDownloadMd,
  onDownloadPdf,
  onReset,
  onBackPhysician,
}: Props) {
  return (
    <section className="screen">
      <StepPill n={4} />
      <h2 className="screen-title">Rapport final</h2>
      <p className="disclaimer-inline">
        <strong>Ce système ne remplace pas une consultation médicale.</strong>
      </p>

      {loading && <p className="muted">Chargement du rapport…</p>}

      {reportText ? (
        <>
          <article className="report-body">{reportText}</article>
          <div className="row">
            <button type="button" className="secondary" onClick={onDownloadMd}>
              Télécharger .md
            </button>
            {pdfAvailable && (
              <button type="button" className="primary" onClick={onDownloadPdf}>
                Télécharger PDF
              </button>
            )}
          </div>
        </>
      ) : (
        !loading && (
          <div className="muted">
            <p>Rapport non encore disponible. Terminez la revue médecin ou réessayez.</p>
            <button type="button" className="secondary" onClick={onBackPhysician}>
              Retour étape médecin
            </button>
          </div>
        )
      )}

      <button type="button" className="primary btn-block new-consult" onClick={onReset}>
        Nouvelle consultation
      </button>
    </section>
  );
}
