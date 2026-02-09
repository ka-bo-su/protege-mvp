import { Alert, AlertTitle } from "@mui/material";

type ErrorBannerProps = {
    message: string;
    title?: string;
};

export default function ErrorBanner({ message, title = "Error" }: ErrorBannerProps) {
    return (
        <Alert severity="error">
            <AlertTitle>{title}</AlertTitle>
            {message}
        </Alert>
    );
}
