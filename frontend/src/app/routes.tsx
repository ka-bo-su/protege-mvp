import { createBrowserRouter } from "react-router-dom";
import AppShell from "../components/AppShell";
import HomePage from "../pages/HomePage";
import NotFoundPage from "../pages/NotFoundPage";
import Phase1Page from "../pages/Phase1Page";
import Phase3Page from "../pages/Phase3Page";
import SessionsPage from "../pages/SessionsPage";

export const router = createBrowserRouter([
    {
        path: "/",
        element: <AppShell />,
        children: [
            { index: true, element: <HomePage /> },
            { path: "sessions", element: <SessionsPage /> },
            { path: "phase1", element: <Phase1Page /> },
            { path: "phase1/session/:id", element: <Phase1Page /> },
            { path: "phase3", element: <Phase3Page /> },
            { path: "phase3/session/:id", element: <Phase3Page /> },
            { path: "*", element: <NotFoundPage /> },
        ],
    },
]);
