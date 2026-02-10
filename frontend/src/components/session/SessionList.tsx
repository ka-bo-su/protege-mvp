import {
    Button,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Typography,
} from "@mui/material";
import type { SessionSummary } from "../../types/session";

type SessionListProps = {
    sessions: SessionSummary[];
    onOpen: (sessionId: string) => void;
};

export default function SessionList({ sessions, onOpen }: SessionListProps) {
    if (sessions.length === 0) {
        return (
            <Typography variant="body1" color="text.secondary">
                まだセッションがありません。新規セッションを開始してください。
            </Typography>
        );
    }

    return (
        <TableContainer>
            <Table size="small">
                <TableHead>
                    <TableRow>
                        <TableCell>日付</TableCell>
                        <TableCell>Phase</TableCell>
                        <TableCell align="right">Open</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {sessions.map((session) => (
                        <TableRow key={session.id} hover>
                            <TableCell>{session.session_date}</TableCell>
                            <TableCell>Phase {session.phase}</TableCell>
                            <TableCell align="right">
                                <Button size="small" variant="outlined" onClick={() => onOpen(session.id)}>
                                    Open
                                </Button>
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    );
}
