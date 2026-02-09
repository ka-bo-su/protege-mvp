import { Card, CardContent, Stack, Typography } from "@mui/material";

export default function Phase3Page() {
    return (
        <Stack spacing={3}>
            <Typography variant="h4" fontWeight={700}>
                Phase 3: Daily Review
            </Typography>
            <Card>
                <CardContent>
                    <Typography variant="body1">
                        ここに日次振り返りUIを実装予定です。次のIssueで詳細を追加します。
                    </Typography>
                </CardContent>
            </Card>
        </Stack>
    );
}
