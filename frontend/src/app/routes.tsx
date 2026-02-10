import { createBrowserRouter } from "react-router-dom";
import AppShell from "../components/AppShell";
import HomePage from "../pages/HomePage";
import NotFoundPage from "../pages/NotFoundPage";
import Phase1Page from "../pages/Phase1Page";
import Phase1SessionPage from "../pages/Phase1SessionPage";
import Phase3Page from "../pages/Phase3Page";
import Phase3SessionPage from "../pages/Phase3SessionPage";
import SessionsPage from "../pages/SessionsPage";
import KpiEditRatioPage from "../pages/admin/KpiEditRatioPage";

export const router = createBrowserRouter([
    {
        path: "/",
        element: <AppShell />,
        children: [
            { index: true, element: <HomePage /> },
            { path: "sessions", element: <SessionsPage /> },
            { path: "phase1", element: <Phase1Page /> },
            { path: "phase1/session/:sessionId", element: <Phase1SessionPage /> },
            { path: "phase3", element: <Phase3Page /> },
            { path: "phase3/session/:sessionId", element: <Phase3SessionPage /> },
            { path: "admin/kpi", element: <KpiEditRatioPage /> },
            { path: "admin/kpi/edit-ratio", element: <KpiEditRatioPage /> },
            { path: "*", element: <NotFoundPage /> },
        ],
    },
]);
