import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { ApiError, api } from "../api/client";
import type { Activity, ActivityDetail } from "../api/types";
import { FlagList } from "../components/FlagList";
import { StatusBadge } from "../components/StatusBadge";

export function ReviewPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [actionError, setActionError] = useState("");
  const queryClient = useQueryClient();

  const filters = {
    review_status: searchParams.get("review_status") ?? "",
    scope: searchParams.get("scope") ?? "",
    source: searchParams.get("source") ?? "",
    has_flags: searchParams.get("has_flags") ?? "",
  };

  const queryParams = useMemo(() => {
    const p: Record<string, string> = {};
    if (filters.review_status) p.review_status = filters.review_status;
    if (filters.scope) p.scope = filters.scope;
    if (filters.source) p.source = filters.source;
    if (filters.has_flags === "true") p.has_flags = "true";
    return p;
  }, [filters]);

  const { data, isLoading } = useQuery({
    queryKey: ["activities", queryParams],
    queryFn: () => api.listActivities(queryParams),
  });

  const { data: detail } = useQuery({
    queryKey: ["activity", selectedId],
    queryFn: () => api.getActivity(selectedId!),
    enabled: selectedId != null,
  });

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["activities"] });
    queryClient.invalidateQueries({ queryKey: ["activity", selectedId] });
    queryClient.invalidateQueries({ queryKey: ["dashboard"] });
  };

  const bulkApprove = useMutation({
    mutationFn: api.bulkApprove,
    onSuccess: (res) => {
      setActionError("");
      alert(`Approved ${res.approved_count} clean rows.`);
      invalidate();
    },
    onError: (e) => setActionError(e instanceof ApiError ? e.message : "Bulk approve failed"),
  });

  const activities = data?.results ?? [];

  function setFilter(key: string, value: string) {
    const next = new URLSearchParams(searchParams);
    if (value) next.set(key, value);
    else next.delete(key);
    setSearchParams(next);
  }

  return (
    <div className="grid items-start gap-6 lg:grid-cols-[1fr_380px]">
      <div>
        <header>
          <h1 className="mb-1 mt-0 text-5xl font-bold">Review queue</h1>
          <p className="mb-5 mt-0 text-slate-600">
            Approve rows before they are locked for audit.
          </p>
        </header>

        <div className="mb-4 flex flex-wrap items-center gap-2">
          <select
            value={filters.review_status}
            onChange={(e) => setFilter("review_status", e.target.value)}
            aria-label="Review status"
            className="rounded-md border border-slate-300 px-2.5 py-1.5"
          >
            <option value="">All statuses</option>
            <option value="pending">Pending</option>
            <option value="flagged">Flagged</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
          <select
            value={filters.scope}
            onChange={(e) => setFilter("scope", e.target.value)}
            aria-label="Scope"
            className="rounded-md border border-slate-300 px-2.5 py-1.5"
          >
            <option value="">All scopes</option>
            <option value="SCOPE_1">Scope 1</option>
            <option value="SCOPE_2">Scope 2</option>
            <option value="SCOPE_3">Scope 3</option>
          </select>
          <select
            value={filters.source}
            onChange={(e) => setFilter("source", e.target.value)}
            aria-label="Source"
            className="rounded-md border border-slate-300 px-2.5 py-1.5"
          >
            <option value="">All sources</option>
            <option value="SAP">SAP</option>
            <option value="UTILITY">Utility</option>
            <option value="TRAVEL">Travel</option>
          </select>
          <label className="flex items-center gap-1.5 text-sm">
            <input
              type="checkbox"
              checked={filters.has_flags === "true"}
              onChange={(e) => setFilter("has_flags", e.target.checked ? "true" : "")}
            />
            Has quality flags only
          </label>
          <button
            type="button"
            className="cursor-pointer rounded-md bg-emerald-50 px-4 py-2 text-sm font-medium text-emerald-700 transition hover:bg-emerald-100"
            disabled={bulkApprove.isPending}
            onClick={() => {
              if (confirm("Approve all pending rows with no quality flags?")) bulkApprove.mutate();
            }}
          >
            Bulk approve clean rows
          </button>
        </div>

        {actionError && (
          <div className="mb-4 rounded-lg border border-rose-300 bg-rose-50 px-4 py-3 text-rose-700">
            {actionError}
          </div>
        )}

        {isLoading ? (
          <p className="text-slate-500">Loading activities…</p>
        ) : activities.length === 0 ? (
          <p className="text-slate-500">
            No rows match these filters. Try uploading data first.
          </p>
        ) : (
          <table className="w-full overflow-hidden rounded-xl border border-slate-200 bg-white [border-collapse:collapse]">
            <thead>
              <tr>
                <th className="border-b border-slate-200 bg-slate-100 px-3 py-2 text-left text-xs uppercase tracking-wide text-slate-500">Source</th>
                <th className="border-b border-slate-200 bg-slate-100 px-3 py-2 text-left text-xs uppercase tracking-wide text-slate-500">Activity</th>
                <th className="border-b border-slate-200 bg-slate-100 px-3 py-2 text-left text-xs uppercase tracking-wide text-slate-500">Scope</th>
                <th className="border-b border-slate-200 bg-slate-100 px-3 py-2 text-left text-xs uppercase tracking-wide text-slate-500">Est. tCO₂e</th>
                <th className="border-b border-slate-200 bg-slate-100 px-3 py-2 text-left text-xs uppercase tracking-wide text-slate-500">Status</th>
                <th className="border-b border-slate-200 bg-slate-100 px-3 py-2 text-left text-xs uppercase tracking-wide text-slate-500">Flags</th>
              </tr>
            </thead>
            <tbody>
              {activities.map((a) => (
                <tr
                  key={a.id}
                  className={[
                    "cursor-pointer hover:bg-emerald-50",
                    selectedId === a.id ? "bg-emerald-100" : "",
                  ].join(" ")}
                  onClick={() => setSelectedId(a.id)}
                >
                  <td className="border-b border-slate-200 px-3 py-2">{a.batch_source}</td>
                  <td className="border-b border-slate-200 px-3 py-2">
                    <div>{a.activity_type}</div>
                    <span className="text-xs text-slate-500">
                      {a.activity_value} {a.activity_unit}
                    </span>
                  </td>
                  <td className="border-b border-slate-200 px-3 py-2">{a.scope.replace("SCOPE_", "")}</td>
                  <td className="border-b border-slate-200 px-3 py-2">{formatTonnes(a)}</td>
                  <td className="border-b border-slate-200 px-3 py-2">
                    <StatusBadge status={a.review_status} />
                    {a.is_locked && <span className="ml-1" title="Locked">🔒</span>}
                  </td>
                  <td className="border-b border-slate-200 px-3 py-2">{a.quality_flags.length || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <aside className="sticky top-4">
        {selectedId && detail ? (
          <ActivityDetailPanel
            activity={detail}
            onDone={() => {
              invalidate();
            }}
            onError={setActionError}
          />
        ) : (
          <div className="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center text-slate-500">
            Select a row to see details and take action.
          </div>
        )}
      </aside>
    </div>
  );
}

function formatTonnes(a: Activity) {
  const t = a.emission?.co2e_tonnes;
  if (!t) return "—";
  return Number(t).toFixed(4);
}

function ActivityDetailPanel({
  activity,
  onDone,
  onError,
}: {
  activity: ActivityDetail;
  onDone: () => void;
  onError: (msg: string) => void;
}) {
  const [reason, setReason] = useState("");
  const [pending, setPending] = useState(false);

  const { data: audit } = useQuery({
    queryKey: ["audit", activity.id],
    queryFn: () => api.activityAudit(activity.id),
  });

  async function run(action: "approve" | "flag" | "reject") {
    if ((action === "flag" || action === "reject") && !reason.trim()) {
      onError("Please enter a reason for flag or reject.");
      return;
    }
    setPending(true);
    onError("");
    try {
      if (action === "approve") await api.approveActivity(activity.id, reason);
      if (action === "flag") await api.flagActivity(activity.id, reason);
      if (action === "reject") await api.rejectActivity(activity.id, reason);
      setReason("");
      onDone();
    } catch (e) {
      onError(e instanceof ApiError ? e.message : "Action failed");
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="max-h-[calc(100vh-6rem)] overflow-y-auto rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="mt-0">Row #{activity.id}</h2>
      <StatusBadge status={activity.review_status} />
      {activity.is_locked && (
        <p className="mb-4 rounded-lg border border-amber-300 bg-amber-50 px-4 py-3 text-amber-900">
          This row is locked for audit.
        </p>
      )}

      <section className="mt-0 border-t-0 pt-0">
        <h3>Normalized data</h3>
        <dl className="m-0 grid grid-cols-[120px_1fr] gap-x-3 gap-y-1 text-sm">
          <dt className="m-0 text-slate-500">Activity</dt>
          <dd className="m-0">
            {activity.activity_value} {activity.activity_unit} ({activity.activity_type})
          </dd>
          <dt className="m-0 text-slate-500">Scope</dt>
          <dd className="m-0">
            {activity.scope} — {activity.scope_category}
          </dd>
          <dt className="m-0 text-slate-500">Period</dt>
          <dd className="m-0">
            {activity.period_start ?? "—"} → {activity.period_end ?? "—"}
          </dd>
          <dt className="m-0 text-slate-500">Facility / vendor</dt>
          <dd className="m-0">
            {activity.facility_code || "—"} / {activity.vendor_id || "—"}
          </dd>
          <dt className="m-0 text-slate-500">Source record</dt>
          <dd className="m-0">{activity.source_record_id || "—"}</dd>
        </dl>
      </section>

      {activity.emission && (
        <section className="mt-5 border-t border-slate-200 pt-4">
          <h3>Emission estimate</h3>
          <p>
            <strong>{Number(activity.emission.co2e_tonnes).toFixed(4)} tCO₂e</strong>
            <span className="text-slate-500"> ({activity.emission.confidence} confidence)</span>
          </p>
          <p className="text-xs text-slate-500">{activity.emission.factor_source}</p>
          <p className="text-xs text-slate-500">Method: {activity.emission.method}</p>
        </section>
      )}

      <section className="mt-5 border-t border-slate-200 pt-4">
        <h3>Quality flags</h3>
        <FlagList flags={activity.quality_flags} />
      </section>

      {activity.raw_row && (
        <section className="mt-5 border-t border-slate-200 pt-4">
          <h3>Original file row</h3>
          <pre className="max-h-52 overflow-auto rounded-md bg-slate-100 p-3 text-xs">
            {JSON.stringify(activity.raw_row.raw_data, null, 2)}
          </pre>
          {activity.raw_row.parse_errors?.length > 0 && (
            <p className="mb-4 rounded-lg border border-rose-300 bg-rose-50 px-4 py-3 text-rose-700">
              Parse notes: {activity.raw_row.parse_errors.join("; ")}
            </p>
          )}
        </section>
      )}

      {!activity.is_locked && (
        <section className="mt-5 border-t border-slate-200 pt-4">
          <h3>Analyst action</h3>
          <textarea
            placeholder="Reason (required for flag / reject)"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            rows={3}
            className="mb-2 w-full rounded-md border border-slate-300 p-2"
          />
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              className="cursor-pointer rounded-md bg-emerald-700 px-4 py-2 text-sm font-medium text-white transition hover:bg-emerald-800 disabled:cursor-not-allowed disabled:opacity-60"
              disabled={pending}
              onClick={() => run("approve")}
            >
              Approve
            </button>
            <button
              type="button"
              className="cursor-pointer rounded-md bg-emerald-50 px-4 py-2 text-sm font-medium text-emerald-700 transition hover:bg-emerald-100"
              disabled={pending}
              onClick={() => run("flag")}
            >
              Flag
            </button>
            <button
              type="button"
              className="cursor-pointer rounded-md bg-rose-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-rose-700"
              disabled={pending}
              onClick={() => run("reject")}
            >
              Reject
            </button>
          </div>
        </section>
      )}

      {audit && audit.length > 0 && (
        <section className="mt-5 border-t border-slate-200 pt-4">
          <h3>Audit history</h3>
          <ul className="m-0 list-none p-0 text-sm">
            {audit.map((log) => (
              <li key={log.id} className="border-b border-slate-200 py-1.5">
                <strong>{log.action}</strong> by {log.actor_email || "system"}
                <span className="text-xs text-slate-500"> — {new Date(log.timestamp).toLocaleString()}</span>
                {log.reason && <div className="text-xs">{log.reason}</div>}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
