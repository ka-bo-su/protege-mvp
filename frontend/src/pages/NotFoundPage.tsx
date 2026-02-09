import { Button, Stack, Typography } from "@mui/material";
import { Link } from "react-router-dom";

export default function NotFoundPage() {
    return (
        <Stack spacing={2} alignItems="flex-start">
            <Typography variant="h4" fontWeight={700}>
                404 Not Found
            </Typography>
            <Typography variant="body1">ページが見つかりませんでした。</Typography>
            <Button component={Link} to="/" variant="contained">
                Homeへ戻る
            </Button>
        </Stack>
    );
}
