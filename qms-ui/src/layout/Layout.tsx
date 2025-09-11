import { Box } from "@mui/system";
import { Outlet } from "react-router";
import Header from "../components/header/Header";

/**
 * The main layout for the application.
 *
 * @returns A react component.
 */
const Layout = () => {
  return (
    <Box sx={{ minHeight: "100vh" }}>
      <Header />
      <Box
        sx={{
          marginTop: '3.5em'
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
};

export default Layout;
