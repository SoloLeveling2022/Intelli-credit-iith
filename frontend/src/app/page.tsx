"use client";

import { useState, useEffect } from "react";
import {
  Shield,
  GitCompare,
  Network,
  FileSearch,
  BarChart3,
  ArrowRight,
  CheckCircle2,
  Sun,
  Moon,
  Building2,
  Receipt,
  Scale,
} from "lucide-react";
import { useTheme } from "@/hooks/useTheme";

/* ───────── Feature data ───────── */
const FEATURES = [
  {
    icon: Building2,
    title: "Five C's Credit Appraisal Engine",
    desc: "Standardized Character, Capacity, Capital, Collateral, and Conditions scoring reduces analyst subjectivity and improves decision consistency.",
  },
  {
    icon: Network,
    title: "Knowledge Graph Risk Discovery",
    desc: "Neo4j graph traversal connects companies, promoters, documents, and transactions to expose hidden related-party and shell-company networks.",
  },
  {
    icon: Shield,
    title: "Shell & Circular Transaction Detection",
    desc: "Detects closed trading loops, round-tripping patterns, and suspicious transaction chains that are hard to catch in manual spreadsheet reviews.",
  },
  {
    icon: Receipt,
    title: "Revenue Cross-Verification",
    desc: "Cross-checks ITR income, bank inflows, and financial statement figures to flag material inconsistencies before approval.",
  },
  {
    icon: Scale,
    title: "Automated CAM Generation",
    desc: "Generates structured Credit Appraisal Memos with risk indicators, rationale, and recommendation drafts for faster sanction workflows.",
  },
  {
    icon: GitCompare,
    title: "GST Reconciliation & ITC Control",
    desc: "Matches GSTR-1, GSTR-2B, and GSTR-3B with invoice-level checks to prevent excess ITC claims and compliance leakage.",
  },
  {
    icon: FileSearch,
    title: "AI Explanations & Audit Trail",
    desc: "LLM-powered narratives convert raw anomalies into investigation-ready explanations for compliance teams, credit committees, and auditors.",
  },
  {
    icon: BarChart3,
    title: "Portfolio Monitoring Dashboard",
    desc: "Track approval quality, risk concentration, mismatch trends, and exposure metrics from one operational control tower.",
  },
  {
    icon: Shield,
    title: "Due Diligence & External Research",
    desc: "Enriches internal analysis with litigation checks, MCA data, and external risk context for stronger underwriting decisions.",
  },
];

const STATS = [
  { value: "5C", label: "Automated Credit Framework" },
  { value: "360°", label: "Company Risk View" },
  { value: "15+", label: "Risk Signals & Mismatch Types" },
  { value: "24/7", label: "Decision-Ready Monitoring" },
];

const COMPLIANCE = [
  "Cut manual credit appraisal turnaround time",
  "Unify bank, ITR, financial statement verification",
  "Detect shell networks and circular transactions",
  "Standardize underwriting with Five C's scoring",
  "Generate CAM drafts with AI explanations",
  "Control ITC risk via GST return reconciliation",
];

