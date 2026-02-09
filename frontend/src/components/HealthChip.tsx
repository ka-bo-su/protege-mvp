import { Chip } from "@mui/material";

export type HealthStatus = "loading" | "ok" | "error" | "unknown";

type HealthChipProps = {
    status: HealthStatus;
    errorMessage?: string | null;
};

const statusConfig: Record<HealthStatus, { label: string; color: "default" | "success" | "error" | "warning" }> = {
    loading: { label: "loading", color: "warning" },
    ok: { label: "ok", color: "success" },
    error: { label: "error", color: "error" },
    unknown: { label: "unknown", color: "default" },
};

export default function HealthChip({ status, errorMessage }: HealthChipProps) {
    const config = statusConfig[status];
    const label = errorMessage && status === "error" ? `error (${errorMessage})` : config.label;

    return <Chip label={label} color={config.color} variant={status === "unknown" ? "outlined" : "filled"} />;
}
