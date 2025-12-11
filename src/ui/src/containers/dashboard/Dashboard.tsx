import * as React from 'react';
import { Box, Typography, Card, CardContent, Grid } from '@mui/material';
import dashboardBg from '../../assets/images/qmsBackground.svg';
import { useAuth } from "react-oidc-context";

const HEADER_HEIGHT = 65; 

const Dashboard = () => {
  const auth = useAuth();
  const displayName = `${auth?.user?.profile?.given_name ?? ""}`.trim();
  return (
    <Box
      component="main"
      sx={{
        height: `calc(100vh - ${HEADER_HEIGHT}px)`,
        width: '100%',
        backgroundColor: '#474645',
        backgroundImage: `url(${dashboardBg})`,
        backgroundRepeat: 'no-repeat',
        backgroundPosition: 'right center',
        backgroundSize: 'auto 100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
      }}
    >
      <Box
        sx={{
          mt: 'auto',
          mb: 'auto',
          width: '100%',
          maxWidth: 900,
          mx: 'auto',
          px: 2,
          textAlign: 'left',
        }}
      >
        <Typography variant="h3" component="h1" color="#FFF" gutterBottom>
          Welcome back, {displayName}
        </Typography>
        <Typography variant="subtitle1" color="grey.300">
          25-Feb-2025
        </Typography>
      </Box>
      <Box
        sx={{
          width: '100%',
          maxWidth: 900,
          mx: 'auto',   
          px: 2,
          mb: 4,  
        }}
        className="cardContainer"
      >
        <Card sx={{ borderRadius: 2, boxShadow: 3 }}>
          <CardContent sx={{ py: 3 }}>
            <Typography variant="body1" align="center" gutterBottom>
              Breakdown of{' '}
              <Box component="span" fontWeight="bold">
                500 narratives
              </Box>{' '}
              processed this month:
            </Typography>
            <Grid container className="cardBox">
              {[
                ['298', 'Product complaints'],
                ['102', 'Adverse events'],
                ['89', 'Others category'],
                ['75', 'Deviations identified'],
              ].map(([num, label], idx) => (
                <Grid
                  key={label}
                  item
                  xs
                  sx={{
                    textAlign: 'center',
                    px: 2,
                    ...(idx > 0 && {
                      borderLeft: '1px solid rgba(0,0,0,0.12)',
                    })
                  }}
                >
                  <Typography className="resourceNo" variant="h4">{num}</Typography>
                  <Typography className="resourceLabel" variant="body2">{label}</Typography>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
}

export default Dashboard;