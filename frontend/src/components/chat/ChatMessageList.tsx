import { Box, Stack, Typography } from "@mui/material";
import type { ChatTurn } from "../../types/chat";

const messageBubbleStyles = {
    maxWidth: "75%",
    px: 2,
    py: 1.5,
    borderRadius: 2,
    boxShadow: 1,
    whiteSpace: "pre-wrap" as const,
};

type ChatMessageListProps = {
    messages: ChatTurn[];
};

export default function ChatMessageList({ messages }: ChatMessageListProps) {
    const visibleMessages = messages.filter((message) => message.role !== "system");

    if (visibleMessages.length === 0) {
        return (
            <Box display="flex" alignItems="center" justifyContent="center" height="100%">
                <Typography variant="body2" color="text.secondary">
                    まだメッセージがありません。ここから会話を始めましょう。
                </Typography>
            </Box>
        );
    }

    return (
        <Stack spacing={2}>
            {visibleMessages.map((message) => {
                const isUser = message.role === "user";
                return (
                    <Box key={message.id} display="flex" justifyContent={isUser ? "flex-end" : "flex-start"}>
                        <Box
                            sx={{
                                ...messageBubbleStyles,
                                bgcolor: isUser ? "primary.main" : "grey.100",
                                color: isUser ? "primary.contrastText" : "text.primary",
                            }}
                        >
                            <Typography variant="body1">{message.content}</Typography>
                        </Box>
                    </Box>
                );
            })}
        </Stack>
    );
}
