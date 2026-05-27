import type {
  Activity,
  ActivityDetail,
  AuditLogEntry,
  DashboardStats,
  IngestionBatch,
  Paginated,
  User,
} from "./types";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public body?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function parseJson<T>(res: Response): Promise<T> {
  if (res.status === 204) return Promise.resolve({} as T);
  return res.json() as Promise<T>;
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const res = await fetch(path, {
    ...options,
    credentials: "include",
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = (await res.json()) as { detail?: string };
      if (body?.detail) detail = body.detail;
    } catch {
      // ignore non-JSON error bodies
    }
    throw new ApiError(detail, res.status);
  }

  return parseJson<T>(res);
}

export const api = {
  login: (username: string, password: string) =>
    apiFetch<{ access: string; refresh: string }>("/api/auth/login/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    }),

  logout: () => apiFetch("/api/auth/logout/", { method: "POST" }),

  me: () => apiFetch<User>("/api/auth/me/"),

  dashboardStats: () => apiFetch<DashboardStats>("/api/dashboard/stats/"),

  listBatches: () =>
    apiFetch<Paginated<IngestionBatch>>("/api/batches/"),

  uploadBatch: (source: string, file: File) => {
    const form = new FormData();
    form.append("source", source);
    form.append("file", file);
    return apiFetch<IngestionBatch>("/api/batches/upload/", {
      method: "POST",
      body: form,
    });
  },

  listActivities: (params?: Record<string, string>) => {
    const qs = params ? `?${new URLSearchParams(params)}` : "";
    return apiFetch<Paginated<Activity>>(`/api/activities/${qs}`);
  },

  getActivity: (id: number) =>
    apiFetch<ActivityDetail>(`/api/activities/${id}/`),

  approveActivity: (id: number, reason = "") =>
    apiFetch<Activity>(`/api/activities/${id}/approve/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reason }),
    }),

  flagActivity: (id: number, reason: string) =>
    apiFetch<Activity>(`/api/activities/${id}/flag/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reason }),
    }),

  rejectActivity: (id: number, reason: string) =>
    apiFetch<Activity>(`/api/activities/${id}/reject/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reason }),
    }),

  bulkApprove: () =>
    apiFetch<{ approved_count: number }>("/api/activities/bulk-approve/", {
      method: "POST",
    }),

  activityAudit: (id: number) =>
    apiFetch<AuditLogEntry[]>(`/api/activities/${id}/audit/`),
};
