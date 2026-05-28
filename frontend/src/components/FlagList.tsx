const FLAG_LABELS: Record<string, string> = {
  suspicious_quantity: "Quantity looks unusual compared to similar rows in this upload",
  estimated_distance: "Flight distance was estimated from airport codes",
  missing_distance: "Ground transport is missing distance — estimate may be unreliable",
  long_billing_period: "Billing period is longer than 45 days",
  overlapping_billing_period: "Billing period overlaps another bill for the same meter",
  missing_unit: "Procurement row has quantity but no unit — using spend fallback",
  spend_fallback: "Emissions estimated from spend, not physical quantity",
};

export function FlagList({ flags }: { flags: string[] }) {
  if (!flags.length) return <span className="text-slate-500">None</span>;
  return (
    <ul className="m-0 list-none p-0">
      {flags.map((f) => (
        <li key={f} title={FLAG_LABELS[f] ?? f} className="mb-2 text-sm">
          <code className="rounded bg-slate-100 px-1.5 py-0.5">{f}</code>
          {FLAG_LABELS[f] && (
            <span className="mt-0.5 block text-slate-500">
              {FLAG_LABELS[f]}
            </span>
          )}
        </li>
      ))}
    </ul>
  );
}
