"use client";

import { useState } from "react";
import PageShell from "@/components/PageShell";
import {
  fetchCompanyNews,
  fetchMCAData,
  fetchLitigation,
  fetchCIBIL,
  getCompanyRiskDetail,
  analyzeBankStatement,
  uploadDocument,
} from "@/lib/api";
import {
  CheckCircle2,
  AlertCircle,
  Loader2,
  Upload,
  FileText,
  Building2,
  Scale,
  TrendingUp,
  Newspaper,
  Download,
  Eye,
} from "lucide-react";
import { formatCurrency, riskColor } from "@/lib/utils";

interface DDSection {
  id: string;
  title: string;
  status: "pending" | "in-progress" | "completed" | "failed";
  icon: any;
  description: string;
}

interface CompanyProfile {
  cin: string;
  legal_name: string;
  registration_date: string;
  status: string;
  authorized_capital: number;
  paid_up_capital: number;
}

interface RiskAssessment {
  risk_score: number;
  risk_level: string;
  character_score: number;
  capacity_score: number;
  capital_score: number;
  collateral_score: number;
  conditions_score: number;
}

export default function DueDiligencePage() {
  const [cin, setCin] = useState("");
  const [companyProfile, setCompanyProfile] = useState<CompanyProfile | null>(null);
  const [riskAssessment, setRiskAssessment] = useState<RiskAssessment | null>(null);
  const [sections, setSections] = useState<DDSection[]>([
    {
      id: "company",
      title: "Company Profile (MCA)",
      status: "pending",
      icon: Building2,
      description: "Basic company information and MCA filings",
    },
    {
      id: "credit",
      title: "Credit Score (CIBIL)",
      status: "pending",
      icon: TrendingUp,
      description: "Commercial credit score and loan history",
    },
    {
      id: "litigation",
      title: "Litigation Check",
      status: "pending",
      icon: Scale,
      description: "Court cases and legal proceedings",
    },
    {
      id: "news",
      title: "News & Sentiment",
      status: "pending",
      icon: Newspaper,
      description: "Recent news articles and sentiment analysis",
    },
    {
      id: "risk",
      title: "Risk Assessment",
      status: "pending",
      icon: AlertCircle,
      description: "Five C's of credit risk scoring",
    },
    {
      id: "documents",
      title: "Document Verification",
      status: "pending",
      icon: FileText,
      description: "Upload and verify financial documents",
    },
  ]);
  const [activeSection, setActiveSection] = useState<string | null>(null);
  const [sectionData, setSectionData] = useState<Record<string, any>>({});
  const [uploadedFiles, setUploadedFiles] = useState<Array<{ name: string; type: string }>>([]);

  const updateSectionStatus = (id: string, status: DDSection["status"]) => {
    setSections((prev) =>
      prev.map((section) => (section.id === id ? { ...section, status } : section))
    );
  };

  const runDueDiligence = async () => {
    if (!cin.trim()) return;

    // Clear previous data
    setSectionData({});
    setCompanyProfile(null);
    setRiskAssessment(null);

    // Company Profile
    updateSectionStatus("company", "in-progress");
    try {
      const mcaData = (await fetchMCAData(cin)) as any;
      setCompanyProfile({
        cin: mcaData.cin,
        legal_name: mcaData.company_name,
        registration_date: mcaData.registration_date,
        status: mcaData.status,
        authorized_capital: mcaData.authorized_capital,
        paid_up_capital: mcaData.paid_up_capital,
      });
      setSectionData((prev) => ({ ...prev, company: mcaData }));
      updateSectionStatus("company", "completed");
    } catch {
      updateSectionStatus("company", "failed");
    }

    // Credit Score
    updateSectionStatus("credit", "in-progress");
    try {
      const cibilData = await fetchCIBIL(cin);
      setSectionData((prev) => ({ ...prev, credit: cibilData }));
      updateSectionStatus("credit", "completed");
    } catch {
      updateSectionStatus("credit", "failed");
    }

    // Litigation
    updateSectionStatus("litigation", "in-progress");
    try {
      const litData = await fetchLitigation(cin);
      setSectionData((prev) => ({ ...prev, litigation: litData }));
      updateSectionStatus("litigation", "completed");
    } catch {
      updateSectionStatus("litigation", "failed");
    }

    // News
    updateSectionStatus("news", "in-progress");
    try {
      const newsData = await fetchCompanyNews(cin);
      setSectionData((prev) => ({ ...prev, news: newsData }));
      updateSectionStatus("news", "completed");
    } catch {
      updateSectionStatus("news", "failed");
    }

    // Risk Assessment
    updateSectionStatus("risk", "in-progress");
    try {
      const riskData = (await getCompanyRiskDetail(cin)) as any;
      setRiskAssessment({
        risk_score: riskData.risk_score || 0,
        risk_level: riskData.risk_level || "MEDIUM",
        character_score: riskData.character_score || 0,
        capacity_score: riskData.capacity_score || 0,
        capital_score: riskData.capital_score || 0,
        collateral_score: riskData.collateral_score || 0,
        conditions_score: riskData.conditions_score || 0,
      });
      setSectionData((prev) => ({ ...prev, risk: riskData }));
      updateSectionStatus("risk", "completed");
    } catch {
      updateSectionStatus("risk", "failed");
    }
  };

  const handleFileUpload = async (file: File, docType: string) => {
    updateSectionStatus("documents", "in-progress");
    try {
      await uploadDocument(file, docType);
      setUploadedFiles((prev) => [...prev, { name: file.name, type: docType }]);
      updateSectionStatus("documents", "completed");
    } catch {
      updateSectionStatus("documents", "failed");
    }
  };

  const completedCount = sections.filter((s) => s.status === "completed").length;
  const completionPercentage = Math.round((completedCount / sections.length) * 100);

  const downloadReport = () => {
    const report = {
      company: companyProfile,
      risk_assessment: riskAssessment,
      sections: sectionData,
      uploaded_documents: uploadedFiles,
      generated_at: new Date().toISOString(),
    };
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `DD_Report_${cin}_${new Date().toISOString().split("T")[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <PageShell
      title="Due Diligence Workflow"
      description="Comprehensive credit due diligence checklist"
    >
      {/* Header Card */}
      <div className="c-bg-card rounded-xl border c-border p-6 mb-6" style={{ boxShadow: "var(--shadow-sm)" }}>
        <div className="flex flex-col md:flex-row items-start md:items-center gap-4">
          <div className="flex-1">
            <input
              type="text"
              value={cin}
              onChange={(e) => setCin(e.target.value.toUpperCase())}
              placeholder="Enter Company CIN to start due diligence..."
              className="w-full rounded-lg px-4 py-2.5 text-sm outline-none"
              style={{
                backgroundColor: "var(--bg-dark)",
                border: "1px solid var(--bg-border)",
                color: "var(--text-primary)",
              }}
            />
          </div>
          <button
            onClick={runDueDiligence}
            disabled={!cin.trim() || sections.some((s) => s.status === "in-progress")}
            className="flex items-center gap-2 px-6 py-2.5 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 whitespace-nowrap"
            style={{ backgroundColor: "var(--accent)", color: "var(--accent-text)" }}
          >
            {sections.some((s) => s.status === "in-progress") ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <CheckCircle2 className="w-4 h-4" />
            )}
            Run Due Diligence
          </button>
        </div>

        {companyProfile && (
          <div className="mt-4 pt-4 border-t c-border">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-lg font-bold c-text">{companyProfile.legal_name}</h3>
                <p className="text-sm c-text-3 font-mono mt-1">{companyProfile.cin}</p>
              </div>
              <span
                className={`px-3 py-1.5 rounded-full text-xs font-medium border ${
                  companyProfile.status === "Active"
                    ? "text-emerald-400 bg-emerald-500/10 border-emerald-500/20"
                    : "text-red-400 bg-red-500/10 border-red-500/20"
                }`}
              >
                {companyProfile.status}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Progress Bar */}
      {completedCount > 0 && (
        <div className="c-bg-card rounded-xl border c-border p-5 mb-6" style={{ boxShadow: "var(--shadow-sm)" }}>
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium c-text-2">Due Diligence Progress</span>
            <span className="text-sm font-bold" style={{ color: "var(--accent)" }}>
              {completionPercentage}%
            </span>
          </div>
          <div className="w-full h-2 c-bg-dark rounded-full overflow-hidden">
            <div
              className="h-full transition-all duration-500"
              style={{ width: `${completionPercentage}%`, backgroundColor: "var(--accent)" }}
            />
          </div>
          <div className="flex items-center justify-between mt-2 text-xs c-text-3">
            <span>
              {completedCount} of {sections.length} checks completed
            </span>
            {completionPercentage === 100 && (
              <button
                onClick={downloadReport}
                className="flex items-center gap-1.5 text-blue-400 hover:text-blue-300 transition-colors"
              >
                <Download className="w-3.5 h-3.5" />
                Download Report
              </button>
            )}
          </div>
        </div>
      )}

      {/* Risk Summary (if available) */}
      {riskAssessment && (
        <div className="c-bg-card rounded-xl border c-border p-6 mb-6" style={{ boxShadow: "var(--shadow-sm)" }}>
          <h3 className="text-base font-semibold c-text mb-4">Five C's Risk Assessment</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            <div className="text-center p-3 c-bg-dark rounded-lg">
              <p className="text-2xl font-bold" style={{ color: "var(--accent)" }}>
                {riskAssessment.risk_score}
              </p>
              <p className="text-xs c-text-3 mt-1">Overall Score</p>
              <p className={`text-xs font-medium mt-1 ${riskColor(riskAssessment.risk_level)}`}>
                {riskAssessment.risk_level}
              </p>
            </div>
            <div className="text-center p-3 c-bg-dark rounded-lg">
              <p className="text-lg font-bold c-text">{riskAssessment.character_score}</p>
              <p className="text-xs c-text-3 mt-1">Character</p>
            </div>
            <div className="text-center p-3 c-bg-dark rounded-lg">
              <p className="text-lg font-bold c-text">{riskAssessment.capacity_score}</p>
              <p className="text-xs c-text-3 mt-1">Capacity</p>
            </div>
            <div className="text-center p-3 c-bg-dark rounded-lg">
              <p className="text-lg font-bold c-text">{riskAssessment.capital_score}</p>
              <p className="text-xs c-text-3 mt-1">Capital</p>
            </div>
            <div className="text-center p-3 c-bg-dark rounded-lg">
              <p className="text-lg font-bold c-text">{riskAssessment.collateral_score}</p>
              <p className="text-xs c-text-3 mt-1">Collateral</p>
            </div>
            <div className="text-center p-3 c-bg-dark rounded-lg">
              <p className="text-lg font-bold c-text">{riskAssessment.conditions_score}</p>
              <p className="text-xs c-text-3 mt-1">Conditions</p>
            </div>
          </div>
        </div>
      )}

      {/* Checklist Sections */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {sections.map((section) => {
          const Icon = section.icon;
          return (
            <div
              key={section.id}
              className={`c-bg-card rounded-xl border p-5 transition-all cursor-pointer ${
                activeSection === section.id ? "c-border-accent" : "c-border hover:c-border-accent"
              }`}
              style={{ boxShadow: "var(--shadow-sm)" }}
              onClick={() => setActiveSection(activeSection === section.id ? null : section.id)}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div
                    className="p-2 rounded-lg"
                    style={{ backgroundColor: "var(--accent-light)", color: "var(--accent)" }}
                  >
                    <Icon className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold c-text">{section.title}</h3>
                    <p className="text-xs c-text-3 mt-0.5">{section.description}</p>
                  </div>
                </div>
                <div className="shrink-0">
                  {section.status === "completed" && (
                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  )}
                  {section.status === "in-progress" && (
                    <Loader2 className="w-5 h-5 animate-spin text-blue-400" />
                  )}
                  {section.status === "failed" && <AlertCircle className="w-5 h-5 text-red-400" />}
                  {section.status === "pending" && (
                    <div className="w-5 h-5 rounded-full border-2 c-border" />
                  )}
                </div>
              </div>

              {/* Expanded Section Data */}
              {activeSection === section.id && sectionData[section.id] && (
                <div className="mt-4 pt-4 border-t c-border">
                  <div className="text-xs c-text-3 space-y-2">
                    {section.id === "company" && sectionData.company && (
                      <>
                        <div>
                          <span className="font-medium">Authorized Capital:</span> ₹
                          {(sectionData.company.authorized_capital / 10000000).toFixed(2)} Cr
                        </div>
                        <div>
                          <span className="font-medium">Paid-up Capital:</span> ₹
                          {(sectionData.company.paid_up_capital / 10000000).toFixed(2)} Cr
                        </div>
                      </>
                    )}
                    {section.id === "credit" && sectionData.credit && (
                      <>
                        <div>
                          <span className="font-medium">Credit Score:</span> {sectionData.credit.credit_score}
                        </div>
                        <div>
                          <span className="font-medium">Rating:</span> {sectionData.credit.rating}
                        </div>
                      </>
                    )}
                    {section.id === "litigation" && sectionData.litigation?.cases && (
                      <div>
                        <span className="font-medium">Cases:</span> {sectionData.litigation.cases.length}
                      </div>
                    )}
                    {section.id === "news" && sectionData.news?.articles && (
                      <div>
                        <span className="font-medium">Articles:</span> {sectionData.news.articles.length}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Document Upload Section */}
              {section.id === "documents" && activeSection === section.id && (
                <div className="mt-4 pt-4 border-t c-border">
                  <label className="flex items-center justify-center gap-2 px-4 py-3 c-bg-dark hover:c-bg-card rounded-lg border c-border cursor-pointer transition-colors">
                    <Upload className="w-4 h-4 c-text-3" />
                    <span className="text-xs c-text-2">Upload Documents</span>
                    <input
                      type="file"
                      className="hidden"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) handleFileUpload(file, "financial_statement");
                      }}
                    />
                  </label>
                  {uploadedFiles.length > 0 && (
                    <div className="mt-3 space-y-2">
                      {uploadedFiles.map((file, idx) => (
                        <div
                          key={idx}
                          className="flex items-center gap-2 text-xs c-text-3 p-2 c-bg-dark rounded"
                        >
                          <FileText className="w-3.5 h-3.5" />
                          <span className="flex-1 truncate">{file.name}</span>
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </PageShell>
  );
}
