import { Alert, Snackbar } from "@mui/material";
import { useEffect, useState } from "react";

type RequestErrorBannerProps = {
    message?: string;
    onClose?: () => void;
};

export default function RequestErrorBanner({ message, onClose }: RequestErrorBannerProps) {
    const [open, setOpen] = useState(false);

    useEffect(() => {
        setOpen(Boolean(message));
    }, [message]);

    const handleClose = () => {
        setOpen(false);
        onClose?.();
    };

    if (!message) {
        return null;
    }

    return (
        <>
            <Alert severity="error">{message}</Alert>
            <Snackbar
                open={open}
                autoHideDuration={3000}
                onClose={handleClose}
                anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
            >
                <Alert severity="error" variant="filled" onClose={handleClose}>
                    {message}
                </Alert>
            </Snackbar>
        </>
    );
}
