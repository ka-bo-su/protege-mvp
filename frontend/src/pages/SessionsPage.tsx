import { Alert, Box, Button, CircularProgress, Snackbar, Stack, Typography } from "@mui/material";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import SessionList from "../components/session/SessionList";
import StartSessionDialog from "../components/session/StartSessionDialog";
import { createSession, fetchSessions } from "../services/sessionApi";
import type { SessionPhase, SessionSummary } from "../types/session";

type ErrorState = {
    message: string;
} | null;

const DEFAULT_USER_ID = 1;

export default function SessionsPage() {
    const navigate = useNavigate();
    const [sessions, setSessions] = useState<SessionSummary[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<ErrorState>(null);
    const [startDialogOpen, setStartDialogOpen] = useState(false);
    const [startLoading, setStartLoading] = useState(false);

    useEffect(() => {
        let isMounted = true;
        const loadSessions = async () => {
            setLoading(true);
            try {
                const data = await fetchSessions({ userId: DEFAULT_USER_ID });
                if (isMounted) {
                    setSessions(data);
                }
            } catch (err) {
                if (isMounted) {
                    setError({ message: err instanceof Error ? err.message : "セッション一覧の取得に失敗しました。" });
                }
            } finally {
                if (isMounted) {
                    setLoading(false);
                }
            }
        };

        loadSessions();

        return () => {
            isMounted = false;
        };
    }, []);

    const handleOpenSession = (sessionId: string) => {
        const session = sessions.find((item) => item.id === sessionId);
        if (!session) {
            return;
        }
        const path = session.phase === 1 ? `/phase1/session/${session.id}` : `/phase3/session/${session.id}`;
        navigate(path);
    };

    const handleStartSession = async (phase: SessionPhase) => {
        setStartLoading(true);
        try {
            const response = await createSession(phase);
            const sessionId = response.id;
            const path = phase === 1 ? `/phase1/session/${sessionId}` : `/phase3/session/${sessionId}`;
            setStartDialogOpen(false);
            navigate(path);
        } catch (err) {
            setError({ message: err instanceof Error ? err.message : "セッション作成に失敗しました。" });
        } finally {
            setStartLoading(false);
        }
    };

    return (
        <Stack spacing={3}>
            <Typography variant="h4" fontWeight={700}>
                Sessions
            </Typography>

            <Box>
                <Button variant="contained" onClick={() => setStartDialogOpen(true)}>
                    Start New Session
                </Button>
            </Box>

            {loading ? (
                <Box display="flex" justifyContent="center" py={6}>
                    <CircularProgress />
                </Box>
            ) : (
                <SessionList sessions={sessions} onOpen={handleOpenSession} />
            )}

            <StartSessionDialog
                open={startDialogOpen}
                loading={startLoading}
                onClose={() => setStartDialogOpen(false)}
                onStart={handleStartSession}
            />

            <Snackbar
                open={Boolean(error)}
                autoHideDuration={6000}
                onClose={() => setError(null)}
                anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
            >
                <Alert severity="error" onClose={() => setError(null)}>
                    {error?.message}
                </Alert>
            </Snackbar>
        </Stack>
    );
}
