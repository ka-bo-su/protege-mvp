import { Box, Button, CircularProgress, TextField } from "@mui/material";
import { KeyboardEvent } from "react";

type ChatInputProps = {
    value: string;
    onChange: (value: string) => void;
    onSend: () => void;
    disabled?: boolean;
    isSending?: boolean;
};

export default function ChatInput({ value, onChange, onSend, disabled = false, isSending = false }: ChatInputProps) {
    const handleKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            if (!disabled && value.trim().length > 0) {
                onSend();
            }
        }
    };

    const isSendDisabled = disabled || value.trim().length === 0;

    return (
        <Box display="flex" gap={2} alignItems="flex-end">
            <TextField
                fullWidth
                multiline
                minRows={3}
                placeholder="メッセージを入力"
                value={value}
                onChange={(event) => onChange(event.target.value)}
                onKeyDown={handleKeyDown}
                disabled={disabled}
            />
            <Button
                variant="contained"
                onClick={onSend}
                disabled={isSendDisabled}
                sx={{ minWidth: 96, height: 48 }}
            >
                {isSending ? <CircularProgress size={20} color="inherit" /> : "Send"}
            </Button>
        </Box>
    );
}
