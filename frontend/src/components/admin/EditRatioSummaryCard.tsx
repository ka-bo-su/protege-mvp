import { Card, CardContent, Grid, Stack, Typography } from "@mui/material";
import type { EditRatioSummary } from "../../types/kpi";

type EditRatioSummaryCardProps = {
    summary: EditRatioSummary;
};

const formatRatio = (value: number | null) => {
    if (value === null || Number.isNaN(value)) {
        return "N/A";
    }
    return `${(value * 100).toFixed(1)}%`;
};

export default function EditRatioSummaryCard({ summary }: EditRatioSummaryCardProps) {
    return (
        <Card>
            <CardContent>
                <Stack spacing={2}>
                    <Typography variant="h6" fontWeight={700}>
                        Summary
                    </Typography>
                    <Grid container spacing={2}>
                        <Grid item xs={12} sm={4}>
                            <Typography variant="caption" color="text.secondary">
                                Count
                            </Typography>
                            <Typography variant="h5" fontWeight={600}>
                                {summary.count}
                            </Typography>
                        </Grid>
                        <Grid item xs={12} sm={4}>
                            <Typography variant="caption" color="text.secondary">
                                Avg
                            </Typography>
                            <Typography variant="h5" fontWeight={600}>
                                {formatRatio(summary.avg)}
                            </Typography>
                        </Grid>
                        <Grid item xs={12} sm={4}>
                            <Typography variant="caption" color="text.secondary">
                                Median
                            </Typography>
                            <Typography variant="h5" fontWeight={600}>
                                {formatRatio(summary.median)}
                            </Typography>
                        </Grid>
                        <Grid item xs={12} sm={4}>
                            <Typography variant="caption" color="text.secondary">
                                Min
                            </Typography>
                            <Typography variant="h5" fontWeight={600}>
                                {formatRatio(summary.min)}
                            </Typography>
                        </Grid>
                        <Grid item xs={12} sm={4}>
                            <Typography variant="caption" color="text.secondary">
                                Max
                            </Typography>
                            <Typography variant="h5" fontWeight={600}>
                                {formatRatio(summary.max)}
                            </Typography>
                        </Grid>
                    </Grid>
                </Stack>
            </CardContent>
        </Card>
    );
}
