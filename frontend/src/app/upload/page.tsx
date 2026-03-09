"use client";

import { useState, useCallback, useRef } from "react";
import PageShell from "@/components/PageShell";
import { uploadDocument, uploadCompanies } from "@/lib/api";
import { FileUp, CheckCircle2, XCircle, File, Trash2 } from "lucide-react";

type UploadResult = {
  status: string;
  records_ingested?: number;
  companies_ingested?: number;
  taxpayers_ingested?: number;
  doc_type?: string;
  error?: string;
};

export default function UploadPage() {
  const [docType, setDocType] = useState("FINANCIAL_STATEMENTS");
  const [results, setResults] = useState<UploadResult[]>([]);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState<"document" | "company" | null>(null);
  const [stagedDocuments, setStagedDocuments] = useState<File[]>([]);
  const [stagedCompanies, setStagedCompanies] = useState<File[]>([]);
  const documentInputRef = useRef<HTMLInputElement>(null);
  const companyInputRef = useRef<HTMLInputElement>(null);

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const stageFiles = (files: FileList | null, isTaxpayer: boolean) => {
    if (!files?.length) return;
    const arr = Array.from(files);
    if (isTaxpayer) setStagedCompanies((prev) => [...prev, ...arr]);
    else setStagedDocuments((prev) => [...prev, ...arr]);
  };

  const handleUpload = useCallback(
    async (files: FileList | null, isTaxpayer = false) => {
      if (!files?.length) return;
      setUploading(true);
      const newResults: UploadResult[] = [];

      for (const file of Array.from(files)) {
        try {
          const res = isTaxpayer
            ? await uploadCompanies(file)
            : await uploadDocument(file, docType);
          newResults.push(res);
        } catch (err) {
          newResults.push({
            status: "error",
            error: err instanceof Error ? err.message : "Upload failed",
          });
        }
      }

      setResults((prev) => [...newResults, ...prev]);
      setUploading(false);
    },
    [docType]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent, isTaxpayer: boolean) => {
      e.preventDefault();
      setDragOver(null);
      stageFiles(e.dataTransfer.files, isTaxpayer);
    },
    []
  );

  return (
    <PageShell
      title="Upload Documents"
      description="Upload credit appraisal documents and company master data (JSON / CSV)"
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* Document Upload */}
        <div className="c-bg-card rounded-xl border c-border p-6" style={{ boxShadow: "var(--shadow-sm)" }}>
          <h2 className="text-lg font-semibold c-text mb-4">
            Credit Documents
          </h2>
          <div className="space-y-4">
            <div>
              <label className="text-sm c-text-2 block mb-1">
                Document Type
              </label>
              <select
                value={docType}
                onChange={(e) => setDocType(e.target.value)}
                className="w-full rounded-lg px-3 py-2 text-sm outline-none"
              >
                <option value="FINANCIAL_STATEMENTS">Financial Statements</option>
                <option value="BANK_STATEMENTS">Bank Statements</option>
                <option value="GST_RETURNS">GST Returns</option>
                <option value="ITR">Income Tax Returns</option>
                <option value="BUREAU_REPORT">Bureau Report</option>
                <option value="KYC">KYC Documents</option>
              </select>
            </div>
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setDragOver("document");
              }}
              onDragLeave={() => setDragOver(null)}
              onDrop={(e) => handleDrop(e, false)}
              onClick={() => documentInputRef.current?.click()}
              className={`flex flex-col items-center justify-center border-2 border-dashed rounded-lg p-8 cursor-pointer transition-all ${
                dragOver === "document"
                  ? "border-white/60 c-bg-accent-light"
                  : "c-border hover:border-white/60/40 hover:c-bg-dark"
              }`}
            >
              <FileUp
                className={`w-8 h-8 mb-2 transition-colors ${dragOver === "document" ? "c-text-accent" : "c-text-3"}`}
              />
              <span className="text-sm c-text-2">
                {dragOver === "document"
                  ? "Drop files here"
                  : "Drag & drop CSV/JSON or click to upload"}
              </span>
              <input
                ref={documentInputRef}
                type="file"
                accept=".json,.csv"
                multiple
                className="hidden"
                onChange={(e) => stageFiles(e.target.files, false)}
                disabled={uploading}
              />
            </div>
            {/* Document File Preview */}
            {stagedDocuments.length > 0 && (
              <div className="space-y-2">
                {stagedDocuments.map((f, i) => (
                  <div key={i} className="flex items-center gap-2 px-3 py-2 c-bg-dark rounded-lg">
                    <File className="w-4 h-4 c-text-accent shrink-0" />
                    <span className="text-sm c-text-2 truncate flex-1">{f.name}</span>
                    <span className="text-xs c-text-3 shrink-0">{formatFileSize(f.size)}</span>
                    <button onClick={() => setStagedDocuments((p) => p.filter((_, j) => j !== i))} className="p-1 hover:c-bg-card rounded transition-colors">
                      <Trash2 className="w-3 h-3 c-text-3" />
                    </button>
                  </div>
                ))}
                <button
                  onClick={async () => {
                    const dt = new DataTransfer();
                    stagedDocuments.forEach((f) => dt.items.add(f));
                    await handleUpload(dt.files, false);
                    setStagedDocuments([]);
                  }}
                  disabled={uploading}
                  className="w-full py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                  style={{ backgroundColor: "var(--accent)", color: "var(--accent-text)" }}
                >
                  Upload {stagedDocuments.length} file{stagedDocuments.length > 1 ? "s" : ""}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Company Upload */}
        <div className="c-bg-card rounded-xl border c-border p-6" style={{ boxShadow: "var(--shadow-sm)" }}>
          <h2 className="text-lg font-semibold c-text mb-4">
            Company Master
          </h2>
          <p className="text-sm c-text-2 mb-4">
            Upload company details (CIN, legal name, entity type, state)
          </p>
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver("company");
            }}
            onDragLeave={() => setDragOver(null)}
            onDrop={(e) => handleDrop(e, true)}
            onClick={() => companyInputRef.current?.click()}
            className={`flex flex-col items-center justify-center border-2 border-dashed rounded-lg p-8 cursor-pointer transition-all h-48 ${
              dragOver === "company"
                ? "border-white/60 c-bg-accent-light"
                : "c-border hover:border-white/60/40 hover:c-bg-dark"
            }`}
          >
            <FileUp
              className={`w-8 h-8 mb-2 transition-colors ${dragOver === "company" ? "c-text-accent" : "c-text-3"}`}
            />
            <span className="text-sm c-text-2">
              {dragOver === "company"
                ? "Drop files here"
                : "Drag & drop CSV/JSON or click to upload"}
            </span>
            <input
              ref={companyInputRef}
              type="file"
              accept=".json,.csv"
              className="hidden"
              onChange={(e) => stageFiles(e.target.files, true)}
              disabled={uploading}
            />
          </div>
          {/* Company File Preview */}
          {stagedCompanies.length > 0 && (
            <div className="space-y-2">
              {stagedCompanies.map((f, i) => (
                <div key={i} className="flex items-center gap-2 px-3 py-2 c-bg-dark rounded-lg">
                  <File className="w-4 h-4 c-text-accent shrink-0" />
                  <span className="text-sm c-text-2 truncate flex-1">{f.name}</span>
                  <span className="text-xs c-text-3 shrink-0">{formatFileSize(f.size)}</span>
                  <button onClick={() => setStagedCompanies((p) => p.filter((_, j) => j !== i))} className="p-1 hover:c-bg-card rounded transition-colors">
                    <Trash2 className="w-3 h-3 c-text-3" />
                  </button>
                </div>
              ))}
              <button
                onClick={async () => {
                  const dt = new DataTransfer();
                  stagedCompanies.forEach((f) => dt.items.add(f));
                  await handleUpload(dt.files, true);
                  setStagedCompanies([]);
                }}
                disabled={uploading}
                className="w-full py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                style={{ backgroundColor: "var(--accent)", color: "var(--accent-text)" }}
              >
                Upload {stagedCompanies.length} file{stagedCompanies.length > 1 ? "s" : ""}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Upload Progress */}
      {uploading && (
        <div className="flex items-center gap-3 p-4 mb-4 c-bg-accent-light border rounded-xl" style={{ borderColor: "var(--bg-border)" }}>
          <div className="animate-spin rounded-full h-5 w-5 border-2 border-t-transparent" style={{ borderColor: "var(--accent)", borderTopColor: "transparent" }} />
          <span className="text-sm c-text-accent">Processing upload...</span>
        </div>
      )}

      {/* Upload History */}
      {results.length > 0 && (
        <div className="c-bg-card rounded-xl border c-border p-6" style={{ boxShadow: "var(--shadow-sm)" }}>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold c-text">
              Upload Results
            </h2>
            <button
              onClick={() => setResults([])}
              className="text-xs c-text-3 hover:c-text-2"
            >
              Clear
            </button>
          </div>
          <div className="space-y-2">
            {results.map((r, i) => (
              <div
                key={i}
                className={`flex items-center gap-3 p-3 rounded-lg ${
                  r.status === "success"
                    ? "bg-emerald-500/5 border border-emerald-500/10"
                    : "bg-red-500/5 border border-red-500/10"
                }`}
              >
                {r.status === "success" ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-500 shrink-0" />
                )}
                <span className="text-sm c-text-2">
                  {r.status === "success"
                    ? `Ingested ${r.records_ingested ?? r.companies_ingested ?? r.taxpayers_ingested ?? 0} records${r.doc_type ? ` (${r.doc_type})` : ""}`
                    : r.error || "Upload failed"}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </PageShell>
  );
}
