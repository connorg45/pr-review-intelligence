import { Link, Route, Routes } from "react-router-dom";
import { AppLayout } from "./layouts/AppLayout";
import { ActivityPage } from "./pages/ActivityPage";
import { DashboardPage } from "./pages/DashboardPage";
import { PullRequestDetailPage } from "./pages/PullRequestDetailPage";
import { PullRequestsPage } from "./pages/PullRequestsPage";
import { SettingsPage } from "./pages/SettingsPage";

function NotFoundPage() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <div className="panel-surface rounded-3xl px-8 py-10 text-center">
        <p className="font-mono text-xs uppercase tracking-[0.1em] text-slate-400">404</p>
        <h1 className="mt-3 text-2xl font-semibold text-slate-50">Route not found</h1>
        <Link to="/" className="btn btn-secondary mt-6">
          Return to dashboard <span aria-hidden="true" className="ml-2">→</span>
        </Link>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/pull-requests" element={<PullRequestsPage />} />
        <Route path="/pull-requests/:id" element={<PullRequestDetailPage />} />
        <Route path="/activity" element={<ActivityPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
