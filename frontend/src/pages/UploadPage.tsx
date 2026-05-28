import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { ApiError, api } from "../api/client";
import type { IngestionBatch } from "../api/types";
import { StatusBadge } from "../components/StatusBadge";

const SOURCES = [
  {
    id: "SAP",
    label: "SAP",
    hint: "Fuel & procurement — German semicolon CSV (ME2N-style export)",
    sample: "sap_export_de.csv",
  },
  {
    id: "UTILITY",
    label: "Utility",
    hint: "Electricity — portal CSV with usage_kwh and billing dates",
    sample: "utility_portal.csv",
  },
  {
    id: "TRAVEL",
    label: "Travel",
    hint: "Business travel — Concur-style segment export",
    sample: "travel_concur_style.csv",
  },
] as const;

export function UploadPage() {
  const [tab, setTab] = useState<(typeof SOURCES)[number]["id"]>("SAP");
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<IngestionBatch | null>(null);
  const [error, setError] = useState("");
  const queryClient = useQueryClient();

  const upload = useMutation({
    mutationFn: () => {
      if (!file) throw new Error("Choose a CSV file first");
      return api.uploadBatch(tab, file);
    },
    onSuccess: (batch) => {
      setResult(batch);
      setError("");
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["activities"] });
      queryClient.invalidateQueries({ queryKey: ["batches"] });
    },
    onError: (err) => {
      setResult(null);
      setError(err instanceof ApiError ? err.message : "Upload failed");
    },
  });

  const active = SOURCES.find((s) => s.id === tab)!;

  return (
    <div className="mx-auto max-w-xl">
      <header className="text-center">
        <h1 className="mb-1 mt-0 text-5xl font-bold">Upload data</h1>
        <p className="mb-5 mt-0 text-slate-600">
          Import client files from SAP, utility portals, or travel systems.
        </p>
      </header>

      <div className="mb-4 flex justify-center gap-1">
        {SOURCES.map((s) => (
          <button
            key={s.id}
            type="button"
            className={[
              "select-none rounded-t-md border px-4 py-2 font-semibold caret-transparent",
              tab === s.id
                ? "border-emerald-700 bg-emerald-700 text-white"
                : "border-slate-300 bg-white",
            ].join(" ")}
            onClick={() => {
              setTab(s.id);
              setFile(null);
              setResult(null);
              setError("");
            }}
          >
            {s.label}
          </button>
        ))}
      </div>

      <section className="mx-auto max-w-xl rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <p className="text-slate-500">{active.hint}</p>
        <p className="text-sm">
          Sample file: <code>sample_data/{active.sample}</code>
        </p>

        <div
          className="relative my-4 rounded-xl border-2 border-dashed border-slate-300 p-8 text-center"
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            const f = e.dataTransfer.files[0];
            if (f) setFile(f);
          }}
        >
          <input
            type="file"
            accept=".csv,text/csv"
            id="file-input"
            className="absolute inset-0 cursor-pointer opacity-0"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
          <label htmlFor="file-input" className="flex flex-col gap-1">
            {file ? (
              <>
                <strong>{file.name}</strong>
                <span className="text-slate-500">Click or drop to replace</span>
              </>
            ) : (
              <>
                <strong>Drop CSV here</strong>
                <span className="text-slate-500">or click to browse</span>
              </>
            )}
          </label>
        </div>

        {error && (
          <div className="mb-4 rounded-lg border border-rose-300 bg-rose-50 px-4 py-3 text-rose-700">
            {error}
          </div>
        )}

        <div className="flex justify-center">
          <button
            type="button"
            className="cursor-pointer rounded-md bg-emerald-700 px-4 py-2 text-sm font-medium text-white transition hover:bg-emerald-800 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={!file || upload.isPending}
            onClick={() => upload.mutate()}
          >
            {upload.isPending ? "Uploading…" : `Upload ${active.label} file`}
          </button>
        </div>

        {result && (
          <div
            className={[
              "mt-6 rounded-xl p-4",
              result.status === "failed"
                ? "border border-rose-300 bg-rose-50"
                : "border border-green-300 bg-green-50",
            ].join(" ")}
          >
            <h3>
              Upload complete <StatusBadge status={result.status} />
            </h3>
            <ul className="flex list-none gap-6 p-0">
              <li className="flex flex-col">
                <span>Total rows</span>
                <strong>{result.row_count_total}</strong>
              </li>
              <li className="flex flex-col">
                <span>Imported successfully</span>
                <strong>{result.row_count_success}</strong>
              </li>
              <li className="flex flex-col">
                <span>Failed to parse</span>
                <strong>{result.row_count_failed}</strong>
              </li>
            </ul>
            {result.error_summary?.length > 0 && (
              <details>
                <summary>Parse errors ({result.error_summary.length})</summary>
                <ul className="text-sm">
                  {result.error_summary.map((e) => (
                    <li key={e.row}>
                      Row {e.row}: {e.errors.join("; ")}
                    </li>
                  ))}
                </ul>
              </details>
            )}
            {result.row_count_success > 0 && (
              <p>
                <a href="/review?review_status=pending">Go to review queue →</a>
              </p>
            )}
          </div>
        )}
      </section>
    </div>
  );
}
