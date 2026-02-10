import { Alert, Box, Button, CircularProgress, Divider, Paper, Snackbar, Stack, Typography } from "@mui/material";
import { useState } from "react";
import { generateReportDraft, saveReportFinal } from "../../services/reportApi";
import type { EditMetrics } from "../../types/report";
import EditMetricsCard from "./EditMetricsCard";
import ReportEditor from "./ReportEditor";

type ReportPanelProps = {
    sessionId: string;
};

type LastAction = "draft" | "save";

export default function ReportPanel({ sessionId }: ReportPanelProps) {
    const [draftText, setDraftText] = useState<string | undefined>(undefined);
    const [finalText, setFinalText] = useState("");
    const [isGeneratingDraft, setIsGeneratingDraft] = useState(false);
    const [isSavingFinal, setIsSavingFinal] = useState(false);
    const [editMetrics, setEditMetrics] = useState<EditMetrics | undefined>(undefined);
    const [error, setError] = useState<string | undefined>(undefined);
    const [lastAction, setLastAction] = useState<LastAction | undefined>(undefined);
    const [snackbarOpen, setSnackbarOpen] = useState(false);

    const handleGenerateDraft = async () => {
        if (isGeneratingDraft) {
            return;
        }

        setIsGeneratingDraft(true);
        setError(undefined);
        setLastAction(undefined);

        try {
            const response = await generateReportDraft(sessionId);
            setDraftText(response.report_draft);
            if (finalText.trim().length === 0) {
                setFinalText(response.report_draft);
            }
            setEditMetrics(undefined);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Draftの生成に失敗しました。");
            setLastAction("draft");
        } finally {
            setIsGeneratingDraft(false);
        }
    };

    const handleSaveFinal = async () => {
        if (isSavingFinal) {
            return;
        }

        setIsSavingFinal(true);
        setError(undefined);
        setLastAction(undefined);

        try {
            const response = await saveReportFinal(sessionId, finalText);
            setEditMetrics(response.edit_metrics);
            setSnackbarOpen(true);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Finalの保存に失敗しました。");
            setLastAction("save");
        } finally {
            setIsSavingFinal(false);
        }
    };

    const handleRetry = async () => {
        if (lastAction === "draft") {
            await handleGenerateDraft();
        }
        if (lastAction === "save") {
            await handleSaveFinal();
        }
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
                    disabled={isGeneratingDraft}
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
            <ReportEditor value={finalText} onChange={setFinalText} onSave={handleSaveFinal} isSaving={isSavingFinal} />
            {editMetrics && <EditMetricsCard metrics={editMetrics} />}
            {error && (
                <Alert
                    severity="error"
                    action={
                        <Button color="inherit" size="small" onClick={handleRetry} disabled={!lastAction}>
                            Retry
                        </Button>
                    }
                >
                    {error}
                </Alert>
            )}
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
