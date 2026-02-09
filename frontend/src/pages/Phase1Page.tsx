import { Card, CardContent, Stack, Typography } from "@mui/material";

export default function Phase1Page() {
    return (
        <Stack spacing={3}>
            <Typography variant="h4" fontWeight={700}>
                Phase 1: Goal Setting
            </Typography>
            <Card>
                <CardContent>
                    <Typography variant="body1">
                        ここにゴール設定UIを実装予定です。次のIssueでフォームや入力保持を追加します。
                    </Typography>
                </CardContent>
            </Card>
        </Stack>
    );
}
