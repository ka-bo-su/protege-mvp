import { Box, Button, CircularProgress, Stack, Typography } from "@mui/material";
import { useCallback, useEffect, useMemo, useState } from "react";
import EditRatioSummaryCard from "../../components/admin/EditRatioSummaryCard";
import EditRatioTable from "../../components/admin/EditRatioTable";
import RequestErrorBanner from "../../components/common/RequestErrorBanner";
import { fetchEditRatio } from "../../services/kpiApi";
import type { EditRatioResponse, EditRatioSummary } from "../../types/kpi";

const DEFAULT_USER_ID = 1;

const emptySummary: EditRatioSummary = {
    count: 0,
    avg: null,
    median: null,
    min: null,
    max: null,
};

const computeSummary = (items: EditRatioResponse["items"]): EditRatioSummary => {
    if (items.length === 0) {
        return emptySummary;
    }
    const ratios = items.map((item) => item.ratio).sort((a, b) => a - b);
    const count = ratios.length;
    const avg = ratios.reduce((sum, value) => sum + value, 0) / count;
    const median =
        count % 2 === 1
            ? ratios[Math.floor(count / 2)]
            : (ratios[count / 2 - 1] + ratios[count / 2]) / 2;
    return {
        count,
        avg,
        median,
        min: ratios[0],
        max: ratios[ratios.length - 1],
    };
};

export default function KpiEditRatioPage() {
    const [data, setData] = useState<EditRatioResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const loadData = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetchEditRatio({ userId: DEFAULT_USER_ID });
            setData(response);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Edit Ratio の取得に失敗しました。");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        void loadData();
    }, [loadData]);

    const summary = useMemo(() => {
        if (!data) {
            return emptySummary;
        }
        return data.summary ?? computeSummary(data.items);
    }, [data]);

    return (
        <Stack spacing={3}>
            <Typography variant="h4" fontWeight={700}>
                KPI - Edit Ratio
            </Typography>

            <RequestErrorBanner message={error ?? undefined} onClose={() => setError(null)} />

            {error && (
                <Box>
                    <Button variant="outlined" onClick={loadData}>
                        Retry
                    </Button>
                </Box>
            )}

            {loading ? (
                <Box display="flex" justifyContent="center" py={6}>
                    <CircularProgress />
                </Box>
            ) : (
                <Stack spacing={3}>
                    <EditRatioSummaryCard summary={summary} />
                    <EditRatioTable items={data?.items ?? []} />
                </Stack>
            )}
        </Stack>
    );
}
