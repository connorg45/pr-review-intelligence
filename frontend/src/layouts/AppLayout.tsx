import { Link, NavLink, Outlet, useLocation } from "react-router-dom";

const navigation = [
  { to: "/", label: "Dashboard", index: "01" },
  { to: "/pull-requests", label: "Pull Requests", index: "02" },
  { to: "/activity", label: "Activity", index: "03" },
  { to: "/settings", label: "Settings", index: "04" },
];

function navClass(isActive: boolean) {
  return `app-nav-link ${isActive ? "is-active" : ""}`;
}

export function AppLayout() {
  const location = useLocation();

  return (
    <div className="min-h-screen p-3 lg:p-5">
      <div className="app-frame mx-auto grid max-w-[1520px] overflow-hidden rounded-3xl lg:min-h-[calc(100svh-2.5rem)] lg:grid-cols-[228px_minmax(0,1fr)]">
        <aside className="app-sidebar min-w-0 p-3 sm:p-4 lg:p-5">
          <Link to="/" className="brand-lockup group flex items-center gap-3 rounded-xl px-2 py-2">
            <span className="brand-mark" aria-hidden="true">PR</span>
            <div className="min-w-0">
              <p className="brand-kicker">Review operations</p>
              <h2 className="text-sm font-semibold leading-5 tracking-tight text-slate-50">PR Review Intelligence</h2>
            </div>
          </Link>

          <nav className="app-nav mt-3 flex gap-1 overflow-x-auto pb-1 lg:mt-7 lg:grid lg:overflow-visible lg:pb-0" aria-label="Primary navigation">
            {navigation.map((item) => (
              <NavLink key={item.to} to={item.to} end={item.to === "/"} className={({ isActive }) => navClass(isActive)}>
                <span className="nav-index" aria-hidden="true">{item.index}</span>
                <span className="flex-1">{item.label}</span>
                <span className="nav-arrow" aria-hidden="true">→</span>
              </NavLink>
            ))}
          </nav>
        </aside>

        <main className="workspace-shell min-w-0 p-4 sm:p-6 lg:p-8">
          <div key={location.pathname} className="route-frame">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
