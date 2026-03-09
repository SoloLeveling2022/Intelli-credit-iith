"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import PageShell from "@/components/PageShell";
import { StatCardSkeleton } from "@/components/Skeleton";
import {
  getDashboardStats,
  getAppraisalSummary,
  getTopRiskyCompanies,
  getLoanFlow,
  getTrendData,
} from "@/lib/api";
import { formatCurrency, formatNumber, severityColor } from "@/lib/utils";
import {
  AlertTriangle,
  TrendingUp,
  Building2,
  FileText,
  IndianRupee,
  ShieldAlert,
  Play,
  Network,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
} from "recharts";
import ITCSankeyChart from "@/components/ITCSankeyChart";

interface DashboardStats {
  total_companies: number;
  total_applications: number;
  total_transaction_value: number;
  total_appraisals: number;
  total_loan_amount_approved: number;
  high_risk_companies: number;
  gstr1_returns_filed: number;
  gstr2b_returns_generated: number;
  gstr3b_returns_filed: number;
  mismatch_breakdown: Record<string, number>;
  severity_breakdown: Record<string, number>;
}

interface AppraisalItem {
  decision_type: string;
  count: number;
  total_amount: number;
}

interface RiskyCompany {
  cin: string;
  legal_name: string;
  trade_name: string;
  risk_score: number;
  risk_level: string;
  mismatch_count: number;
  total_invoices: number;
  filing_rate: number;
}

const CHART_COLORS = ["#e5e5e5", "#a3a3a3", "#737373", "#d4d4d4", "#525252", "#8b8b8b"];
const SEVERITY_COLORS: Record<string, string> = {
  CRITICAL: "#d9534f",
  HIGH: "#f0ad4e",
  MEDIUM: "#a3a3a3",
  LOW: "#5cb85c",
};

