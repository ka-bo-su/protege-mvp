import { Box, Button, CircularProgress, TextField, Typography } from "@mui/material";

type ReportEditorProps = {
    value: string;
    onChange: (value: string) => void;
    onSave: () => void;
    isSaving: boolean;
};

export default function ReportEditor({ value, onChange, onSave, isSaving }: ReportEditorProps) {
    return (
        <Box>
            <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                Final
            </Typography>
            <TextField
                fullWidth
                multiline
                minRows={8}
                value={value}
                onChange={(event) => onChange(event.target.value)}
                placeholder="最終レポートを編集してください"
            />
            <Box sx={{ display: "flex", justifyContent: "flex-end", mt: 2 }}>
                <Button
                    variant="contained"
                    onClick={onSave}
                    disabled={isSaving}
                    startIcon={isSaving ? <CircularProgress size={16} /> : undefined}
                >
                    Save Final
                </Button>
            </Box>
        </Box>
    );
}
