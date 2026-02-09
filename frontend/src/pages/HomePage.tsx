import { Stack, Typography } from "@mui/material";
import { useEffect, useState } from "react";
import ErrorBanner from "../components/ErrorBanner";
import HealthChip, { HealthStatus } from "../components/HealthChip";
import { getHealth } from "../lib/api";

type HealthState = {
    status: HealthStatus;
    errorMessage?: string | null;
};

export default function HomePage() {
    const [health, setHealth] = useState<HealthState>({ status: "loading" });

    useEffect(() => {
        let active = true;

        const fetchHealth = async () => {
            try {
                const data = await getHealth();
                if (!active) return;
                const status = data.status === "ok" ? "ok" : "unknown";
                setHealth({ status });
            } catch (error) {
                if (!active) return;
                const message = error instanceof Error ? error.message : "Unknown error";
                setHealth({ status: "error", errorMessage: message });
            }
        };

        fetchHealth();

        return () => {
            active = false;
        };
    }, []);

    return (
        <Stack spacing={3}>
            <Typography variant="h4" fontWeight={700}>
                Frontend OK
            </Typography>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2} alignItems={{ sm: "center" }}>
                <Typography variant="subtitle1">Backend health:</Typography>
                <HealthChip status={health.status} errorMessage={health.errorMessage} />
            </Stack>
            {health.status === "error" && health.errorMessage ? (
                <ErrorBanner message={health.errorMessage} title="Backend error" />
            ) : null}
        </Stack>
    );
}
