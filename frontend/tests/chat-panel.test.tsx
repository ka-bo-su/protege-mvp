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

    expect(await screen.findByText(/500/i)).toBeInTheDocument();
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
});
