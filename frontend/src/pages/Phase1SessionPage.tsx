import { Alert, Stack } from "@mui/material";
import { useParams } from "react-router-dom";
import ChatPanel from "../components/chat/ChatPanel";

export default function Phase1SessionPage() {
    const { sessionId } = useParams();

    if (!sessionId) {
        return (
            <Stack spacing={2}>
                <Alert severity="warning">セッションIDが見つかりませんでした。</Alert>
            </Stack>
        );
    }

    return <ChatPanel phase={1} sessionId={sessionId} />;
}
