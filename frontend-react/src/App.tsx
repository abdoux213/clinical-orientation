import { useCallback, useEffect, useState } from "react";
import {
  defaultApiBase,
  getConsultation,
  getReport,
  getReportPdf,
  persistApiBase,
  resumeConsultation,
  startConsultation,
  startSession,
  verifyApi,
} from "./api";
import { Sidebar } from "./components/Sidebar";
import { Stepper } from "./components/Stepper";
import { IntakeStep } from "./components/steps/IntakeStep";
import { PhysicianStep } from "./components/steps/PhysicianStep";
import { QuestionsStep } from "./components/steps/QuestionsStep";
import { ReportStep } from "./components/steps/ReportStep";
import { DISCLAIMER, EXAMPLES } from "./constants";
import { inferStep } from "./inferStep";
import type { ConsultationState } from "./types";

export default function App() {
  const [apiBase, setApiBase] = useState(defaultApiBase);
  const [threadId, setThreadId] = useState<string | null>(null);
  const [consultationState, setConsultationState] = useState<ConsultationState | null>(null);
  const [step, setStep] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [healthOk, setHealthOk] = useState<boolean | null>(null);
  const [healthMessage, setHealthMessage] = useState<string | null>(null);

  const [patientCase, setPatientCase] = useState("");
  const [exampleKey, setExampleKey] = useState("");
  const [patientAnswer, setPatientAnswer] = useState("");
  const [physicianText, setPhysicianText] = useState("");

  const [reportText, setReportText] = useState<string | null>(null);
  const [pdfBlob, setPdfBlob] = useState<Blob | null>(null);
  const [reportLoading, setReportLoading] = useState(false);

  const interrupt = consultationState?.interrupt;

  const applyState = useCallback((tid: string | null, st: ConsultationState | null) => {
    setConsultationState(st);
    const s = inferStep(tid, st);
    setStep((prev) => Math.max(prev, s));
  }, []);

  const refreshRemote = useCallback(async () => {
    if (!threadId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getConsultation(apiBase, threadId);
      applyState(threadId, data.state);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }, [apiBase, threadId, applyState]);

  useEffect(() => {
    if (exampleKey && EXAMPLES[exampleKey]) {
      setPatientCase(EXAMPLES[exampleKey]);
    }
  }, [exampleKey]);

  useEffect(() => {
    if (step !== 4 || !threadId) {
      setReportText(null);
      setPdfBlob(null);
      return;
    }
    let cancelled = false;
    setReportLoading(true);
    (async () => {
      try {
        const rep = await getReport(apiBase, threadId);
        if (!cancelled) setReportText(rep.final_report);
      } catch {
        const refreshed = await getConsultation(apiBase, threadId).catch(() => null);
        if (!cancelled && refreshed?.state?.final_report) {
          setReportText(refreshed.state.final_report);
        }
      }
      try {
        const blob = await getReportPdf(apiBase, threadId);
        if (!cancelled) setPdfBlob(blob);
      } catch {
        if (!cancelled) setPdfBlob(null);
      }
      if (!cancelled) setReportLoading(false);
    })();
    return () => {
      cancelled = true;
    };
  }, [step, threadId, apiBase]);

  const handleApiBlur = () => persistApiBase(apiBase);

  const checkApi = async () => {
    const { ok, message } = await verifyApi(apiBase);
    setHealthOk(ok);
    setHealthMessage(message);
  };

  const resetAll = () => {
    setThreadId(null);
    setConsultationState(null);
    setStep(1);
    setError(null);
    setPatientAnswer("");
    setPhysicianText("");
    setReportText(null);
    setPdfBlob(null);
    setPatientCase("");
    setExampleKey("");
  };

  const handleStart = async () => {
    const trimmed = patientCase.trim();
    if (trimmed.length < 10) {
      setError("Veuillez saisir au moins 10 caractères pour le cas patient.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      persistApiBase(apiBase);
      const { session_id } = await startSession(apiBase);
      const result = await startConsultation(apiBase, trimmed, session_id);
      setThreadId(result.thread_id);
      applyState(result.thread_id, result.state);
      setStep(inferStep(result.thread_id, result.state));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  };

  const handlePatientSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!threadId || !patientAnswer.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const result = await resumeConsultation(apiBase, threadId, patientAnswer.trim());
      setPatientAnswer("");
      applyState(threadId, result.state);
      setStep(inferStep(threadId, result.state));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  const handlePhysicianSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!threadId || !physicianText.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const result = await resumeConsultation(apiBase, threadId, {
        physician_treatment: physicianText.trim(),
      });
      setPhysicianText("");
      applyState(threadId, result.state);
      setStep(inferStep(threadId, result.state));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  const downloadMarkdown = () => {
    if (!reportText || !threadId) return;
    const blob = new Blob([reportText], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `rapport_orientation_${threadId.slice(0, 8)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadPdf = () => {
    if (!pdfBlob || !threadId) return;
    const url = URL.createObjectURL(pdfBlob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `rapport_orientation_${threadId.slice(0, 8)}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="app-shell">
      <Sidebar
        apiBase={apiBase}
        onApiBaseChange={setApiBase}
        onApiBlur={handleApiBlur}
        onCheckApi={checkApi}
        healthMessage={healthMessage}
        healthOk={healthOk}
        step={step}
        onReset={resetAll}
      />

      <main className="main">
        <header className="co-hero">
          <h1>Orientation clinique préliminaire</h1>
          <p className="sub">Workflow multi-agents (LangGraph) — exercice pédagogique</p>
        </header>
        <div className="banner">{DISCLAIMER}</div>
        <Stepper current={step} />
        {error && (
          <div className="error" role="alert">
            {error}
          </div>
        )}

        {step === 1 && (
          <IntakeStep
            patientCase={patientCase}
            exampleKey={exampleKey}
            loading={loading}
            onPatientCaseChange={setPatientCase}
            onExampleChange={setExampleKey}
            onStart={handleStart}
          />
        )}
        {step === 2 && (
          <QuestionsStep
            state={consultationState}
            threadId={threadId}
            interrupt={interrupt}
            patientAnswer={patientAnswer}
            loading={loading}
            onPatientAnswerChange={setPatientAnswer}
            onSubmit={handlePatientSubmit}
            onRefresh={refreshRemote}
            onContinuePhysician={() => setStep(3)}
          />
        )}
        {step === 3 && (
          <PhysicianStep
            state={consultationState}
            interrupt={interrupt}
            physicianText={physicianText}
            loading={loading}
            onPhysicianTextChange={setPhysicianText}
            onSubmit={handlePhysicianSubmit}
            onGoToReport={() => setStep(4)}
          />
        )}
        {step === 4 && (
          <ReportStep
            reportText={reportText}
            pdfAvailable={pdfBlob != null}
            loading={reportLoading}
            onDownloadMd={downloadMarkdown}
            onDownloadPdf={downloadPdf}
            onReset={resetAll}
            onBackPhysician={() => setStep(3)}
          />
        )}
      </main>
    </div>
  );
}
