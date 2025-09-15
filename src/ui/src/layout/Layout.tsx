import * as React from 'react';
import { Box, Toolbar } from '@mui/material';
import { Outlet, useLocation } from 'react-router';
import Header from '../components/header/Header';
import Sidebar from '@components/sidebar/Sidebar';
import Footer from '@components/Footer/Footer';

const HEADER_HEIGHT = 65;      
const SIDEBAR_WIDTH = 280;   

const Layout = () => {
  const { pathname } = useLocation();
  
  const isHome = pathname === "/" || pathname.toLowerCase() === "/home";

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
      }}
    >
      <Header />
      <Toolbar sx={{ minHeight: HEADER_HEIGHT }} />

      <Box
        component="div"
        sx={{
          display: 'flex',
          //flexGrow: 1,
          overflow: 'hidden',
          height: `calc(100vh - ${HEADER_HEIGHT}px)`,
        }}
      >
        <Box
          component="aside"
          sx={{
            width: SIDEBAR_WIDTH,
            flexShrink: 0,
            height: '100%',
            overflowY: 'auto',
            marginTop: '5px'
          }}
        >
          <Sidebar />
        </Box>

        <Box
          component="main"
          sx={{
            flexGrow: 1,
            height: '100%',
            overflowY: 'auto',
             minWidth: 0,
             flexDirection: "column",
          }}
        >
          <Outlet />
          {!isHome && (
            <Box
              component="footer"
            >
              <Footer />
            </Box>
          )}
        </Box>
      </Box>
    </Box>
  );
}

export default Layout;
