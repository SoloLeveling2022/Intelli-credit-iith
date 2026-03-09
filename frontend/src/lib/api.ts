const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface AuthUser {
  username: string;
  cin: string;
  company_name: string;
}

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

function authHeaders(): Record<string, string> {
  const token = getToken();
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return headers;
}

async function fetchAPI<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: authHeaders(),
    ...options,
  });
  if (res.status === 401) {
    if (typeof window !== "undefined") {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      if (window.location.pathname !== "/") {
        window.location.href = "/";
      }
    }
    throw new Error("Unauthorized");
  }
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

// Auth
export const login = (username: string, password: string) =>
  fetchAPI<{ token: string; user: AuthUser }>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });

export const register = (
  username: string,
  password: string,
  gstin: string,
  company_name: string
) =>
  fetchAPI<{ token: string; user: AuthUser }>("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ username, password, gstin, company_name }),
  });

export const getMe = () => fetchAPI<AuthUser>("/api/auth/me");

// Dashboard stats
export const getDashboardStats = () => fetchAPI("/api/stats/dashboard");
export const getAppraisalSummary = () => fetchAPI("/api/stats/appraisal-summary");
export const getTopRiskyCompanies = () =>
  fetchAPI("/api/stats/top-risky-companies");

// Reconciliation (GST)
export const triggerReconciliation = (returnPeriod: string = "012026", force: boolean = false) =>
  fetchAPI("/api/reconcile", {
    method: "POST",
    body: JSON.stringify({ return_period: returnPeriod, force }),
  });

export const getReconciliationResults = (
  returnPeriod: string = "012026",
  page = 1,
  pageSize = 50,
  mismatchType?: string,
  severity?: string
) => {
  const params = new URLSearchParams({
    return_period: returnPeriod,
    page: String(page),
    page_size: String(pageSize),
  });
  if (mismatchType) params.set("mismatch_type", mismatchType);
  if (severity) params.set("severity", severity);
  return fetchAPI(`/api/reconcile/results?${params}`);
};

// Credit Appraisal
export const triggerAppraisal = (cin: string) =>
  fetchAPI("/api/appraisal", {
    method: "POST",
    body: JSON.stringify({ cin }),
  });
export const getAppraisalResults = (
  page = 1,
  pageSize = 50,
  decisionType?: string,
  severity?: string
) => {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  if (decisionType) params.set("decision_type", decisionType);
  if (severity) params.set("severity", severity);
  return fetchAPI(`/api/appraisal/results?${params}`);
};

// Graph
export const getGraphNodes = (limit = 200) =>
  fetchAPI(`/api/appraisal/graph/nodes?limit=${limit}`);
export const searchGraph = (query: string) =>
  fetchAPI(`/api/appraisal/graph/search?q=${encodeURIComponent(query)}`);
export const getShellCompanies = () =>
  fetchAPI("/api/appraisal/graph/shell-companies");
export const getCompanyNetwork = (cin: string) =>
  fetchAPI(`/api/appraisal/graph/company-network?cin=${encodeURIComponent(cin)}`);

// Audit
export const generateAuditTrail = (mismatch: object) =>
  fetchAPI("/api/audit/generate", {
    method: "POST",
    body: JSON.stringify(mismatch),
  });

// CAM (Credit Appraisal Memo)
export const generateCAM = (cin: string) =>
  fetchAPI("/api/cam/generate", {
    method: "POST",
    body: JSON.stringify({ cin }),
  });
