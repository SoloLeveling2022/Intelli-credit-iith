"use client";

import { useState } from "react";
import PageShell from "@/components/PageShell";
import {
  triggerVoiceAgentCall,
  fetchVoiceAgentTranscript,
  extractTranscriptText,
  summarizeTranscriptWithGemini,
} from "@/lib/api";
import {
  Phone,
  Loader2,
  CheckCircle2,
  AlertCircle,
  Download,
  Copy,
  Clock,
} from "lucide-react";

export default function PrimaryInsightsPage() {
  const [callStatus, setCallStatus] = useState<"idle" | "calling" | "completed" | "error">("idle");
  const [callExecutionId, setCallExecutionId] = useState<string | null>(null);
  const [callTranscript, setCallTranscript] = useState<string | null>(null);
  const [callSummary, setCallSummary] = useState<{
    summary: string;
    risk_insights: string[];
    recommendations: string[];
  } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [fetchingTranscript, setFetchingTranscript] = useState(false);

  // Environment variables
  const RECIPIENT_PHONE = process.env.NEXT_PUBLIC_VOICE_AGENT_RECIPIENT_PHONE || "+918019227239";
  const FROM_PHONE = process.env.NEXT_PUBLIC_VOICE_AGENT_FROM_PHONE || "+13185269358";
  const DEMO_CIN = process.env.NEXT_PUBLIC_DEMO_CIN || "U72200KA2007PTC043114";
  const DEMO_COMPANY_NAME = process.env.NEXT_PUBLIC_DEMO_COMPANY_NAME || "Example Tech Private Limited";

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const handleDemoCall = async () => {
    setCallStatus("calling");
    setError(null);
    setCallExecutionId(null);
    setCallTranscript(null);
    setCallSummary(null);

    try {
      const response = await triggerVoiceAgentCall({
        recipient_phone_number: RECIPIENT_PHONE,
        from_phone_number: FROM_PHONE,
        company_data: {
          cin: DEMO_CIN,
          legal_name: DEMO_COMPANY_NAME,
          industry: "Manufacturing/Services",
          revenue: "₹50 Cr (estimated)",
          loan_requested: "₹10 Cr",
        },
      });

      setCallExecutionId(response.execution_id);
      setCallStatus("completed");

      alert(
        `✓ Call initiated successfully!\n\nExecution ID: ${response.execution_id}\n\nThe AI will now call ${RECIPIENT_PHONE}.\n\nExpected call duration: 2-5 minutes.\n\nClick "Fetch Transcript" after the call completes.`
      );
    } catch (err: any) {
      setError(err.message || "Failed to initiate call");
      setCallStatus("error");
    }
  };

  const handleFetchTranscript = async () => {
    if (!callExecutionId) {
      setError("No execution ID found. Please initiate a call first.");
      return;
    }

    setFetchingTranscript(true);
    setError(null);

    try {
      const transcriptData = await fetchVoiceAgentTranscript(callExecutionId);

      if (transcriptData.status !== "completed") {
        setError(
          `Call still in progress (status: ${transcriptData.status}). Please wait and try again.`
        );
        setFetchingTranscript(false);
        return;
      }

      // Extract transcript text from conversation array
      const transcriptText = extractTranscriptText(transcriptData);
      setCallTranscript(transcriptText);

      // Send extracted transcript to backend for analysis
      const summary = await summarizeTranscriptWithGemini(transcriptText);
      setCallSummary(summary);
    } catch (err: any) {
      setError(err.message || "Failed to fetch transcript");
    } finally {
      setFetchingTranscript(false);
    }
  };

  return (
    <PageShell
      title="Primary Insights - AI Verification Call"
      description="Conduct AI-powered verification calls with company representatives to gather qualitative credit assessment insights"
    >
      {/* Intro Card */}
      <div
        className="c-bg-card rounded-xl border c-border p-6 mb-6"
        style={{ boxShadow: "var(--shadow-sm)" }}
      >
        <h2 className="text-lg font-semibold c-text mb-3">Demo Call Details</h2>
        <div className="space-y-3 text-sm c-text-2">
          <div className="p-4 c-bg-dark rounded-lg border c-border space-y-2">
            <p className="text-xs c-text-3 font-mono">
              <span className="font-medium text-blue-400">Company:</span> {DEMO_COMPANY_NAME}
            </p>
            <p className="text-xs c-text-3 font-mono">
              <span className="font-medium text-green-400">CIN:</span> {DEMO_CIN}
            </p>
            <p className="text-xs c-text-3 font-mono">
              <span className="font-medium text-yellow-400">Recipient:</span> {RECIPIENT_PHONE}
            </p>
          </div>
          <p className="text-sm">
            Click the button below to initiate an AI-powered verification call. The AI agent will
            conduct a 2-5 minute structured interview covering business operations, financial
            health, and credit capacity.
          </p>
        </div>
      </div>

      {/* Demo Call Button */}
      <div
        className="c-bg-card rounded-xl border c-border p-8 mb-6 text-center"
        style={{ boxShadow: "var(--shadow-sm)" }}
      >
        {error && (
          <div className="flex items-start gap-3 p-3 mb-4 bg-red-500/10 border border-red-500/20 rounded-lg">
            <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        <button
          onClick={handleDemoCall}
          disabled={callStatus === "calling"}
          className="flex items-center justify-center gap-3 px-8 py-4 rounded-lg text-lg font-semibold transition-all disabled:opacity-50 mx-auto"
          style={{ backgroundColor: "var(--accent)", color: "var(--accent-text)" }}
        >
          {callStatus === "calling" ? (
            <>
              <Loader2 className="w-6 h-6 animate-spin" />
              Initiating Call...
            </>
          ) : (
            <>
              <Phone className="w-6 h-6" />
              Initiate Demo Call
            </>
          )}
        </button>
      </div>

      {/* Call Status Card */}
      {callExecutionId && (
        <div
          className="c-bg-card rounded-xl border c-border p-6 mb-6"
          style={{ boxShadow: "var(--shadow-sm)" }}
        >
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-base font-semibold c-text">Call In Progress / Completed</h3>
              <p className="text-sm c-text-3 mt-1">
                <Clock className="w-4 h-4 inline mr-1" />
                Initiated at {new Date().toLocaleTimeString()}
              </p>
            </div>
            <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0" />
          </div>

          <div className="p-4 c-bg-dark rounded-lg border c-border mb-4">
            <p className="text-xs c-text-3 font-medium mb-2">Execution ID:</p>
            <div className="flex items-center gap-2">
              <code className="flex-1 text-xs bg-gray-900 px-3 py-2 rounded font-mono">
                {callExecutionId}
              </code>
              <button
                onClick={() => copyToClipboard(callExecutionId)}
                className="p-2 hover:c-bg-card rounded transition-colors"
              >
                <Copy className="w-4 h-4 c-text-2" />
              </button>
            </div>
          </div>

          <button
            onClick={handleFetchTranscript}
            disabled={fetchingTranscript}
            className="flex items-center justify-center gap-2 w-full px-4 py-3 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
            style={{
              backgroundColor: "var(--accent)",
              color: "var(--accent-text)",
            }}
          >
            {fetchingTranscript ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Fetching Transcript...
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                Fetch & Analyze Transcript
              </>
            )}
          </button>

          <p className="text-xs c-text-3 mt-3 text-center">
            ⏱️ Wait for call to complete before fetching (typically 2-5 minutes)
          </p>
        </div>
      )}

      {/* Transcript & Summary Card */}
      {callSummary && (
        <div
          className="c-bg-card rounded-xl border c-border p-6"
          style={{ boxShadow: "var(--shadow-sm)" }}
        >
          <h3 className="text-base font-semibold c-text mb-4 flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            AI Analysis Results
          </h3>

          {/* Summary Section */}
          <div className="mb-6">
            <h4 className="text-sm font-semibold c-text mb-2">Summary</h4>
            <div className="p-4 c-bg-dark rounded-lg border c-border">
              <p className="text-sm c-text-2 leading-relaxed">{callSummary.summary}</p>
            </div>
          </div>

          {/* Risk Insights Section */}
          {callSummary.risk_insights && callSummary.risk_insights.length > 0 && (
            <div className="mb-6">
              <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-red-400" />
                <span className="text-red-400">Risk Insights</span>
              </h4>
              <div className="space-y-2">
                {callSummary.risk_insights.map((insight, idx) => (
                  <div key={idx} className="flex gap-3 p-3 c-bg-dark rounded-lg border c-border">
                    <span className="text-red-400 shrink-0 mt-0.5">⚠</span>
                    <p className="text-sm c-text-2">{insight}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations Section */}
          {callSummary.recommendations && callSummary.recommendations.length > 0 && (
            <div className="mb-6">
              <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-blue-400" />
                <span className="text-blue-400">Recommendations</span>
              </h4>
              <div className="space-y-2">
                {callSummary.recommendations.map((rec, idx) => (
                  <div key={idx} className="flex gap-3 p-3 c-bg-dark rounded-lg border c-border">
                    <span className="text-blue-400 shrink-0 mt-0.5">✓</span>
                    <p className="text-sm c-text-2">{rec}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Full Transcript */}
          {callTranscript && (
            <details className="cursor-pointer">
              <summary className="text-sm font-semibold c-text mb-3 p-3 c-bg-dark rounded-lg hover:c-bg-card transition-colors">
                📋 View Full Transcript
              </summary>
              <div className="mt-3 p-4 c-bg-dark rounded-lg border c-border max-h-96 overflow-y-auto">
                <pre className="text-xs c-text-3 whitespace-pre-wrap font-mono">
                  {callTranscript}
                </pre>
              </div>
            </details>
          )}
        </div>
      )}

      {/* Empty State */}
      {!callExecutionId && (
        <div className="text-center py-12 text-gray-500">
          <Phone className="w-16 h-16 mx-auto mb-4 opacity-30" />
          <p className="text-sm">Ready to initiate demo call</p>
        </div>
      )}
    </PageShell>
  );
}
