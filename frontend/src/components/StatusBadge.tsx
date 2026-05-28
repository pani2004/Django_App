const STATUS_CLASS: Record<string, string> = {
  pending: "bg-amber-100 text-amber-800",
  approved: "bg-green-100 text-green-800",
  flagged: "bg-orange-100 text-orange-800",
  rejected: "bg-rose-100 text-rose-800",
  complete: "bg-green-100 text-green-800",
  failed: "bg-rose-100 text-rose-800",
  processing: "bg-amber-100 text-amber-800",
};

export function StatusBadge({ status }: { status: string }) {
  const key = status.toLowerCase();
  return (
    <span
      className={`inline-block rounded px-2 py-0.5 text-xs font-semibold capitalize ${STATUS_CLASS[key] ?? ""}`}
    >
      {status}
    </span>
  );
}
