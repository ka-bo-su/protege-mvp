import { Alert, Stack } from "@mui/material";
import { useParams } from "react-router-dom";
import ChatPanel from "../components/chat/ChatPanel";
import ReportPanel from "../components/report/ReportPanel";
import SplitWorkspace from "../components/workspace/SplitWorkspace";

type Phase3WorkspacePageProps = {
    sessionId?: string;
};

export default function Phase3WorkspacePage({ sessionId: sessionIdProp }: Phase3WorkspacePageProps) {
    const params = useParams();
    const sessionId = sessionIdProp ?? params.sessionId;

    if (!sessionId) {
        return (
            <Stack spacing={2}>
                <Alert severity="warning">セッションIDが見つかりませんでした。</Alert>
            </Stack>
        );
    }

    return (
        <SplitWorkspace
            left={<ChatPanel phase={3} sessionId={sessionId} />}
            right={<ReportPanel sessionId={sessionId} />}
        />
    );
}
