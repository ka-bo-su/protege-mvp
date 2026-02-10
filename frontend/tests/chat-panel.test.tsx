import "@testing-library/jest-dom/vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import ChatPanel from "../src/components/chat/ChatPanel";

const createMockResponse = (data: unknown, ok = true): Response => {
    const status = ok ? 200 : 500;
    const statusText = ok ? "OK" : "Internal Server Error";
    return new Response(JSON.stringify(data), { status, statusText });
};

afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
});

describe("ChatPanel", () => {
    it("disables input while sending", async () => {
        let resolveFetch: (value: Response) => void;
        const fetchPromise = new Promise<Response>((resolve) => {
            resolveFetch = resolve;
        });

        vi.spyOn(globalThis, "fetch").mockReturnValue(fetchPromise);

        render(<ChatPanel phase={1} sessionId="session-1" />);

        const input = screen.getByRole("textbox");
        const sendButton = screen.getByRole("button", { name: /send/i });

        await userEvent.type(input, "こんにちは");
        await userEvent.click(sendButton);

        expect(input).toBeDisabled();
        expect(sendButton).toBeDisabled();

        resolveFetch!(createMockResponse({ session_id: "session-1", assistant_message: "OK", turn_index: 1 }));

        await waitFor(() => {
            expect(input).not.toBeDisabled();
        });
    });

    it("keeps draft text after an error", async () => {
        vi.spyOn(globalThis, "fetch").mockResolvedValue(createMockResponse({ message: "error" }, false));

        render(<ChatPanel phase={1} sessionId="session-1" />);

        const input = screen.getByRole("textbox");
        const sendButton = screen.getByRole("button", { name: /send/i });

        await userEvent.type(input, "retry test");
        await userEvent.click(sendButton);

        const errorMessages = await screen.findAllByText("エラーが発生しました。再試行してください。");
        expect(errorMessages.length).toBeGreaterThan(0);
        expect(input).toHaveValue("retry test");
        expect(screen.getByText("retry test", { selector: "p" })).toBeInTheDocument();
    });

    it("retries the last failed request", async () => {
        vi.spyOn(globalThis, "fetch")
            .mockResolvedValueOnce(createMockResponse({ message: "error" }, false))
            .mockResolvedValueOnce(createMockResponse({ session_id: "session-1", assistant_message: "OK", turn_index: 2 }));

        render(<ChatPanel phase={1} sessionId="session-1" />);

        const input = screen.getByRole("textbox");
        const sendButton = screen.getByRole("button", { name: /send/i });

        await userEvent.type(input, "再送メッセージ");
        await userEvent.click(sendButton);

        const retryButton = await screen.findByRole("button", { name: /retry/i });
        await userEvent.click(retryButton);

        expect(await screen.findByText("OK")).toBeInTheDocument();
        expect(globalThis.fetch).toHaveBeenCalledTimes(2);
    });

    it("cancels in-flight request and ignores late response", async () => {
        let resolveFetch: (value: Response) => void;
        const fetchPromise = new Promise<Response>((resolve) => {
            resolveFetch = resolve;
        });

        vi.spyOn(globalThis, "fetch").mockReturnValue(fetchPromise);

        render(<ChatPanel phase={1} sessionId="session-1" />);

        const input = screen.getByRole("textbox");
        const sendButton = screen.getByRole("button", { name: /send/i });

        await userEvent.type(input, "cancel test");
        await userEvent.click(sendButton);

        const cancelButton = await screen.findByRole("button", { name: /cancel/i });
        await userEvent.click(cancelButton);

        expect(input).not.toBeDisabled();
        expect(sendButton).not.toBeDisabled();

        resolveFetch!(createMockResponse({ session_id: "session-1", assistant_message: "OK", turn_index: 3 }));

        await waitFor(() => {
            expect(screen.queryByText("OK")).not.toBeInTheDocument();
        });
    });
});
