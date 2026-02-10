import { Alert, Box, Button, Divider, Stack, Typography } from "@mui/material";
import { useEffect, useRef, useState } from "react";
import { sendPhase1Turn, sendPhase3Turn } from "../../services/chatApi";
import type { ChatTurn } from "../../types/chat";
import ChatInput from "./ChatInput";
import ChatMessageList from "./ChatMessageList";

type ChatPanelProps = {
    phase: 1 | 3;
    sessionId: string;
};

type FailedRequest = {
    message: string;
};

export default function ChatPanel({ phase, sessionId }: ChatPanelProps) {
    const [messages, setMessages] = useState<ChatTurn[]>([]);
    const [draftText, setDraftText] = useState("");
    const [isSending, setIsSending] = useState(false);
    const [error, setError] = useState<string | undefined>(undefined);
    const [lastFailedRequest, setLastFailedRequest] = useState<FailedRequest | undefined>(undefined);
    const listRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        if (listRef.current) {
            listRef.current.scrollTop = listRef.current.scrollHeight;
        }
    }, [messages]);

    const performSend = async (message: string, { addUser }: { addUser: boolean }) => {
        if (isSending) {
            return;
        }

        if (addUser) {
            setMessages((prev) => [
                ...prev,
                {
                    id: `user-${Date.now()}`,
                    role: "user",
                    content: message,
                },
            ]);
        }

        setIsSending(true);
        setError(undefined);

        try {
            const response = phase === 1 ? await sendPhase1Turn(sessionId, message) : await sendPhase3Turn(sessionId, message);
            setMessages((prev) => [
                ...prev,
                {
                    id: `assistant-${response.turn_index}-${Date.now()}`,
                    role: "assistant",
                    content: response.assistant_message,
                },
            ]);
            setDraftText("");
            setLastFailedRequest(undefined);
        } catch (err) {
            setError(err instanceof Error ? err.message : "送信に失敗しました。");
            setLastFailedRequest({ message });
        } finally {
            setIsSending(false);
        }
    };

    const handleSend = async () => {
        if (isSending || draftText.trim().length === 0) {
            return;
        }

        const message = draftText.trim();
        await performSend(message, { addUser: true });
    };

    const handleRetry = async () => {
        if (!lastFailedRequest || isSending) {
            return;
        }

        await performSend(lastFailedRequest.message, { addUser: false });
    };

    return (
        <Stack spacing={2}>
            <Box>
                <Typography variant="h4" fontWeight={700} gutterBottom>
                    Phase {phase} Chat
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    Session ID: {sessionId}
                </Typography>
            </Box>
            <Divider />
            <Box
                ref={listRef}
                sx={{
                    border: 1,
                    borderColor: "divider",
                    borderRadius: 2,
                    p: 2,
                    height: { xs: "50vh", md: "60vh" },
                    overflowY: "auto",
                    bgcolor: "background.paper",
                }}
            >
                <ChatMessageList messages={messages} />
            </Box>
            <ChatInput value={draftText} onChange={setDraftText} onSend={handleSend} disabled={isSending} isSending={isSending} />
            {error && (
                <Alert
                    severity="error"
                    action={
                        <Button color="inherit" size="small" onClick={handleRetry} disabled={!lastFailedRequest || isSending}>
                            Retry
                        </Button>
                    }
                >
                    {error}
                </Alert>
            )}
        </Stack>
    );
}
