"use client";

import { useState, useEffect } from "react";
import PageShell from "@/components/PageShell";
import {
  fetchCompanyNews,
  fetchMCAData,
  fetchLitigation,
  fetchCIBIL,
} from "@/lib/api";
import {
  Loader2,
  Newspaper,
  Scale,
  FileText,
  TrendingUp,
  AlertCircle,
  Building2,
  Calendar,
  ExternalLink,
} from "lucide-react";
import MarkdownRenderer from "@/components/MarkdownRenderer";

const CIN_REGEX = /^[A-Z][0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6}$/;

interface NewsArticle {
  title: string;
  url: string;
  published_date: string;
  sentiment: "POSITIVE" | "NEGATIVE" | "NEUTRAL";
  summary: string;
  source: string;
}

interface LitigationCase {
  case_number: string;
  court: string;
  case_type: string;
  filing_date: string;
  status: string;
  description: string;
  amount_involved?: number;
}

interface MCAData {
  cin: string;
  company_name: string;
  registration_date: string;
  status: string;
  authorized_capital: number;
  paid_up_capital: number;
  last_agm_date?: string;
  last_balance_sheet_date?: string;
  compliance_status: string;
  directors: Array<{
    name: string;
    din: string;
    appointment_date: string;
  }>;
}

interface CIBILData {
  cin: string;
  credit_score: number;
  score_date: string;
  rating: string;
  score_type?: string;
  confidence?: "HIGH" | "MEDIUM" | "LOW";
  is_official_bureau_data?: boolean;
  proxy_metrics?: {
    litigation_case_count?: number;
    litigation_exposure_estimate?: number;
  };
  data_quality?: {
    mca_source?: string;
    news_count?: number;
    litigation_count?: number;
  };
  remarks: string;
}

