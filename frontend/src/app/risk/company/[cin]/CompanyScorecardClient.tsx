"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import PageShell from "@/components/PageShell";
import { getCompanyRiskDetail, getCompanyScorecard, getCompanyRiskSummary } from "@/lib/api";
import { riskColor, formatCurrency } from "@/lib/utils";
import { ArrowLeft, Bot, ShieldAlert, X } from "lucide-react";
import MarkdownRenderer from "@/components/MarkdownRenderer";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts";

const CHART_COLORS = ["#e5e5e5", "#a3a3a3", "#737373", "#525252"];

export default function CompanyScorecardPage() {
  const params = useParams();
  const cin = params.cin as string;
  const [company, setCompany] = useState<any>(null);
  const [scorecard, setScorecard] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [aiSummary, setAiSummary] = useState<string | null>(null);
  const [aiLoading, setAiLoading] = useState(false);

  useEffect(() => {
    Promise.allSettled([
      getCompanyRiskDetail(cin),
      getCompanyScorecard(cin),
    ]).then(([companyRes, scorecardRes]) => {
      if (companyRes.status === "fulfilled") setCompany(companyRes.value);
      if (scorecardRes.status === "fulfilled") setScorecard(scorecardRes.value);
      setLoading(false);
    });
  }, [cin]);

  const loadAISummary = async () => {
    setAiLoading(true);
    try {
      const data = (await getCompanyRiskSummary(cin)) as any;
      setAiSummary(data.ai_summary || "No summary available.");
    } catch {
      setAiSummary("Unable to generate AI summary.");
    }
    setAiLoading(false);
  };

  const riskBreakdown = scorecard?.risk_breakdown
    ? Object.entries(scorecard.risk_breakdown).map(([key, val]: [string, any]) => ({
        name: key.replace(/_/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase()),
        score: Math.round(val.score * 10) / 10,
        weight: val.weight * 100,
      }))
    : [];

  return (
    <PageShell
      title="Company Scorecard"
      description={`Detailed credit risk analysis for ${cin}`}
    >
      <Link
        href="/risk"
        className="inline-flex items-center gap-2 text-sm c-text-2 hover:c-text mb-6 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Risk Assessment
      </Link>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-8 w-8 border-2 border-t-transparent" style={{ borderColor: "var(--text-secondary)", borderTopColor: "transparent" }} />
        </div>
      ) : company ? (
        <div className="space-y-6">
          {/* Header */}
          <div className="c-bg-card rounded-xl border c-border p-6" style={{ boxShadow: "var(--shadow-sm)" }}>
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-bold c-text">
                  {company.legal_name || company.company_name || "Unknown"}
                </h2>
                <p className="text-sm c-text-3 font-mono mt-1">{company.cin}</p>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-center">
                  <p className="text-3xl font-bold c-text">{Math.round(company.credit_score || company.risk_score || 0)}</p>
                  <p className="text-xs c-text-3">Credit Score</p>
                </div>
                <span className={`text-sm font-bold px-3 py-1.5 rounded-lg ${riskColor(company.risk_level)}`}>
                  {company.risk_level}
                </span>
              </div>
            </div>
            {/* Score bar */}
            <div className="mt-4">
              <div className="w-full c-bg-dark rounded-full h-3">
                <div
                  className={`h-3 rounded-full transition-all ${
                    (company.credit_score || 0) >= 75 ? "bg-emerald-500" :
                    (company.credit_score || 0) >= 50 ? "bg-gray-400" :
                    (company.credit_score || 0) >= 25 ? "bg-amber-500" : "bg-red-500"
                  }`}
                  style={{ width: `${Math.min(100, company.credit_score || company.risk_score || 0)}%` }}
                />
              </div>
            </div>
          </div>

          {/* Risk Factor Breakdown */}
          {riskBreakdown.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {riskBreakdown.map((factor, i) => (
                <div key={factor.name} className="c-bg-card rounded-xl border c-border p-4" style={{ boxShadow: "var(--shadow-sm)" }}>
                  <p className="text-xs c-text-3 mb-2">{factor.name}</p>
                  <p className="text-2xl font-bold c-text">{factor.score}</p>
                  <p className="text-[10px] c-text-3 mt-1">Weight: {factor.weight}%</p>
                  <div className="mt-2 w-full c-bg-dark rounded-full h-1.5">
                    <div
                      className="h-1.5 rounded-full"
                      style={{ width: `${Math.min(100, factor.score)}%`, backgroundColor: CHART_COLORS[i % CHART_COLORS.length] }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Stats row */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: "Promoters", value: scorecard?.promoters?.length || 0 },
              { label: "Litigation Cases", value: scorecard?.litigation?.length || 0 },
              { label: "Related Companies", value: scorecard?.related_companies?.length || 0 },
              { label: "Financial Years", value: scorecard?.financial_history?.length || 0 },
            ].map((stat) => (
              <div key={stat.label} className="c-bg-card rounded-xl border c-border p-4 text-center" style={{ boxShadow: "var(--shadow-sm)" }}>
                <p className="text-xs c-text-3">{stat.label}</p>
                <p className="text-xl font-bold c-text mt-1">{stat.value}</p>
              </div>
            ))}
          </div>

          {/* Financial History Chart */}
          {scorecard?.financial_history?.length > 0 && (
            <div className="c-bg-card rounded-xl border c-border p-5" style={{ boxShadow: "var(--shadow-sm)" }}>
              <h3 className="text-sm font-semibold c-text mb-4">Financial Performance</h3>
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={scorecard.financial_history} margin={{ top: 5, right: 10, bottom: 5, left: 10 }}>
                  <XAxis dataKey="year" tick={{ fill: "var(--text-tertiary)", fontSize: 10 }} axisLine={{ stroke: "var(--bg-border)" }} tickLine={false} />
                  <YAxis tick={{ fill: "var(--text-tertiary)", fontSize: 10 }} axisLine={{ stroke: "var(--bg-border)" }} tickLine={false} tickFormatter={(value) => `₹${(value / 1e7).toFixed(1)}Cr`} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "var(--bg-card)", border: "1px solid var(--bg-border)", borderRadius: "8px", color: "var(--text-primary)", fontSize: 12 }}
                    formatter={(value: any) => formatCurrency(Number(value) || 0)}
                  />
                  <Line type="monotone" dataKey="revenue" stroke="#e5e5e5" strokeWidth={2} name="Revenue" dot={{ fill: "#e5e5e5" }} />
                  <Line type="monotone" dataKey="profit" stroke="#a3a3a3" strokeWidth={2} name="Profit" dot={{ fill: "#a3a3a3" }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Promoters */}
          {scorecard?.promoters?.length > 0 && (
            <div className="c-bg-card rounded-xl border c-border p-5" style={{ boxShadow: "var(--shadow-sm)" }}>
              <h3 className="text-sm font-semibold c-text mb-4">Promoters & Directors</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b c-border">
                      <th className="text-left py-2 px-3 c-text-2 text-xs font-medium">Name</th>
                      <th className="text-left py-2 px-3 c-text-2 text-xs font-medium">PAN</th>
                      <th className="text-right py-2 px-3 c-text-2 text-xs font-medium">Shareholding</th>
                    </tr>
                  </thead>
                  <tbody>
                    {scorecard.promoters.map((p: any, i: number) => (
                      <tr key={i} className="border-b c-border hover:c-bg-dark transition-colors">
                        <td className="py-2 px-3 c-text text-sm">{p.name || "Unknown"}</td>
                        <td className="py-2 px-3 c-text-3 text-xs font-mono">{p.pan || "N/A"}</td>
                        <td className="py-2 px-3 c-text text-sm text-right font-mono">{p.shareholding ? `${(p.shareholding * 100).toFixed(2)}%` : "N/A"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Related Companies */}
          {scorecard?.related_companies?.length > 0 && (
            <div className="c-bg-card rounded-xl border c-border p-5" style={{ boxShadow: "var(--shadow-sm)" }}>
              <h3 className="text-sm font-semibold c-text mb-4">Related Companies</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b c-border">
                      <th className="text-left py-2 px-3 c-text-2 text-xs font-medium">Company</th>
                      <th className="text-left py-2 px-3 c-text-2 text-xs font-medium">CIN</th>
                      <th className="text-left py-2 px-3 c-text-2 text-xs font-medium">Relationship</th>
                      <th className="text-right py-2 px-3 c-text-2 text-xs font-medium">Volume</th>
                    </tr>
                  </thead>
                  <tbody>
                    {scorecard.related_companies.map((c: any, i: number) => (
                      <tr key={i} className="border-b c-border hover:c-bg-dark transition-colors">
                        <td className="py-2 px-3 c-text text-sm">{c.name || "Unknown"}</td>
                        <td className="py-2 px-3 c-text-3 text-xs font-mono">{c.cin}</td>
                        <td className="py-2 px-3 c-text-2 text-xs">{c.relationship || "N/A"}</td>
                        <td className="py-2 px-3 c-text text-sm text-right font-mono">{c.volume ? formatCurrency(c.volume) : "N/A"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Litigation */}
          {scorecard?.litigation?.length > 0 && (
            <div className="c-bg-card rounded-xl border c-border p-5" style={{ boxShadow: "var(--shadow-sm)" }}>
              <h3 className="text-sm font-semibold c-text mb-4">Litigation Cases</h3>
              <div className="space-y-3">
                {scorecard.litigation.map((lit: any, i: number) => (
                  <div key={i} className="p-4 c-bg-dark rounded-lg">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <p className="text-sm c-text font-medium">{lit.case_type || "Unknown Type"}</p>
                        <p className="text-xs c-text-3 font-mono mt-1">{lit.case_number || "N/A"}</p>
                      </div>
                      <span className={`text-xs px-2 py-1 rounded ${lit.status === "Pending" ? "bg-amber-500/20 text-amber-400" : "bg-emerald-500/20 text-emerald-400"}`}>
                        {lit.status || "Unknown"}
                      </span>
                    </div>
                    <p className="text-xs c-text-3">{lit.court || "Unknown Court"}</p>
                    {lit.amount && (
                      <p className="text-xs c-text-2 mt-1">Amount: {formatCurrency(lit.amount)}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AI Summary Button */}
          <div className="c-bg-card rounded-xl border c-border p-5" style={{ boxShadow: "var(--shadow-sm)" }}>
            <button
              onClick={loadAISummary}
              disabled={aiLoading}
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              style={{ backgroundColor: "var(--accent)", color: "var(--accent-text)" }}
            >
              <Bot className="w-4 h-4" />
              {aiLoading ? "Generating..." : "Generate AI Credit Risk Summary"}
            </button>
            {aiSummary && (
              <div className="mt-4 p-4 c-bg-dark rounded-lg">
                <MarkdownRenderer content={aiSummary} />
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="c-bg-card rounded-xl border c-border p-12 text-center">
          <ShieldAlert className="w-12 h-12 c-text-3 mx-auto mb-4" />
          <p className="c-text-2 text-sm">Company not found or data not available.</p>
        </div>
      )}
    </PageShell>
  );
}
