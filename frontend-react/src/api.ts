import type {
  ConsultationState,
  ReportResponse,
  SessionStartResponse,
  StartConsultationResponse,
} from "./types";

const LS_API = "clinical-orientation-api-base";

export function defaultApiBase(): string {
  const fromEnv = import.meta.env.VITE_API_URL?.replace(/\/$/, "");
  if (fromEnv) return fromEnv;
  try {
    const stored = localStorage.getItem(LS_API);
    if (stored) return stored.replace(/\/$/, "");
  } catch {
    /* ignore */
  }
  return "http://127.0.0.1:8000";
}

export function persistApiBase(url: string): void {
  try {
    localStorage.setItem(LS_API, url.replace(/\/$/, ""));
  } catch {
    /* ignore */
  }
}

async function parseError(res: Response): Promise<string> {
  const t = await res.text();
  try {
    const j = JSON.parse(t) as { detail?: unknown };
    if (Array.isArray(j.detail)) {
      const parts = j.detail
        .map((item) => {
          if (item && typeof item === "object" && "msg" in item) {
            const loc = Array.isArray((item as { loc?: unknown[] }).loc)
              ? (item as { loc: unknown[] }).loc.filter((x) => x !== "body").join(".")
              : "";
            return loc ? `${loc}: ${(item as { msg: string }).msg}` : (item as { msg: string }).msg;
          }
          return String(item);
        })
        .filter(Boolean);
      if (parts.length) return parts.join(" ; ");
    }
    if (j.detail != null) return String(j.detail);
  } catch {
    /* ignore */
  }
  return t || res.statusText;
}

export async function apiGet<T>(base: string, path: string): Promise<T> {
  const res = await fetch(`${base.replace(/\/$/, "")}${path}`, {
    headers: { Accept: "application/json" },
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json() as Promise<T>;
}

export async function apiPost<T>(base: string, path: string, body: unknown): Promise<T> {
  const res = await fetch(`${base.replace(/\/$/, "")}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json() as Promise<T>;
}

export async function verifyApi(base: string): Promise<{ ok: boolean; message: string }> {
  const url = base.replace(/\/$/, "");
  try {
    const health = await fetch(`${url}/health`);
    if (health.ok) return { ok: true, message: "API joignable (/health)." };
    const openapi = await fetch(`${url}/openapi.json`);
    if (openapi.ok) return { ok: true, message: "API joignable (/openapi.json)." };
    return { ok: false, message: `Réponse inattendue (health=${health.status}).` };
  } catch (e) {
    return { ok: false, message: `Connexion impossible : ${e instanceof Error ? e.message : String(e)}` };
  }
}

/** @deprecated Utiliser verifyApi */
export function healthCheck(base: string): Promise<boolean> {
  return verifyApi(base).then((r) => r.ok);
}

export async function startSession(base: string): Promise<SessionStartResponse> {
  return apiPost(base, "/sessions/start", {});
}

export async function startConsultation(
  base: string,
  patientCase: string,
  sessionId: string
): Promise<StartConsultationResponse> {
  return apiPost(base, "/consultation/start", {
    patient_case: patientCase,
    session_id: sessionId,
  });
}

export async function resumeConsultation(
  base: string,
  threadId: string,
  resumeValue: unknown
): Promise<StartConsultationResponse> {
  return apiPost(base, "/consultation/resume", {
    thread_id: threadId,
    resume_value: resumeValue,
  });
}

export async function getConsultation(
  base: string,
  threadId: string
): Promise<{ thread_id: string; state: ConsultationState }> {
  return apiGet(base, `/consultation/${threadId}`);
}

export async function getReport(base: string, threadId: string): Promise<ReportResponse> {
  return apiGet(base, `/consultation/${threadId}/report`);
}

export async function getReportPdf(base: string, threadId: string): Promise<Blob | null> {
  const res = await fetch(`${base.replace(/\/$/, "")}/consultation/${threadId}/report/pdf`);
  if (!res.ok) return null;
  return res.blob();
}
