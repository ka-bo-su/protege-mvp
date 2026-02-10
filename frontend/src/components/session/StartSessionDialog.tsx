import {
    Button,
    CircularProgress,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    FormControl,
    FormControlLabel,
    Radio,
    RadioGroup,
    Stack,
    Typography,
} from "@mui/material";
import { useEffect, useState } from "react";
import type { SessionPhase } from "../../types/session";

type StartSessionDialogProps = {
    open: boolean;
    loading?: boolean;
    onClose: () => void;
    onStart: (phase: SessionPhase) => void;
};

export default function StartSessionDialog({ open, loading = false, onClose, onStart }: StartSessionDialogProps) {
    const [selectedPhase, setSelectedPhase] = useState<SessionPhase | "">("");

    useEffect(() => {
        if (!open) {
            setSelectedPhase("");
        }
    }, [open]);

    const handleClose = () => {
        if (loading) {
            return;
        }
        onClose();
    };

    const handleStart = () => {
        if (!selectedPhase || loading) {
            return;
        }
        onStart(selectedPhase);
    };

    return (
        <Dialog open={open} onClose={handleClose} fullWidth maxWidth="xs">
            <DialogTitle>新規セッション開始</DialogTitle>
            <DialogContent>
                <Stack spacing={2} mt={1}>
                    <Typography variant="subtitle1" fontWeight={600}>
                        Select Phase
                    </Typography>
                    <FormControl component="fieldset">
                        <RadioGroup
                            value={selectedPhase}
                            onChange={(event) => setSelectedPhase(Number(event.target.value) as SessionPhase)}
                        >
                            <FormControlLabel value={1} control={<Radio />} label="Phase1 Goal Setting" />
                            <FormControlLabel value={3} control={<Radio />} label="Phase3 Reflection" />
                        </RadioGroup>
                    </FormControl>
                </Stack>
            </DialogContent>
            <DialogActions>
                <Button onClick={handleClose} disabled={loading}>
                    Cancel
                </Button>
                <Button
                    variant="contained"
                    onClick={handleStart}
                    disabled={!selectedPhase || loading}
                    startIcon={loading ? <CircularProgress size={16} color="inherit" /> : undefined}
                >
                    Start
                </Button>
            </DialogActions>
        </Dialog>
    );
}
