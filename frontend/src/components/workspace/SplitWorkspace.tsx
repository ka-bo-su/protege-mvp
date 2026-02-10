import { Box, Grid } from "@mui/material";
import { ReactNode } from "react";

type SplitWorkspaceProps = {
    left: ReactNode;
    right: ReactNode;
};

export default function SplitWorkspace({ left, right }: SplitWorkspaceProps) {
    return (
        <Grid container spacing={3} alignItems="stretch">
            <Grid item xs={12} lg={6}>
                <Box sx={{ height: "100%" }}>{left}</Box>
            </Grid>
            <Grid item xs={12} lg={6}>
                <Box sx={{ height: "100%" }}>{right}</Box>
            </Grid>
        </Grid>
    );
}
