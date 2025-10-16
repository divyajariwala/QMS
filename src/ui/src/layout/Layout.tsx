import { Box, Toolbar } from "@mui/material";
import { Outlet } from "react-router";
import Header from "../components/header/Header";

const HEADER_HEIGHT = 70;

const Layout = () => {
  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        minHeight: "100vh",
      }}
    >
      <Header />
      <Toolbar sx={{ minHeight: HEADER_HEIGHT }} />
      <Box
        component="main"
        sx={{
          width: "100%",
          overflowY: "auto",
          flexDirection: "column",
          height: `calc(100vh - ${HEADER_HEIGHT}px)`,
        }}
        pt={4}
        pb={4}
        pl={14}
        pr={14}
      >
        <Outlet />
      </Box>
    </Box>
  );
};

export default Layout;
