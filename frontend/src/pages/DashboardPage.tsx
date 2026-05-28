import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "../api/client";

export function DashboardPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["dashboard"],
    queryFn: api.dashboardStats,
  });

  if (isLoading) return (
    <div className="flex items-center gap-3 py-20 text-slate-400">
      <span className="h-5 w-5 animate-spin rounded-full border-2 border-slate-200 border-t-slate-400" />
      Loading summary…
    </div>
  );

  if (error) return (
    <div className="flex items-start gap-3 rounded-2xl border border-rose-200 bg-rose-50 px-5 py-4 text-rose-700">
      <span className="mt-0.5 text-lg">⚠</span>
      <div>
        <p className="font-semibold">Unable to load dashboard</p>
        <p className="mt-0.5 text-sm text-rose-500">Check your connection or try refreshing.</p>
      </div>
    </div>
  );

  if (!data) return null;

  const attention = data.needs_attention + data.flagged;

  return (
    <div className="flex h-full flex-col gap-6 overflow-hidden">
      {/* Attention Banner */}
      {attention > 0 && (
        <div className="flex items-center justify-between gap-4 rounded-2xl border border-amber-200 bg-amber-50 px-5 py-4">
          <div>
            <p className="font-semibold text-amber-900">
              {attention} row{attention !== 1 ? "s" : ""} need your attention
            </p>
            <p className="mt-0.5 text-sm text-amber-700">
              Pending items with quality flags, or rows you have flagged.
            </p>
          </div>
          <Link
            to="/review?has_flags=true"
            className="shrink-0 rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-white no-underline transition hover:bg-amber-600 active:scale-95"
          >
            Review now →
          </Link>
        </div>
      )}

      {/* Stat Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Pending Review"
          value={data.pending_review}
          to="/review?review_status=pending"
          accent="blue"
        />
        <StatCard
          label="Flagged"
          value={data.flagged}
          to="/review?review_status=flagged"
          accent="amber"
          warn={data.flagged > 0}
        />
        <StatCard
          label="Approved & Locked"
          value={data.approved_locked}
          to="/review?review_status=approved"
          accent="emerald"
        />
        <StatCard
          label="Failed Uploads"
          value={data.failed_batches}
          to="/upload"
          accent="rose"
          warn={data.failed_batches > 0}
        />
      </div>

      {/* Breakdown Sections */}
      <div className="grid min-h-0 flex-1 gap-4 md:grid-cols-2">
        <ScopeSection title="By Scope" items={data.by_scope} />
        <ScopeSection title="By Review Status" items={data.by_status} />
      </div>
    </div>
  );
}

const accentMap = {
  blue: {
    bg: "bg-blue-50",
    ring: "ring-blue-100",
    value: "text-blue-700",
  },
  amber: {
    bg: "bg-amber-50",
    ring: "ring-amber-200",
    value: "text-amber-700",
  },
  emerald: {
    bg: "bg-emerald-50",
    ring: "ring-emerald-100",
    value: "text-emerald-700",
  },
  rose: {
    bg: "bg-rose-50",
    ring: "ring-rose-200",
    value: "text-rose-700",
  },
};

function StatCard({
  label,
  value,
  to,
  accent = "blue",
  warn,
}: {
  label: string;
  value: number;
  to: string;
  accent?: keyof typeof accentMap;
  warn?: boolean;
}) {
  const a = accentMap[accent];
  return (
    <Link
      to={to}
      className={[
        "group relative flex flex-col gap-3 rounded-2xl border border-slate-100 bg-white p-5 no-underline shadow-sm ring-2 transition-all hover:-translate-y-0.5 hover:shadow-md active:translate-y-0",
        warn ? `ring-2 ${a.ring}` : "ring-transparent",
      ].join(" ")}
    >
      <div className={`h-1.5 w-12 rounded-full ${a.bg}`} />
      <div>
        <p className={`text-3xl font-bold tabular-nums ${a.value}`}>{value.toLocaleString()}</p>
        <p className="mt-0.5 text-sm font-medium text-slate-500">{label}</p>
      </div>
      <span className="absolute bottom-4 right-4 text-slate-300 transition group-hover:translate-x-0.5 group-hover:text-slate-400">→</span>
    </Link>
  );
}

function ScopeSection({
  title,
  items,
}: {
  title: string;
  items: Record<string, number>;
}) {
  const entries = Object.entries(items);
  const total = entries.reduce((sum, [, v]) => sum + v, 0);

  return (
    <section className="flex flex-col rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center gap-2">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">{title}</h2>
      </div>
      {!entries.length ? (
        <p className="py-4 text-center text-sm text-slate-400">
          No activity yet. Upload a file to get started.
        </p>
      ) : (
        <ul className="m-0 list-none space-y-1 p-0">
          {entries.map(([k, v]) => {
            const pct = total > 0 ? Math.round((v / total) * 100) : 0;
            return (
              <li key={k} className="group rounded-lg px-3 py-2 transition hover:bg-slate-50">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-slate-700">
                    {k.replace("SCOPE_", "Scope ")}
                  </span>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-slate-400">{pct}%</span>
                    <span className="min-w-[2rem] text-right text-sm font-bold text-slate-800">{v.toLocaleString()}</span>
                  </div>
                </div>
                <div className="mt-1.5 h-1 w-full overflow-hidden rounded-full bg-slate-100">
                  <div
                    className="h-full rounded-full bg-emerald-400 transition-all"
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}