const DECISION_SHORT: Record<string, string> = {
  APPROVED: "APPROVED",
  REJECTED: "REJECTED",
  PENDING: "PENDING",
  CONDITIONAL: "CONDITIONAL",
  UNDER_REVIEW: "UNDER_REVIEW",
};

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [appraisalData, setAppraisalData] = useState<AppraisalItem[]>([]);
  const [riskyCompanies, setRiskyCompanies] = useState<RiskyCompany[]>([]);
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);
  const [loanFlow, setLoanFlow] = useState<any>(null);
  const [trendData, setTrendData] = useState<any[]>([]);

  useEffect(() => {
    setMounted(true);
    Promise.allSettled([
      getDashboardStats(),
      getAppraisalSummary(),
      getTopRiskyCompanies(),
      getLoanFlow(),
      getTrendData(),
    ]).then(([statsRes, appraisalRes, companyRes, loanRes, trendRes]) => {
      if (statsRes.status === "fulfilled")
        setStats(statsRes.value as DashboardStats);
      if (appraisalRes.status === "fulfilled") {
        const data = appraisalRes.value as { breakdown: AppraisalItem[] };
        setAppraisalData(data.breakdown || []);
      }
      if (companyRes.status === "fulfilled") {
        const data = companyRes.value as {
          top_risky_companies?: RiskyCompany[];
          top_risky_vendors?: RiskyCompany[];
        };
        setRiskyCompanies(data.top_risky_companies || data.top_risky_vendors || []);
      }
      if (loanRes.status === "fulfilled") setLoanFlow(loanRes.value);
      if (trendRes.status === "fulfilled") {
        const data = trendRes.value as { periods: any[] };
        setTrendData(data.periods || []);
      }
      setLoading(false);
    });
  }, []);

  const severityData = stats?.severity_breakdown
    ? Object.entries(stats.severity_breakdown).map(([name, value]) => ({
        name,
        value,
      }))
    : [];

  return (
    <PageShell title="Dashboard" description="Credit Appraisal Overview">
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3 mb-8">
          {Array.from({ length: 6 }).map((_, i) => (
            <StatCardSkeleton key={i} />
          ))}
        </div>
      ) : (
        <>
          {/* Stat Cards with staggered fade-in */}
          <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-3 mb-6">
            {[
              { icon: Building2, label: "Companies", value: formatNumber(stats?.total_companies ?? 0), color: "#e5e5e5", desc: "Total companies assessed" },
              { icon: FileText, label: "Applications", value: formatNumber(stats?.total_applications ?? 0), color: "#a3a3a3", desc: "Total applications processed" },
              { icon: TrendingUp, label: "Txn Value", value: formatCurrency(stats?.total_transaction_value ?? 0), color: "#737373", desc: "Total transaction value" },
              { icon: AlertTriangle, label: "Appraisals", value: formatNumber(stats?.total_appraisals ?? 0), color: "#d4d4d4", desc: "Total appraisal decisions generated" },
              { icon: IndianRupee, label: "Loan Approved", value: formatCurrency(stats?.total_loan_amount_approved ?? 0), color: "#525252", desc: "Total loan amount approved" },
              { icon: ShieldAlert, label: "High Risk", value: formatNumber(stats?.high_risk_companies ?? 0), color: "#8b8b8b", desc: "High risk company count" },
            ].map((card, i) => (
              <div
                key={card.label}
                className="transition-all duration-500"
                style={{
                  opacity: mounted ? 1 : 0,
                  transform: mounted ? "translateY(0)" : "translateY(12px)",
                  transitionDelay: `${i * 80}ms`,
                }}
              >
                <StatCard {...card} />
              </div>
            ))}
          </div>

          {/* Quick Actions */}
          <div className="flex flex-wrap gap-2 mb-6">
            <Link
              href="/reconcile"
              className="flex items-center gap-2 px-4 py-2 c-bg-accent rounded-lg text-sm font-medium hover:opacity-90 transition-opacity"
              style={{ backgroundColor: "var(--accent)", color: "var(--accent-text)" }}
            >
              <Play className="w-3.5 h-3.5" /> New Appraisal
            </Link>
            <Link
              href="/graph"
              className="flex items-center gap-2 px-4 py-2 c-bg-dark hover:c-bg-card rounded-lg text-sm c-text-2 transition-colors border c-border"
            >
              <Network className="w-3.5 h-3.5" /> View Graph
            </Link>
          </div>

          {/* Charts Row: Decision + Severity Donut + Loan Pie */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
            {/* Decision Distribution Bar Chart */}
            <div className="c-bg-card rounded-xl border c-border p-5" style={{ boxShadow: "var(--shadow-sm)" }}>
              <h2 className="text-sm font-semibold c-text mb-4">Appraisal Decision Distribution</h2>
              {appraisalData.length > 0 ? (
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart
                    data={appraisalData.map((d) => ({
                      ...d,
                      label: DECISION_SHORT[d.decision_type] || d.decision_type,
                    }))}
                    margin={{ top: 5, right: 10, bottom: 5, left: -10 }}
                  >
                    <XAxis dataKey="label" tick={{ fill: "var(--text-tertiary)", fontSize: 10 }} axisLine={{ stroke: "var(--bg-border)" }} tickLine={false} />
                    <YAxis tick={{ fill: "var(--text-tertiary)", fontSize: 10 }} axisLine={{ stroke: "var(--bg-border)" }} tickLine={false} />
                    <Tooltip contentStyle={{ backgroundColor: "var(--bg-card)", border: "1px solid var(--bg-border)", borderRadius: "8px", color: "var(--text-primary)", fontSize: 12, boxShadow: "var(--shadow-md)" }} />
                    <Bar dataKey="count" radius={[3, 3, 0, 0]}>
                      {appraisalData.map((_, i) => (
                        <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <EmptyState text="No appraisal data. Start a new appraisal to view decisions." />
              )}
            </div>

            {/* Severity Distribution Donut */}
            <div className="c-bg-card rounded-xl border c-border p-5" style={{ boxShadow: "var(--shadow-sm)" }}>
              <h2 className="text-sm font-semibold c-text mb-4">Severity Distribution</h2>
              {severityData.length > 0 ? (
                <div className="flex flex-col items-center">
                  <ResponsiveContainer width="100%" height={180}>
                    <PieChart>
                      <Pie
                        data={severityData}
                        cx="50%" cy="50%"
                        innerRadius={45} outerRadius={75}
                        paddingAngle={4} dataKey="value" stroke="none"
                      >
                        {severityData.map((d) => (
                          <Cell key={d.name} fill={SEVERITY_COLORS[d.name] || "#6b6b6b"} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{ backgroundColor: "var(--bg-card)", border: "1px solid var(--bg-border)", borderRadius: "8px", color: "var(--text-primary)", fontSize: 12, boxShadow: "var(--shadow-md)" }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="flex flex-wrap justify-center gap-3 mt-2">
                    {severityData.map((d) => (
                      <div key={d.name} className="flex items-center gap-1.5">
                        <div className="w-2 h-2 rounded-full" style={{ backgroundColor: SEVERITY_COLORS[d.name] || "#6b6b6b" }} />
                        <span className={`text-xs font-medium px-1.5 py-0.5 rounded ${severityColor(d.name)}`}>
                          {d.name}: {d.value}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <EmptyState text="No severity data." />
              )}
            </div>

            {/* Loan Amount Pie */}
            <div className="c-bg-card rounded-xl border c-border p-5" style={{ boxShadow: "var(--shadow-sm)" }}>
              <h2 className="text-sm font-semibold c-text mb-4">Loan Amount by Decision Type</h2>
              {appraisalData.length > 0 ? (
                <div className="flex flex-col items-center">
                  <ResponsiveContainer width="100%" height={180}>
                    <PieChart>
                      <Pie
                        data={appraisalData.map((d) => ({ name: DECISION_SHORT[d.decision_type] || d.decision_type, value: d.total_amount }))}
                        cx="50%" cy="50%" innerRadius={45} outerRadius={75} paddingAngle={3} dataKey="value" stroke="none"
                      >
                        {appraisalData.map((_, i) => (
                          <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip contentStyle={{ backgroundColor: "var(--bg-card)", border: "1px solid var(--bg-border)", borderRadius: "8px", color: "var(--text-primary)", fontSize: 12, boxShadow: "var(--shadow-md)" }} formatter={(value) => [formatCurrency(Number(value ?? 0)), "Amount"]} />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="flex flex-wrap justify-center gap-x-3 gap-y-1 mt-2">
                    {appraisalData.map((d, i) => (
                      <div key={d.decision_type} className="flex items-center gap-1.5">
                        <div className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: CHART_COLORS[i % CHART_COLORS.length] }} />
                        <span className="text-[10px] c-text-3">{DECISION_SHORT[d.decision_type] || d.decision_type}</span>
                        <span className="text-[10px] c-text-2 font-mono">{formatCurrency(d.total_amount)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <EmptyState text="No data available." />
              )}
            </div>
          </div>

          {/* Top Risky Companies */}
          <div className="c-bg-card rounded-xl border c-border p-5" style={{ boxShadow: "var(--shadow-sm)" }}>
            <h2 className="text-sm font-semibold c-text mb-4">Top Risky Companies</h2>
            {riskyCompanies.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {riskyCompanies.slice(0, 6).map((v) => {
                  const rate = v.total_invoices > 0 ? Math.round((v.mismatch_count / v.total_invoices) * 100) : 0;
                  return (
                    <div
                      key={v.cin}
                      className="flex items-center justify-between p-3.5 rounded-lg c-bg-dark border c-border hover:c-border-accent transition-all cursor-default"
                      style={{ boxShadow: "var(--shadow-sm)" }}
                    >
                      <div className="min-w-0">
                        <p className="text-sm font-medium c-text truncate">{v.legal_name || v.trade_name || v.cin}</p>
                        <p className="text-[10px] c-text-3 font-mono mt-0.5">{v.cin}</p>
                      </div>
                      <div className="text-right shrink-0 ml-3">
                        <p className={`text-sm font-bold ${rate > 50 ? "text-red-400" : rate > 25 ? "text-amber-400" : "text-emerald-400"}`}>{rate}%</p>
                        <p className="text-[10px] c-text-3">{v.mismatch_count}/{v.total_invoices}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <EmptyState text="No company risk data available yet." />
            )}
          </div>

          {/* Loan Flow Sankey */}
          <div className="c-bg-card rounded-xl border c-border p-5 mt-6" style={{ boxShadow: "var(--shadow-sm)" }}>
            <h2 className="text-sm font-semibold c-text mb-4">Loan Flow Analysis</h2>
            {loanFlow ? (
              <>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                  {[
                    { label: "Total Applied", value: formatCurrency(loanFlow.summary?.total_applied || 0) },
                    { label: "Total Eligible", value: formatCurrency(loanFlow.summary?.total_eligible || 0) },
                    { label: "Approved", value: formatCurrency(loanFlow.summary?.total_approved || 0) },
                    { label: "At Risk", value: formatCurrency(loanFlow.summary?.total_at_risk || 0) },
                  ].map((item) => (
                    <div key={item.label} className="c-bg-dark rounded-lg p-3 text-center">
                      <p className="text-[10px] c-text-3">{item.label}</p>
                      <p className="text-sm font-bold c-text mt-1">{item.value}</p>
                    </div>
                  ))}
                </div>
                <ITCSankeyChart nodes={loanFlow.nodes || []} links={loanFlow.links || []} />
              </>
            ) : (
              <EmptyState text="No loan flow data available." />
            )}
          </div>

          {/* Trend Chart */}
          {trendData.length > 0 && (
            <div className="c-bg-card rounded-xl border c-border p-5 mt-6" style={{ boxShadow: "var(--shadow-sm)" }}>
              <h2 className="text-sm font-semibold c-text mb-4">Application Trends</h2>
              <ResponsiveContainer width="100%" height={280}>
                <AreaChart
                  data={trendData.map((item) => ({
                    ...item,
                    appraisals: item.appraisals ?? item.mismatches ?? 0,
                    applications: item.applications ?? item.invoices ?? 0,
                  }))}
                  margin={{ top: 5, right: 20, bottom: 5, left: 0 }}
                >
                  <XAxis dataKey="period" tick={{ fill: "var(--text-tertiary)", fontSize: 10 }} axisLine={{ stroke: "var(--bg-border)" }} tickLine={false} />
                  <YAxis tick={{ fill: "var(--text-tertiary)", fontSize: 10 }} axisLine={{ stroke: "var(--bg-border)" }} tickLine={false} />
                  <Tooltip contentStyle={{ backgroundColor: "var(--bg-card)", border: "1px solid var(--bg-border)", borderRadius: "8px", color: "var(--text-primary)", fontSize: 12, boxShadow: "var(--shadow-md)" }} />
                  <Area type="monotone" dataKey="appraisals" stroke="#a3a3a3" fill="#a3a3a3" fillOpacity={0.2} name="Appraisals" />
                  <Area type="monotone" dataKey="applications" stroke="#e5e5e5" fill="#e5e5e5" fillOpacity={0.1} name="Applications" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}
        </>
      )}
    </PageShell>
  );
}

function StatCard({ icon: Icon, label, value, color, desc }: {
  icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>;
  label: string;
  value: string;
  color: string;
  desc: string;
}) {
  return (
    <div
      className="c-bg-card rounded-xl border c-border p-4 hover:c-border-accent transition-all cursor-default group relative"
      style={{ boxShadow: "var(--shadow-sm)" }}
    >
      <div className="flex items-center gap-2 mb-2">
        <div className="p-1.5 rounded-md" style={{ backgroundColor: `${color}15`, color }}>
          <Icon className="w-3.5 h-3.5" style={{ color }} />
        </div>
        <span className="text-xs c-text-3">{label}</span>
      </div>
      <p className="text-lg font-bold c-text">{value}</p>
      <div
        className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-1.5 c-bg-card border c-border rounded-lg text-xs c-text-2 whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-10"
        style={{ boxShadow: "var(--shadow-lg)" }}
      >
        {desc}
      </div>
    </div>
  );
}

function EmptyState({ text }: { text: string }) {
  return <p className="c-text-3 text-sm py-8 text-center">{text}</p>;
}
