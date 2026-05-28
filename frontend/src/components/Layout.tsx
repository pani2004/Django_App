import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

const nav = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/upload", label: "Upload data" },
  { to: "/review", label: "Review queue" },
];

export function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-slate-100">
      <header className="flex items-center gap-6 border-b border-slate-200 bg-white px-6 py-3">
        <NavLink to="/" end className="text-inherit no-underline">
          <div>
            <strong>Breathe ESG</strong>
            <span className="block text-xs text-slate-500">Analyst review</span>
          </div>
        </NavLink>
        <nav className="flex flex-1 gap-2">
          {nav.map(({ to, label, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                [
                  "rounded-md px-3 py-2 text-sm font-medium transition",
                  isActive
                    ? "bg-emerald-50 text-emerald-700"
                    : "text-slate-600 hover:bg-emerald-50 hover:text-emerald-700",
                ].join(" ")
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="flex items-center gap-3 text-sm">
          <span>{user?.organization.name}</span>
          <button
            type="button"
            className="rounded-md px-4 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100"
            onClick={logout}
          >
            Sign out
          </button>
        </div>
      </header>
      <main className="mx-auto w-full max-w-7xl p-6">
        <Outlet />
      </main>
    </div>
  );
}
