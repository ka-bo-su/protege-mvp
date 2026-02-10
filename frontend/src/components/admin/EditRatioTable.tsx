import {
    Box,
    Button,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Typography,
} from "@mui/material";
import { Link } from "react-router-dom";
import type { EditRatioItem } from "../../types/kpi";

type EditRatioTableProps = {
    items: EditRatioItem[];
};

const formatRatio = (value: number) => `${(value * 100).toFixed(1)}%`;

export default function EditRatioTable({ items }: EditRatioTableProps) {
    return (
        <TableContainer>
            <Table>
                <TableHead>
                    <TableRow>
                        <TableCell>Date</TableCell>
                        <TableCell>Session ID</TableCell>
                        <TableCell align="right">Ratio</TableCell>
                        <TableCell align="right">Added</TableCell>
                        <TableCell align="right">Removed</TableCell>
                        <TableCell>Open Session</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {items.length === 0 ? (
                        <TableRow>
                            <TableCell colSpan={6}>
                                <Box py={2} textAlign="center">
                                    <Typography color="text.secondary">No data</Typography>
                                </Box>
                            </TableCell>
                        </TableRow>
                    ) : (
                        items.map((item) => (
                            <TableRow key={item.session_id} hover>
                                <TableCell>{item.session_date}</TableCell>
                                <TableCell>
                                    <Typography variant="body2" color="text.secondary">
                                        {item.session_id}
                                    </Typography>
                                </TableCell>
                                <TableCell align="right">{formatRatio(item.ratio)}</TableCell>
                                <TableCell align="right">{item.chars_added}</TableCell>
                                <TableCell align="right">{item.chars_removed}</TableCell>
                                <TableCell>
                                    <Button
                                        component={Link}
                                        to={`/phase3/session/${item.session_id}`}
                                        size="small"
                                        variant="outlined"
                                    >
                                        Open
                                    </Button>
                                </TableCell>
                            </TableRow>
                        ))
                    )}
                </TableBody>
            </Table>
        </TableContainer>
    );
}
