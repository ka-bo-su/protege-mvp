import { AppBar, Box, Button, Container, Toolbar, Typography } from "@mui/material";
import { NavLink, Outlet } from "react-router-dom";

const navItems = [
    { label: "Home", to: "/" },
    { label: "Sessions", to: "/sessions" },
    { label: "Phase1", to: "/phase1" },
    { label: "Phase3", to: "/phase3" },
    { label: "Admin KPI", to: "/admin/kpi/edit-ratio" },
];

export default function AppShell() {
    return (
        <Box display="flex" flexDirection="column" minHeight="100vh">
            <AppBar position="static" color="primary">
                <Toolbar sx={{ gap: 2 }}>
                    <Typography variant="h6" sx={{ flexGrow: 1 }}>
                        t2ai MVP
                    </Typography>
                    {navItems.map((item) => (
                        <Button
                            key={item.to}
                            component={NavLink}
                            to={item.to}
                            color="inherit"
                            sx={{
                                textTransform: "none",
                                fontWeight: 600,
                                "&.active": {
                                    textDecoration: "underline",
                                },
                            }}
                        >
                            {item.label}
                        </Button>
                    ))}
                </Toolbar>
            </AppBar>
            <Box component="main" flexGrow={1} py={4}>
                <Container maxWidth="md">
                    <Outlet />
                </Container>
            </Box>
        </Box>
    );
}
