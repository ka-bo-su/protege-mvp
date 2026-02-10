import "@testing-library/jest-dom/vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import ReportPanel from "../src/components/report/ReportPanel";

const createMockResponse = (data: unknown, ok = true): Response => {
    const status = ok ? 200 : 500;
    const statusText = ok ? "OK" : "Internal Server Error";
    return new Response(JSON.stringify(data), { status, statusText });
};

afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
});

describe("ReportPanel", () => {
    it("disables generate button while draft is loading", async () => {
        let resolveFetch: (value: Response) => void;
        const fetchPromise = new Promise<Response>((resolve) => {
            resolveFetch = resolve;
        });

        vi.spyOn(globalThis, "fetch").mockReturnValue(fetchPromise as Promise<Response>);

        render(<ReportPanel sessionId="session-1" />);

        const generateButton = screen.getByRole("button", { name: /generate draft/i });
        await userEvent.click(generateButton);

        expect(generateButton).toBeDisabled();

        resolveFetch!(createMockResponse({ session_id: "session-1", report_draft: "draft", saved: true }));

        await waitFor(() => {
            expect(generateButton).not.toBeDisabled();
        });
    });

    it("keeps final text after save error", async () => {
        vi.spyOn(globalThis, "fetch").mockResolvedValue(createMockResponse({ message: "error" }, false));

        render(<ReportPanel sessionId="session-1" />);

        const input = screen.getByRole("textbox");
        const saveButton = screen.getByRole("button", { name: /save final/i });

        await userEvent.type(input, "final content");
        await userEvent.click(saveButton);

        const errorMessages = await screen.findAllByText("エラーが発生しました。再試行してください。");
        expect(errorMessages.length).toBeGreaterThan(0);
        expect(input).toHaveValue("final content");
    });

    it("shows edit metrics after save success", async () => {
        vi.spyOn(globalThis, "fetch").mockResolvedValue(
            createMockResponse({
                session_id: "session-1",
                saved: true,
                edit_metrics: { chars_added: 10, chars_removed: 5, ratio: 0.05 },
            })
        );

        render(<ReportPanel sessionId="session-1" />);

        const saveButton = screen.getByRole("button", { name: /save final/i });
        await userEvent.click(saveButton);

        expect(await screen.findByText(/chars_added/i)).toBeInTheDocument();
        expect(screen.getByText(/chars_removed/i)).toBeInTheDocument();
        expect(screen.getByText(/0.05/i)).toBeInTheDocument();
    });

    it("retries the last failed draft request", async () => {
        vi.spyOn(globalThis, "fetch")
            .mockResolvedValueOnce(createMockResponse({ message: "error" }, false))
            .mockResolvedValueOnce(createMockResponse({ session_id: "session-1", report_draft: "draft", saved: true }));

        render(<ReportPanel sessionId="session-1" />);

        const generateButton = screen.getByRole("button", { name: /generate draft/i });
        await userEvent.click(generateButton);

        const retryButton = await screen.findByRole("button", { name: /retry/i });
        await userEvent.click(retryButton);

        expect(await screen.findByRole("textbox")).toHaveValue("draft");
        expect(globalThis.fetch).toHaveBeenCalledTimes(2);
    });

    it("cancels in-flight draft request and ignores late response", async () => {
        let resolveFetch: (value: Response) => void;
        const fetchPromise = new Promise<Response>((resolve) => {
            resolveFetch = resolve;
        });

        vi.spyOn(globalThis, "fetch").mockReturnValue(fetchPromise as Promise<Response>);

        render(<ReportPanel sessionId="session-1" />);

        const generateButton = screen.getByRole("button", { name: /generate draft/i });
        await userEvent.click(generateButton);

        const cancelButton = await screen.findByRole("button", { name: /cancel/i });
        await userEvent.click(cancelButton);

        expect(generateButton).not.toBeDisabled();

        resolveFetch!(createMockResponse({ session_id: "session-1", report_draft: "draft", saved: true }));

        await waitFor(() => {
            expect(screen.queryByText("draft")).not.toBeInTheDocument();
        });
    });
});
