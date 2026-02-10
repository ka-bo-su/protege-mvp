import "@testing-library/jest-dom/vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ReactNode } from "react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import KpiEditRatioPage from "../src/pages/admin/KpiEditRatioPage";

const baseUrl = "http://localhost:8000";

const createMockResponse = (data: unknown, ok = true): Response => {
    const status = ok ? 200 : 500;
    const statusText = ok ? "OK" : "Internal Server Error";
    return new Response(JSON.stringify(data), { status, statusText });
};

const renderWithRouter = (ui: ReactNode, initialPath = "/admin/kpi/edit-ratio") =>
    render(
        <MemoryRouter initialEntries={[initialPath]}>
            <Routes>
                <Route path="/admin/kpi/edit-ratio" element={ui} />
            </Routes>
        </MemoryRouter>
    );

afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
});

describe("KpiEditRatioPage", () => {
    it("renders empty state with N/A summary", async () => {
        vi.spyOn(globalThis, "fetch").mockResolvedValue(
            createMockResponse({
                user_id: 1,
                items: [],
                summary: { count: 0, avg: null, median: null, min: null, max: null },
            })
        );

        renderWithRouter(<KpiEditRatioPage />);

        expect(await screen.findByText("KPI - Edit Ratio")).toBeInTheDocument();
        expect(await screen.findByText("No data")).toBeInTheDocument();
        expect(screen.getAllByText("N/A").length).toBeGreaterThan(0);
    });

    it("shows ratio as percent", async () => {
        vi.spyOn(globalThis, "fetch").mockResolvedValue(
            createMockResponse({
                user_id: 1,
                items: [
                    {
                        session_id: "abc",
                        session_date: "2026-02-10",
                        ratio: 0.12,
                        chars_added: 10,
                        chars_removed: 5,
                    },
                ],
                summary: { count: 1, avg: 0.12, median: 0.12, min: 0.12, max: 0.12 },
            })
        );

        renderWithRouter(<KpiEditRatioPage />);

        const ratios = await screen.findAllByText("12.0%", { exact: true });
        expect(ratios.length).toBeGreaterThan(0);
    });

    it("shows snackbar and retry on API error", async () => {
        const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(createMockResponse({}, false));

        renderWithRouter(<KpiEditRatioPage />);

        expect(await screen.findByText(/500/i)).toBeInTheDocument();
        const retryButton = screen.getByRole("button", { name: "Retry" });
        await userEvent.click(retryButton);

        await waitFor(() => {
            expect(fetchMock).toHaveBeenCalledWith(
                `${baseUrl}/api/v1/kpi/edit-ratio?user_id=1`,
                expect.any(Object)
            );
        });
    });
});
