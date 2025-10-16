import { createTheme, Theme } from "@mui/material/styles";

const colors = {
  palette: {
    primary: {
      main: "#3078A0",
    },
    yellow: {
      main: "#FFA929",
      dark: "#D3702A",
    },
    red: {
      main: "#C80E0E",
    },
    secondary: {
      main: "#0ab093",
    },
    error: {
      main: "#E1242A",
    },
    success: {
      main: "#249A2A",
    },
    gray: {
      light: "#CBCBCB",
      dark: "#6B7280",
      darker: "#6E6E6E",
      bg: "#F0F2F5",
    },
  },
};

const theme = createTheme(
  {
    shape: {
      borderRadius: 5,
    },
    ...colors,
    typography: {
      fontFamily: "Inter",
    },
  },
  {
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: "uppercase",
            borderRadius: "2px",
          },
        },
      },
    },
  }
);

export default theme as Theme & typeof colors;