export default function LoginPage() {
  const { isDark, toggleTheme } = useTheme();

  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  return (
    <div className="min-h-screen c-bg-main relative overflow-x-hidden">
      {/* ─── Sticky top bar ─── */}
      <header
        className="sticky top-0 z-40 w-full border-b backdrop-blur-md"
        style={{
          backgroundColor: isDark
            ? "rgba(17,17,17,0.85)"
            : "rgba(245,244,239,0.85)",
          borderColor: "var(--bg-border)",
        }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <img
              src="/intelli-credit-logo.png"
              alt="Intelli-Credit"
              className="w-8 h-8 rounded-lg"
            />
            <span className="text-sm font-bold tracking-tight c-text">
              Intelli-Credit
            </span>
            <span
              className="hidden sm:inline text-[10px] font-medium px-1.5 py-0.5 rounded"
              style={{
                backgroundColor: "var(--accent-light)",
                color: "var(--text-secondary)",
              }}
            >
              AI Credit Appraisal
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg transition-colors"
              style={{ color: "var(--text-secondary)" }}
              aria-label="Toggle theme"
            >
              {isDark ? (
                <Sun className="w-4 h-4" />
              ) : (
                <Moon className="w-4 h-4" />
              )}
            </button>
            <a
              href="/login"
              className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium c-bg-accent transition-colors"
            >
              Sign In
              <ArrowRight className="w-3 h-3" />
            </a>
          </div>
        </div>
      </header>

      {/* ─── Hero Section ─── */}
      <section className="relative">
        {/* Background decorative elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div
            className="absolute -top-40 -right-40 w-80 h-80 rounded-full blur-[100px] transition-opacity duration-1000"
            style={{
              backgroundColor: isDark
                ? "rgba(255,255,255,0.03)"
                : "rgba(0,0,0,0.03)",
              opacity: mounted ? 1 : 0,
            }}
          />
          <div
            className="absolute top-60 -left-20 w-72 h-72 rounded-full blur-[80px] transition-opacity duration-1000 delay-300"
            style={{
              backgroundColor: isDark
                ? "rgba(255,255,255,0.02)"
                : "rgba(0,0,0,0.02)",
              opacity: mounted ? 1 : 0,
            }}
          />
          {/* Grid pattern */}
          <div
            className="absolute inset-0"
            style={{
              backgroundImage: isDark
                ? "linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)"
                : "linear-gradient(rgba(0,0,0,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0,0,0,0.03) 1px, transparent 1px)",
              backgroundSize: "60px 60px",
            }}
          />
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 sm:pt-24 pb-16 sm:pb-20">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
            {/* Left — Hero copy */}
            <div className="space-y-8">
              <div className="space-y-4">
                <div
                  className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-[11px] font-medium border"
                  style={{
                    borderColor: "var(--bg-border)",
                    color: "var(--text-secondary)",
                    backgroundColor: "var(--bg-card)",
                  }}
                >
                  <Building2 className="w-3 h-3" />
                  Integrated Credit Appraisal + GST Intelligence
                </div>
                <h1
                  className="text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight leading-[1.1]"
                  style={{ color: "var(--text-primary)" }}
                >
                  Faster, Safer
                  <br />
                  <span style={{ color: "var(--text-tertiary)" }}>
                    Credit Decisions
                  </span>
                </h1>
                <p
                  className="text-base sm:text-lg leading-relaxed max-w-lg"
                  style={{ color: "var(--text-secondary)" }}
                >
                  Replace fragmented, manual appraisal workflows with a
                  knowledge-graph platform that validates documents, highlights
                  hidden risk, scores borrowers across Five C's, and supports
                  GST compliance from the same cockpit.
                </p>
              </div>

              {/* Stats row */}
              <div
                className="grid grid-cols-2 sm:grid-cols-4 gap-4 py-6 border-y"
                style={{ borderColor: "var(--bg-border)" }}
              >
                {STATS.map((s) => (
                  <div key={s.label}>
                    <div
                      className="text-xl sm:text-2xl font-bold tracking-tight"
                      style={{ color: "var(--text-primary)" }}
                    >
                      {s.value}
                    </div>
                    <div
                      className="text-[11px] mt-0.5"
                      style={{ color: "var(--text-tertiary)" }}
                    >
                      {s.label}
                    </div>
                  </div>
                ))}
              </div>

              {/* GST compliance checklist */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {COMPLIANCE.map((item) => (
                  <div
                    key={item}
                    className="flex items-center gap-2 text-[13px]"
                    style={{ color: "var(--text-secondary)" }}
                  >
                    <CheckCircle2 className="w-3.5 h-3.5 shrink-0 text-emerald-500" />
                    {item}
                  </div>
                ))}
              </div>
            </div>

            {/* Right — Reserved space for interactive Spline model */}
            <div id="login-section" className="hidden lg:flex justify-center lg:justify-end">
              <div className="w-full max-w-360 min-h-130 group">
                <iframe
                  src="https://my.spline.design/nexbotrobotcharacterconcept-22637c44a77736a58365c65e225a8d97/"
                  frameBorder="0"
                  width="100%"
                  height="100%"
                  className="w-full h-full rounded-2xl transform transition-transform duration-500"
                  title="NexBot Robot Character"
                />
                <span className="absolute right-44 bottom-32 z-50 bg-white dark:bg-gray-800 text-xs font-semibold px-8 py-3 rounded shadow-md">
                  Credit Appraisal System
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Features Section ─── */}
      <section
        className="border-t"
        style={{
          borderColor: "var(--bg-border)",
          backgroundColor: "var(--bg-card)",
        }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
          <div className="text-center mb-12 sm:mb-16">
            <div
              className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-[11px] font-medium border mb-4"
              style={{
                borderColor: "var(--bg-border)",
                color: "var(--text-secondary)",
                backgroundColor: "var(--bg-main)",
              }}
            >
              <Shield className="w-3 h-3" />
              Core + Extended Capabilities
            </div>
            <h2
              className="text-2xl sm:text-3xl font-bold tracking-tight"
              style={{ color: "var(--text-primary)" }}
            >
              Built Around Core Underwriting Problems
            </h2>
            <p
              className="text-sm sm:text-base mt-3 max-w-2xl mx-auto"
              style={{ color: "var(--text-secondary)" }}
            >
              Designed for lenders and finance teams that need faster
              turnaround, stronger verification, and explainable risk decisions.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
            {FEATURES.map((f) => (
              <div
                key={f.title}
                className="group rounded-xl border p-5 sm:p-6 transition-all duration-200"
                style={{
                  borderColor: "var(--bg-border)",
                  backgroundColor: "var(--bg-main)",
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLElement).style.borderColor =
                    "var(--accent)";
                  (e.currentTarget as HTMLElement).style.boxShadow =
                    "var(--shadow-md)";
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLElement).style.borderColor =
                    "var(--bg-border)";
                  (e.currentTarget as HTMLElement).style.boxShadow = "none";
                }}
              >
                <div
                  className="w-9 h-9 rounded-lg flex items-center justify-center mb-4"
                  style={{
                    backgroundColor: "var(--accent-light)",
                    color: "var(--accent)",
                  }}
                >
                  <f.icon className="w-4.5 h-4.5" />
                </div>
                <h3
                  className="text-sm font-semibold mb-2"
                  style={{ color: "var(--text-primary)" }}
                >
                  {f.title}
                </h3>
                <p
                  className="text-[13px] leading-relaxed"
                  style={{ color: "var(--text-secondary)" }}
                >
                  {f.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── How It Works ─── */}
      <section
        className="border-t"
        style={{ borderColor: "var(--bg-border)" }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
          <div className="text-center mb-12">
            <h2
              className="text-2xl sm:text-3xl font-bold tracking-tight"
              style={{ color: "var(--text-primary)" }}
            >
              How It Works
            </h2>
            <p
              className="text-sm sm:text-base mt-3 max-w-xl mx-auto"
              style={{ color: "var(--text-secondary)" }}
            >
              From document ingestion to committee-ready recommendation in three
              operational steps.
            </p>
          </div>

          <div className="grid sm:grid-cols-3 gap-6 sm:gap-8">
            {[
              {
                step: "01",
                title: "Ingest Financial + Compliance Data",
                desc: "Upload bank statements, ITRs, financial statements, and GST returns in supported formats. The platform standardizes and links records automatically.",
              },
              {
                step: "02",
                title: "Run Graph-Powered Risk Analysis",
                desc: "The engine performs Five C's scoring, cross-verification, shell network checks, and GST mismatch detection to produce a consolidated risk view.",
              },
              {
                step: "03",
                title: "Generate Decision Artifacts",
                desc: "Produce CAM-ready narratives, risk indicators, and actionable recommendations for credit committee review and compliance audit trails.",
              },
            ].map((s) => (
              <div key={s.step} className="relative">
                <div
                  className="text-5xl sm:text-6xl font-black tracking-tighter opacity-10 mb-3"
                  style={{ color: "var(--text-primary)" }}
                >
                  {s.step}
                </div>
                <h3
                  className="text-sm font-semibold mb-2"
                  style={{ color: "var(--text-primary)" }}
                >
                  {s.title}
                </h3>
                <p
                  className="text-[13px] leading-relaxed"
                  style={{ color: "var(--text-secondary)" }}
                >
                  {s.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── CTA Banner ─── */}
      <section
        className="border-t"
        style={{
          borderColor: "var(--bg-border)",
          backgroundColor: "var(--accent)",
        }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 text-center">
          <h2
            className="text-xl sm:text-2xl font-bold tracking-tight mb-3"
            style={{ color: "var(--accent-text)" }}
          >
            Ready to modernize credit appraisal operations?
          </h2>
          <p
            className="text-sm mb-6 max-w-lg mx-auto"
            style={{ color: "var(--accent-text)", opacity: 0.7 }}
          >
            Join teams using one intelligent platform for underwriting,
            explainable risk, CAM preparation, and GST control.
          </p>
          <a
            href="/login"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all"
            style={{
              backgroundColor: "var(--bg-main)",
              color: "var(--text-primary)",
            }}
          >
            Get Started
            <ArrowRight className="w-4 h-4" />
          </a>
        </div>
      </section>

      {/* ─── Footer ─── */}
      <footer
        className="border-t"
        style={{
          borderColor: "var(--bg-border)",
          backgroundColor: "var(--bg-card)",
        }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <img
                src="/intelli-credit-logo.png"
                alt="Intelli-Credit"
                className="w-6 h-6 rounded-md"
              />
              <span
                className="text-xs font-semibold"
                style={{ color: "var(--text-primary)" }}
              >
                Intelli-Credit
              </span>
            </div>
            <p
              className="text-[11px] text-center sm:text-right"
              style={{ color: "var(--text-tertiary)" }}
            >
              &copy; {new Date().getFullYear()} Intelli-Credit — AI-Powered
              Credit Appraisal & GST Compliance Platform. Built with Neo4j Knowledge Graph.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
