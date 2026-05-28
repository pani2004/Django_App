import { FormEvent, useState } from "react";
import { Navigate } from "react-router-dom";
import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";

export function LoginPage() {
  const { user, login, loading } = useAuth();
  const [username, setUsername] = useState("analyst@demo.breathe.local");
  const [password, setPassword] = useState("demo-analyst-2025");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (!loading && user) return <Navigate to="/" replace />;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login(username, password);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Login failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <form
        className="flex w-full max-w-md flex-col gap-4 rounded-xl border border-slate-200 bg-white p-8 shadow-sm"
        onSubmit={handleSubmit}
      >
        <h1 className="m-0 text-4xl font-bold text-emerald-700">Breathe ESG</h1>
        <p className="m-0 text-slate-600">
          Sign in to review and approve emissions data.
        </p>
        {error && (
          <div className="mb-1 rounded-lg border border-rose-300 bg-rose-50 px-4 py-3 text-rose-700">
            {error}
          </div>
        )}
        <label className="flex flex-col gap-1.5 text-sm font-medium">
          Email
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            className="rounded-md border border-slate-300 px-3 py-2 text-base outline-none ring-emerald-200 focus:ring"
            required
          />
        </label>
        <label className="flex flex-col gap-1.5 text-sm font-medium">
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            className="rounded-md border border-slate-300 px-3 py-2 text-base outline-none ring-emerald-200 focus:ring"
            required
          />
        </label>
        <button
          type="submit"
          className="cursor-pointer rounded-md bg-emerald-700 px-4 py-2 text-sm font-medium text-white transition hover:bg-emerald-800 disabled:cursor-not-allowed disabled:opacity-60"
          disabled={submitting}
        >
          {submitting ? "Signing in…" : "Sign in"}
        </button>
        <p className="m-0 text-xs text-slate-500">
          Demo: analyst@demo.breathe.local / demo-analyst-2025
        </p>
      </form>
    </div>
  );
}
