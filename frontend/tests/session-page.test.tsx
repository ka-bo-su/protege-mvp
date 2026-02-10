import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ReactNode } from "react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import SessionsPage from "../src/pages/SessionsPage";
import Phase1SessionPage from "../src/pages/Phase1SessionPage";
import Phase3SessionPage from "../src/pages/Phase3SessionPage";

const baseUrl = "http://localhost:8000";

const createMockResponse = (data: unknown, ok = true): Response => {
    const status = ok ? 200 : 500;
    const statusText = ok ? "OK" : "Internal Server Error";
    return new Response(JSON.stringify(data), { status, statusText });
};

const renderWithRouter = (ui: ReactNode, initialPath = "/sessions") =>
    render(
        <MemoryRouter initialEntries={[initialPath]}>
            <Routes>
                <Route path="/sessions" element={ui} />
                <Route path="/phase1/session/:sessionId" element={<Phase1SessionPage />} />
                <Route path="/phase3/session/:sessionId" element={<Phase3SessionPage />} />
            </Routes>
        </MemoryRouter>
    );

afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
});

describe("SessionsPage", () => {
    it("renders the page header", async () => {
        vi.spyOn(globalThis, "fetch").mockResolvedValue(createMockResponse([]));
        renderWithRouter(<SessionsPage />);

        expect(await screen.findByText("Sessions")).toBeInTheDocument();
        expect(screen.getByRole("button", { name: "Start New Session" })).toBeInTheDocument();
    });

    it("fetches sessions and renders the table", async () => {
        vi.spyOn(globalThis, "fetch").mockResolvedValue(
            createMockResponse([
                { id: "abc", phase: 1, session_date: "2026-02-10" },
                { id: "def", phase: 3, session_date: "2026-02-09" },
            ])
        );

        renderWithRouter(<SessionsPage />);

        expect(await screen.findByText("2026-02-10")).toBeInTheDocument();
        expect(screen.getByText("Phase 3")).toBeInTheDocument();
    });

    it("opens the dialog and starts a phase1 session", async () => {
        const fetchMock = vi
            .spyOn(globalThis, "fetch")
            .mockImplementation((input: RequestInfo | URL, init?: RequestInit) => {
                const url = input.toString();
                if (url === `${baseUrl}/api/v1/sessions?user_id=1`) {
                    return Promise.resolve(createMockResponse([]));
                }
                if (url === `${baseUrl}/api/v1/phase1/session` && init?.method === "POST") {
                    return Promise.resolve(createMockResponse({ id: "new-session" }));
                }
                return Promise.resolve(createMockResponse({ message: "not found" }, false));
            });

        renderWithRouter(<SessionsPage />);

        await userEvent.click(await screen.findByRole("button", { name: "Start New Session" }));
        await userEvent.click(screen.getByLabelText("Phase1 Goal Setting"));
        await userEvent.click(screen.getByRole("button", { name: "Start" }));

        await waitFor(() => {
            expect(fetchMock).toHaveBeenCalledWith(`${baseUrl}/api/v1/phase1/session`, expect.any(Object));
        });
    });

    it("navigates after session creation", async () => {
        vi.spyOn(globalThis, "fetch").mockImplementation((input: RequestInfo | URL, init?: RequestInit) => {
            const url = input.toString();
            if (url === `${baseUrl}/api/v1/sessions?user_id=1`) {
                return Promise.resolve(createMockResponse([]));
            }
            if (url === `${baseUrl}/api/v1/phase3/session` && init?.method === "POST") {
                return Promise.resolve(createMockResponse({ id: "session-3" }));
            }
            return Promise.resolve(createMockResponse({ message: "not found" }, false));
        });

        renderWithRouter(<SessionsPage />);

        await userEvent.click(await screen.findByRole("button", { name: "Start New Session" }));
        await userEvent.click(screen.getByLabelText("Phase3 Reflection"));
        await userEvent.click(screen.getByRole("button", { name: "Start" }));

        expect(await screen.findByText("Phase 3 Chat")).toBeInTheDocument();
    });

    it("shows a snackbar on API error", async () => {
        vi.spyOn(globalThis, "fetch").mockResolvedValue(createMockResponse({ message: "error" }, false));

        renderWithRouter(<SessionsPage />);

        expect(await screen.findByText(/500/i)).toBeInTheDocument();
    });
});