export const getCAMList = () => fetchAPI("/api/cam/list");
export const exportCAMPDF = async (camId: string) => {
  const token = getToken();
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}/api/cam/export/${camId}/pdf`, { headers });
  if (!res.ok) throw new Error("CAM PDF generation failed");
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `CAM_${camId}.pdf`;
  a.click();
  URL.revokeObjectURL(url);
};

// Risk
export const getCompanyRisks = () => fetchAPI("/api/risk/companies");
export const getCompanyRiskDetail = (cin: string) =>
  fetchAPI(`/api/risk/companies/${cin}`);
export const getCompanyRiskSummary = (cin: string) =>
  fetchAPI(`/api/risk/companies/${cin}/summary`);
export const getCompanyScorecard = (cin: string) =>
  fetchAPI(`/api/risk/companies/${cin}/scorecard`);

// Vendor Risk (GST Module)
export const getVendorRisks = () => fetchAPI("/api/risk/vendors");
export const getVendorRiskDetail = (gstin: string) =>
  fetchAPI(`/api/risk/vendors/${gstin}`);
export const getVendorRiskSummary = (gstin: string) =>
  fetchAPI(`/api/risk/vendors/${gstin}/summary`);
export const getVendorScorecard = (gstin: string) =>
  fetchAPI(`/api/risk/vendors/${gstin}/scorecard`);

// Upload
export const uploadDocument = (file: File, docType: string) => {
  const formData = new FormData();
  formData.append("file", file);
    formData.append("doc_type", docType);
  const token = getToken();
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return fetch(`${API_BASE}/api/documents/upload`, {
    method: "POST",
    body: formData,
    headers,
  }).then((r) => r.json());
};

export const batchUploadDocuments = (files: File[]) => {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));
  const token = getToken();
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return fetch(`${API_BASE}/api/documents/batch-upload`, {
    method: "POST",
    body: formData,
    headers,
  }).then((r) => r.json());
};

export const uploadCompanies = (file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  const token = getToken();
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return fetch(`${API_BASE}/api/data/upload-companies`, {
    method: "POST",
    body: formData,
    headers,
  }).then((r) => r.json());
};
// Chat
export const sendChatMessage = (message: string, conversationId?: string) =>
  fetchAPI<{ response: string; conversation_id: string }>("/api/chat/message", {
    method: "POST",
    body: JSON.stringify({ message, conversation_id: conversationId }),
  });

export const getChatSuggestions = () =>
  getToken()
    ? fetchAPI<{ suggestions: string[] }>("/api/chat/suggestions")
    : Promise.resolve({ suggestions: [] });

// PDF Download
// (Removed - Use exportCAMPDF instead)

// ITC Flow (Sankey)
// Loan Approval Flow
export const getLoanFlow = () => fetchAPI("/api/stats/loan-flow");

// Trend Data
export const getTrendData = () => fetchAPI("/api/stats/trends");

// Vendor Scorecard
// Company Credit Score
export const getCompanyCreditScore = (cin: string) =>
  fetchAPI(`/api/risk/companies/${cin}/score`);

// GSTN Mock API
// Research APIs
export const fetchCompanyNews = (cin: string, companyName?: string) => {
  const params = new URLSearchParams({ cin });
  if (companyName) params.append("company_name", companyName);
  return fetchAPI(`/api/research/news?${params}`);
};
export const fetchMCAData = (cin: string) =>
  fetchAPI(`/api/research/mca?cin=${cin}`);
export const fetchLitigation = (cin: string, companyName?: string) => {
  const params = new URLSearchParams({ cin });
  if (companyName) params.append("company_name", companyName);
  return fetchAPI(`/api/research/litigation?${params}`);
};
export const fetchCIBIL = (cin: string, companyName?: string) => {
  const params = new URLSearchParams({ cin });
  if (companyName) params.append("company_name", companyName);
  return fetchAPI(`/api/research/cibil?${params}`);
};

// GSTN/GSP Integration
export const getGSTNStatus = () => fetchAPI("/api/gstn/status");

export const fetchGSTN = (type: string, gstin: string, period: string) => {
  const endpoint = type === "GSTR1" ? "/api/gstn/fetch-gstr1" :
                   type === "GSTR2B" ? "/api/gstn/fetch-gstr2b" :
                   "/api/gstn/fetch-gstr3b";
  return fetchAPI(endpoint, {
    method: "POST",
    body: JSON.stringify({ gstin, return_period: period }),
  });
};

// ERP Import
export const importERP = (source: string, file: File, period?: string) => {
  const formData = new FormData();
  formData.append("file", file);
  if (period) formData.append("return_period", period);
  const token = getToken();
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return fetch(`${API_BASE}/api/erp/import/${source}`, {
    method: "POST",
    body: formData,
    headers,
  }).then((r) => r.json());
};

// Banking
export const analyzeBankStatement = (file: File, cin: string) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("cin", cin);
  const token = getToken();
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return fetch(`${API_BASE}/api/banking/analyze`, {
    method: "POST",
    body: formData,
    headers,
  }).then((r) => r.json());
};
// Notifications
export const getNotificationSettings = () =>
  fetchAPI("/api/notifications/settings");

export const configureNotifications = (settings: Record<string, unknown>) =>
  fetchAPI("/api/notifications/configure", {
    method: "POST",
    body: JSON.stringify(settings),
  });

export const testNotification = () =>
  fetchAPI("/api/notifications/test", { method: "POST" });

// Bolna AI Agent
const BOLNA_API_KEY = "bn-988a382a338a42afb0b1ec02068d0784";
const BOLNA_AGENT_ID = "c882e4dc-42cd-4154-b803-026efc0ebfcb";

export interface BolnaCallRequest {
  recipient_phone_number: string;
  from_phone_number: string;
  company_data: {
    cin: string;
    legal_name: string;
    industry?: string;
    revenue?: string;
    loan_requested?: string;
    [key: string]: any;
  };
}

export interface BolnaCallResponse {
  execution_id: string;
  status: string;
  call_id?: string;
  message?: string;
}

export interface BolnaTranscript {
  execution_id: string;
  call_duration?: number;
  status: string;
  conversation?: Array<{
    speaker: string;
    text: string;
    timestamp?: string;
  }>;
}

// Helper to extract transcript text from Bolna conversation
export const extractTranscriptText = (bolnaData: BolnaTranscript): string => {
  if (!bolnaData.conversation || bolnaData.conversation.length === 0) {
    return "No conversation recorded.";
  }
  return bolnaData.conversation
    .map((msg) => `${msg.speaker}: ${msg.text}`)
    .join("\n");
};

export const triggerBolnaCall = async (
  request: BolnaCallRequest
): Promise<BolnaCallResponse> => {
  const response = await fetch("https://api.bolna.ai/call", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${BOLNA_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      agent_id: BOLNA_AGENT_ID,
      recipient_phone_number: request.recipient_phone_number,
      from_phone_number: request.from_phone_number,
      user_data: request.company_data,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Bolna API error: ${response.status} - ${error}`);
  }

  return response.json();
};

export const fetchBolnaTranscript = async (
  execution_id: string
): Promise<BolnaTranscript> => {
  const response = await fetch(
    `https://api.bolna.ai/agent/${BOLNA_AGENT_ID}/execution/${execution_id}`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${BOLNA_API_KEY}`,
      },
    }
  );

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Bolna transcript fetch error: ${response.status} - ${error}`);
  }

  return response.json();
};

export const summarizeTranscriptWithGemini = async (
  transcript: string
): Promise<{ summary: string; risk_insights: string[]; recommendations: string[] }> => {
  // Call backend to summarize with Gemini
  return fetchAPI("/api/chat/summarize-transcript", {
    method: "POST",
    body: JSON.stringify({ transcript }),
  });
};
