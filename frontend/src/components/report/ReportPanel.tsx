import { Alert, Box, Button, CircularProgress, Divider, Paper, Snackbar, Stack, Typography } from "@mui/material";
import { useState } from "react";
import RequestErrorBanner from "../common/RequestErrorBanner";
import RetryCancelBar from "../common/RetryCancelBar";
import useRequestController from "../../hooks/useRequestController";
import { generateReportDraft, saveReportFinal } from "../../services/reportApi";
import type { EditMetrics, ReportDraftResponse, ReportFinalResponse } from "../../types/report";
import EditMetricsCard from "./EditMetricsCard";
import ReportEditor from "./ReportEditor";

type ReportPanelProps = {
    sessionId: string;
};

type ReportActionType = "draft_generate" | "final_save";

type DraftPayload = {
    sessionId: string;
};

type FinalPayload = {
    sessionId: string;
    reportFinal: string;
};

type ReportPayload = DraftPayload | FinalPayload;

export default function ReportPanel({ sessionId }: ReportPanelProps) {
    const [draftText, setDraftText] = useState<string | undefined>(undefined);
    const [finalText, setFinalText] = useState("");
    const [editMetrics, setEditMetrics] = useState<EditMetrics | undefined>(undefined);
    const [snackbarOpen, setSnackbarOpen] = useState(false);
    const requestController = useRequestController<ReportActionType, ReportPayload>();

    const isGeneratingDraft =
        requestController.state.status === "loading" && requestController.state.actionType === "draft_generate";
    const isSavingFinal =
        requestController.state.status === "loading" && requestController.state.actionType === "final_save";
    const isBusy = requestController.state.status === "loading";

    const handleGenerateDraft = async () => {
        if (isBusy) {
            return;
        }

        const result = await requestController.run<ReportDraftResponse>({
            actionType: "draft_generate",
            payload: { sessionId },
            requestFn: (payload) => generateReportDraft(payload.sessionId),
        });

        if (result.status === "success") {
            setDraftText(result.data.report_draft);
            if (finalText.trim().length === 0) {
                setFinalText(result.data.report_draft);
            }
            setEditMetrics(undefined);
        }
    };

    const handleSaveFinal = async () => {
        if (isBusy) {
            return;
        }

        const result = await requestController.run<ReportFinalResponse>({
            actionType: "final_save",
            payload: { sessionId, reportFinal: finalText },
            requestFn: (payload) => saveReportFinal(payload.sessionId, (payload as FinalPayload).reportFinal),
        });

        if (result.status === "success") {
            setEditMetrics(result.data.edit_metrics);
            setSnackbarOpen(true);
        }
    };

    const handleRetry = async () => {
        if (requestController.state.status === "loading") {
            return;
        }

        const result = await requestController.retry<ReportDraftResponse | ReportFinalResponse>();

        if (result.status === "success") {
            if (result.actionType === "draft_generate") {
                const data = result.data as ReportDraftResponse;
                setDraftText(data.report_draft);
                if (finalText.trim().length === 0) {
                    setFinalText(data.report_draft);
                }
                setEditMetrics(undefined);
                return;
            }

            const data = result.data as ReportFinalResponse;
            setEditMetrics(data.edit_metrics);
            setSnackbarOpen(true);
        }
    };

    const handleCancel = () => {
        requestController.cancel();
    };

    return (
        <Stack spacing={2}>
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <Box>
                    <Typography variant="h4" fontWeight={700} gutterBottom>
                        Report
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        Session ID: {sessionId}
                    </Typography>
                </Box>
                <Button
                    variant="outlined"
                    onClick={handleGenerateDraft}
                    disabled={isBusy}
                    startIcon={isGeneratingDraft ? <CircularProgress size={16} /> : undefined}
                >
                    Generate Draft
                </Button>
            </Box>
            <Divider />
            <Box>
                <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                    Draft
                </Typography>
                <Paper variant="outlined" sx={{ p: 2, minHeight: 160, bgcolor: "background.default" }}>
                    <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>
                        {draftText && draftText.trim().length > 0 ? draftText : "未生成"}
                    </Typography>
                </Paper>
            </Box>
            <ReportEditor
                value={finalText}
                onChange={setFinalText}
                onSave={handleSaveFinal}
                isSaving={isSavingFinal}
                disabled={isBusy}
            />
            {editMetrics && <EditMetricsCard metrics={editMetrics} />}
            <RetryCancelBar status={requestController.state.status} onRetry={handleRetry} onCancel={handleCancel} />
            <RequestErrorBanner message={requestController.state.error} />
            <Snackbar
                open={snackbarOpen}
                autoHideDuration={3000}
                onClose={() => setSnackbarOpen(false)}
                anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
            >
                <Alert severity="success" variant="filled" onClose={() => setSnackbarOpen(false)}>
                    Finalを保存しました。
                </Alert>
            </Snackbar>
        </Stack>
    );
}
