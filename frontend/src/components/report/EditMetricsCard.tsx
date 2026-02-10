import { Card, CardContent, Stack, Typography } from "@mui/material";
import type { EditMetrics } from "../../types/report";

type EditMetricsCardProps = {
    metrics: EditMetrics;
};

export default function EditMetricsCard({ metrics }: EditMetricsCardProps) {
    return (
        <Card variant="outlined">
            <CardContent>
                <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                    Edit Metrics
                </Typography>
                <Stack spacing={1}>
                    <Typography variant="body2">chars_added: {metrics.chars_added}</Typography>
                    <Typography variant="body2">chars_removed: {metrics.chars_removed}</Typography>
                    <Typography variant="body2">ratio: {metrics.ratio}</Typography>
                </Stack>
            </CardContent>
        </Card>
    );
}