export default function ResearchPage() {
  const [cin, setCin] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [activeTab, setActiveTab] = useState<"news" | "mca" | "litigation" | "cibil">("news");
  const [loading, setLoading] = useState(false);
  const [news, setNews] = useState<NewsArticle[]>([]);
  const [mcaData, setMcaData] = useState<MCAData | null>(null);
  const [litigation, setLitigation] = useState<LitigationCase[]>([]);
  const [cibilData, setCibilData] = useState<CIBILData | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Auto-fetch all data when CIN is valid
  useEffect(() => {
    const normalizedCin = cin.trim().toUpperCase();

    if (!normalizedCin) {
      setNews([]);
      setMcaData(null);
      setLitigation([]);
      setCibilData(null);
      setError(null);
      return;
    }

    if (!CIN_REGEX.test(normalizedCin)) {
      setNews([]);
      setMcaData(null);
      setLitigation([]);
      setCibilData(null);
      setError("Enter a valid CIN in format like U72200KA2007PTC043114");
      return;
    }

    const fetchAllData = async () => {
      setLoading(true);
      setError(null);

      try {
        const nameParam = companyName.trim() || undefined;
        
        // Fetch all data in parallel
        const [newsRes, mcaRes, litRes, cibilRes] = await Promise.allSettled([
          fetchCompanyNews(normalizedCin, nameParam),
          fetchMCAData(normalizedCin),
          fetchLitigation(normalizedCin, nameParam),
          fetchCIBIL(normalizedCin, nameParam),
        ]);

        // Handle news
        if (newsRes.status === "fulfilled") {
          setNews((newsRes.value as any).articles || []);
        }

        // Handle MCA
        if (mcaRes.status === "fulfilled") {
          setMcaData(mcaRes.value as MCAData);
        }

        // Handle litigation
        if (litRes.status === "fulfilled") {
          setLitigation((litRes.value as any).cases || []);
        }

        // Handle CIBIL
        if (cibilRes.status === "fulfilled") {
          setCibilData(cibilRes.value as CIBILData);
        }

        // Only set error if all fail
        if (
          newsRes.status === "rejected" &&
          mcaRes.status === "rejected" &&
          litRes.status === "rejected" &&
          cibilRes.status === "rejected"
        ) {
          setError("Failed to fetch company data");
        }
      } catch (err: any) {
        setError(err.message || "Failed to fetch data");
      } finally {
        setLoading(false);
      }
    };

    fetchAllData();
  }, [cin]);

  const sentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case "POSITIVE":
        return "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
      case "NEGATIVE":
        return "text-red-400 bg-red-500/10 border-red-500/20";
      default:
        return "text-gray-400 bg-gray-500/10 border-gray-500/20";
    }
  };

  const ratingColor = (rating: string) => {
    if (!rating) return "text-gray-400";
    if (rating.startsWith("AA")) return "text-emerald-400";
    if (rating.startsWith("A")) return "text-green-400";
    if (rating.startsWith("BBB")) return "text-amber-400";
    if (rating.startsWith("BB")) return "text-orange-400";
    return "text-red-400";
  };

  return (
    <PageShell
      title="Company Research"
      description="External data gathering and due diligence"
    >
      {/* Search Bar */}
      <div className="mb-6 space-y-3">
        <div>
          <label className="block text-xs c-text-3 mb-1.5">
            Company Identification Number (CIN) *
          </label>
          <input
            type="text"
            value={cin}
            onChange={(e) => setCin(e.target.value.toUpperCase())}
            placeholder="E.g., U72200KA2007PTC043114"
            className="w-full rounded-lg px-4 py-2.5 text-sm outline-none"
            style={{
              backgroundColor: "var(--bg-card)",
              border: "1px solid var(--bg-border)",
              color: "var(--text-primary)",
            }}
          />
          {!loading && cin.trim() && !CIN_REGEX.test(cin.trim().toUpperCase()) && (
            <p className="mt-1.5 text-xs text-amber-400">
              CIN must be exactly 21 characters and match pattern: letter + 5 digits + 2 letters + 4 digits + 3 letters + 6 digits.
            </p>
          )}
        </div>
        
        <div>
          <label className="block text-xs c-text-3 mb-1.5">
            Company Name (optional - improves news search)
          </label>
          <input
            type="text"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            placeholder="E.g., Infosys Limited or leave blank to auto-derive"
            className="w-full rounded-lg px-4 py-2.5 text-sm outline-none"
            style={{
              backgroundColor: "var(--bg-card)",
              border: "1px solid var(--bg-border)",
              color: "var(--text-primary)",
            }}
          />
          <p className="mt-1.5 text-xs c-text-3">
            Providing the actual company name helps in finding relevant news articles
          </p>
        </div>
        
        {loading && (
          <div className="flex items-center gap-2 text-xs c-text-3">
            <Loader2 className="w-3 h-3 animate-spin" />
            Fetching research data for all data sources...
          </div>
        )}
      </div>

      {/* Error State */}
      {error && (
        <div className="flex items-center gap-3 p-4 mb-6 bg-red-500/10 border border-red-500/20 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}

      {/* Company Header */}
      {mcaData && (
        <div className="mb-6 p-4 c-bg-dark rounded-lg border c-border">
          <h1 className="text-2xl font-bold c-text mb-1">{mcaData.company_name}</h1>
          <p className="text-sm c-text-3 font-mono">{mcaData.cin}</p>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 mb-6 overflow-x-auto">
        {[
          { id: "news", label: "News & Sentiment", icon: Newspaper },
          { id: "mca", label: "MCA Filings", icon: FileText },
          { id: "litigation", label: "Litigation", icon: Scale },
          { id: "cibil", label: "Credit Score (Estimated)", icon: TrendingUp },
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as typeof activeTab)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${
                activeTab === tab.id ? "" : "c-bg-dark c-text-2 hover:c-bg-card"
              }`}
              style={
                activeTab === tab.id
                  ? { backgroundColor: "var(--accent)", color: "var(--accent-text)" }
                  : undefined
              }
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Content Area */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 animate-spin c-text-3" />
        </div>
      ) : (
        <>
          {/* News Tab */}
          {activeTab === "news" && (
            <>
              {news.length > 0 ? (
                <div className="space-y-4">
                  {news.map((article, idx) => (
                    <div
                      key={idx}
                      className="c-bg-card rounded-xl border c-border p-5 hover:c-border-accent transition-all cursor-pointer"
                      style={{ boxShadow: "var(--shadow-sm)" }}
                      onClick={() => article.url && window.open(article.url, "_blank")}
                    >
                      <div className="flex items-start justify-between gap-4 mb-3">
                        <h3 className="text-base font-semibold c-text">{article.title}</h3>
                        <span
                          className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border whitespace-nowrap ${sentimentColor(
                            article.sentiment
                          )}`}
                        >
                          {article.sentiment}
                        </span>
                      </div>
                      <p className="text-sm c-text-2 mb-3">{article.summary}</p>
                      <div className="flex items-center gap-4 text-xs c-text-3">
                        <span className="flex items-center gap-1.5">
                          <Newspaper className="w-3.5 h-3.5" />
                          {article.source}
                        </span>
                        <span className="flex items-center gap-1.5">
                          <Calendar className="w-3.5 h-3.5" />
                          {new Date(article.published_date).toLocaleDateString()}
                        </span>
                        {article.url && (
                          <span className="flex items-center gap-1.5 ml-auto text-blue-400">
                            <ExternalLink className="w-3.5 h-3.5" />
                            Read more
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-12 c-bg-card rounded-xl border c-border text-center">
                  <p className="c-text-3 mb-2">No news articles found</p>
                  <p className="text-sm c-text-3">No recent news data available for this company</p>
                </div>
              )}
            </>
          )}

          {/* MCA Tab */}
          {activeTab === "mca" && (
            <>
              {mcaData ? (
                <div className="c-bg-card rounded-xl border c-border p-6" style={{ boxShadow: "var(--shadow-sm)" }}>
                  <div className="flex items-start justify-end mb-4">
                    <span
                      className={`px-3 py-1.5 rounded-full text-xs font-medium border ${
                        mcaData.status === "Active"
                          ? "text-emerald-400 bg-emerald-500/10 border-emerald-500/20"
                          : "text-red-400 bg-red-500/10 border-red-500/20"
                      }`}
                    >
                      {mcaData.status}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                    <div className="c-bg-dark rounded-lg p-4 border c-border">
                      <p className="text-xs c-text-3 mb-1">Authorized Capital</p>
                      <p className="text-lg font-bold c-text">
                        ₹{(mcaData.authorized_capital / 10000000).toFixed(2)} Cr
                      </p>
                    </div>
                    <div className="c-bg-dark rounded-lg p-4 border c-border">
                      <p className="text-xs c-text-3 mb-1">Paid-up Capital</p>
                      <p className="text-lg font-bold c-text">
                        ₹{(mcaData.paid_up_capital / 10000000).toFixed(2)} Cr
                      </p>
                    </div>
                    <div className="c-bg-dark rounded-lg p-4 border c-border">
                      <p className="text-xs c-text-3 mb-1">Compliance Status</p>
                      <p className="text-lg font-bold c-text">{mcaData.compliance_status}</p>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <h3 className="text-sm font-semibold c-text-2 flex items-center gap-2">
                      <Building2 className="w-4 h-4" />
                      Directors
                    </h3>
                    {mcaData.directors.map((director, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 c-bg-dark rounded-lg">
                        <div>
                          <p className="text-sm font-medium c-text">{director.name}</p>
                          <p className="text-xs c-text-3 font-mono mt-0.5">DIN: {director.din}</p>
                        </div>
                        <span className="text-xs c-text-3">
                          Since {new Date(director.appointment_date).toLocaleDateString()}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="p-12 c-bg-card rounded-xl border c-border text-center">
                  <p className="c-text-3 mb-2">No MCA data found</p>
                  <p className="text-sm c-text-3">MCA filing information not available</p>
                </div>
              )}
            </>
          )}

          {/* Litigation Tab */}
          {activeTab === "litigation" && (
            <>
              {litigation.length > 0 ? (
                <div className="space-y-4">
                  {litigation.map((case_, idx) => (
                    <div
                      key={idx}
                      className="c-bg-card rounded-xl border c-border p-5"
                      style={{ boxShadow: "var(--shadow-sm)" }}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h3 className="text-base font-semibold c-text mb-1">{case_.case_number}</h3>
                          <p className="text-sm c-text-3">{case_.court}</p>
                        </div>
                        <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
                          {case_.status}
                        </span>
                      </div>
                      <p className="text-sm c-text-2 mb-3">{case_.description}</p>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs">
                        <div>
                          <span className="c-text-3">Case Type</span>
                          <p className="c-text-2 font-medium mt-0.5">{case_.case_type}</p>
                        </div>
                        <div>
                          <span className="c-text-3">Filing Date</span>
                          <p className="c-text-2 font-medium mt-0.5">
                            {new Date(case_.filing_date).toLocaleDateString()}
                          </p>
                        </div>
                        {case_.amount_involved && (
                          <div>
                            <span className="c-text-3">Amount Involved</span>
                            <p className="c-text-2 font-medium mt-0.5">
                              ₹{(case_.amount_involved / 100000).toFixed(2)} L
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-12 c-bg-card rounded-xl border c-border text-center">
                  <p className="c-text-3 mb-2">No litigation cases found</p>
                  <p className="text-sm c-text-3">No active litigation on record</p>
                </div>
              )}
            </>
          )}

          {/* CIBIL Tab */}
          {activeTab === "cibil" && (
            <>
              {cibilData ? (
                <div className="c-bg-card rounded-xl border c-border p-6" style={{ boxShadow: "var(--shadow-sm)" }}>
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <h3 className="text-lg font-bold c-text mb-1">Estimated Commercial Credit Score</h3>
                      <p className="text-xs text-amber-400">
                        Model-based proxy, not official bureau CIBIL data
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-4xl font-bold" style={{ color: "var(--accent)" }}>
                        {cibilData.credit_score}
                      </p>
                      <p className={`text-lg font-bold ${ratingColor(cibilData.rating)}`}>
                        {cibilData.rating || "N/A"}
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="c-bg-dark rounded-lg p-4 border c-border text-center">
                      <p className="text-xs c-text-3 mb-1">Confidence</p>
                      <p className="text-2xl font-bold c-text">{cibilData.confidence || "N/A"}</p>
                    </div>
                    <div className="c-bg-dark rounded-lg p-4 border c-border text-center">
                      <p className="text-xs c-text-3 mb-1">Litigation Cases</p>
                      <p className="text-2xl font-bold c-text">
                        {cibilData.proxy_metrics?.litigation_case_count ?? cibilData.data_quality?.litigation_count ?? 0}
                      </p>
                    </div>
                    <div className="c-bg-dark rounded-lg p-4 border c-border text-center">
                      <p className="text-xs c-text-3 mb-1">Exposure (Est.)</p>
                      <p className="text-2xl font-bold c-text">
                        ₹{((cibilData.proxy_metrics?.litigation_exposure_estimate ?? 0) / 10000000).toFixed(1)}Cr
                      </p>
                    </div>
                    <div className="c-bg-dark rounded-lg p-4 border c-border text-center">
                      <p className="text-xs c-text-3 mb-1">News Coverage</p>
                      <p className="text-2xl font-bold c-text">
                        {cibilData.data_quality?.news_count ?? 0}
                      </p>
                    </div>
                  </div>

                  <div className="c-bg-dark rounded-lg p-4 border c-border mb-4">
                    <p className="text-xs c-text-3 mb-1">MCA Source</p>
                    <p className="text-sm c-text">{cibilData.data_quality?.mca_source || "unknown"}</p>
                  </div>

                  {cibilData.remarks && (
                    <div className="c-bg-dark rounded-lg p-4 border c-border">
                      <p className="text-xs c-text-3 mb-2">Remarks</p>
                      <MarkdownRenderer content={cibilData.remarks} />
                    </div>
                  )}

                  <div className="flex items-center gap-2 mt-4 text-xs c-text-3">
                    <Calendar className="w-3.5 h-3.5" />
                    Score Date: {new Date(cibilData.score_date).toLocaleDateString()}
                  </div>
                </div>
              ) : (
                <div className="p-12 c-bg-card rounded-xl border c-border text-center">
                  <p className="c-text-3 mb-2">No CIBIL data found</p>
                  <p className="text-sm c-text-3">CIBIL score information not available</p>
                </div>
              )}
            </>
          )}
        </>
      )}
    </PageShell>
  );
}
