import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
    palette: {
        mode: "light",
        primary: {
            main: "#2563eb",
        },
        background: {
            default: "#f9fafb",
        },
    },
    typography: {
        fontFamily: "Inter, system-ui, -apple-system, sans-serif",
    },
});
