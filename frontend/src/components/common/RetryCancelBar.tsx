import { Box, Button } from "@mui/material";
import type { RequestStatus } from "../../types/request";

type RetryCancelBarProps = {
    status: RequestStatus;
    onRetry: () => void;
    onCancel: () => void;
    disabled?: boolean;
};

export default function RetryCancelBar({ status, onRetry, onCancel, disabled = false }: RetryCancelBarProps) {
    if (status === "idle") {
        return null;
    }

    const isLoading = status === "loading";

    return (
        <Box sx={{ display: "flex", justifyContent: "flex-end" }}>
            <Button variant="outlined" onClick={isLoading ? onCancel : onRetry} disabled={disabled}>
                {isLoading ? "Cancel" : "Retry"}
            </Button>
        </Box>
    );
}
