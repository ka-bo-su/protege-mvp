import { Box, Divider, Stack, Typography } from "@mui/material";
import { useEffect, useRef, useState } from "react";
import RequestErrorBanner from "../common/RequestErrorBanner";
import RetryCancelBar from "../common/RetryCancelBar";
import useRequestController from "../../hooks/useRequestController";
import { sendPhase1Turn, sendPhase3Turn } from "../../services/chatApi";
import type { ChatTurn, ChatTurnResponse } from "../../types/chat";
import ChatInput from "./ChatInput";
import ChatMessageList from "./ChatMessageList";

type ChatPanelProps = {
    phase: 1 | 3;
    sessionId: string;
};

type ChatActionType = "chat_turn";

type ChatPayload = {
    message: string;
};

export default function ChatPanel({ phase, sessionId }: ChatPanelProps) {
    const [messages, setMessages] = useState<ChatTurn[]>([]);
    const [draftText, setDraftText] = useState("");
    const requestController = useRequestController<ChatActionType, ChatPayload>();
    const listRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        if (listRef.current) {
            listRef.current.scrollTop = listRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSend = async () => {
        if (requestController.state.status === "loading" || draftText.trim().length === 0) {
            return;
        }

        const message = draftText.trim();

        setMessages((prev) => [
            ...prev,
            {
                id: `user-${Date.now()}`,
                role: "user",
                content: message,
            },
        ]);

        const result = await requestController.run<ChatTurnResponse>({
            actionType: "chat_turn",
            payload: { message },
            requestFn: (payload) =>
                phase === 1 ? sendPhase1Turn(sessionId, payload.message) : sendPhase3Turn(sessionId, payload.message),
        });

        if (result.status === "success") {
            setMessages((prev) => [
                ...prev,
                {
                    id: `assistant-${result.data.turn_index}-${Date.now()}`,
                    role: "assistant",
                    content: result.data.assistant_message,
                    emergency: result.data.emergency,
                },
            ]);
            setDraftText("");
        }
    };

    const handleRetry = async () => {
        if (requestController.state.status === "loading") {
            return;
        }

        const result = await requestController.retry<ChatTurnResponse>();
        if (result.status === "success") {
            setMessages((prev) => [
                ...prev,
                {
                    id: `assistant-${result.data.turn_index}-${Date.now()}`,
                    role: "assistant",
                    content: result.data.assistant_message,
                    emergency: result.data.emergency,
                },
            ]);
            setDraftText("");
        }
    };

    const handleCancel = () => {
        requestController.cancel();
    };

    const isSending = requestController.state.status === "loading";

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
            <RetryCancelBar
                status={requestController.state.status}
                onRetry={handleRetry}
                onCancel={handleCancel}
            />
            <RequestErrorBanner message={requestController.state.error} />
        </Stack>
    );
}
