import React from 'react';
import {
  Box,
  Button,
  Chip,
  Grid,
  Stack,
  Typography,
  Paper,
} from '@mui/material';
import EventIcon from '@mui/icons-material/Event';
import CheckIcon from '@mui/icons-material/Check';

interface ComplaintHeaderCardProps {
  status: string;
  caseId: string;
  overdueDays: number;
  primaryReporter: {
    name: string;
    location: string;
  };
  patientName: string;
  physicianName: string;
  drug: string;
  lotNumber: string | number;
  doseAmount: string;
  expirationDate: string;
  partNumber: string | number;
  onApproveAndSend?: () => void;
}

const ComplaintHeaderCard: React.FC<ComplaintHeaderCardProps> = ({
  status,
  caseId,
  overdueDays,
  primaryReporter,
  patientName,
  physicianName,
  drug,
  lotNumber,
  doseAmount,
  expirationDate,
  partNumber,
  onApproveAndSend,
}) => {
  return (
    <Paper
      sx={{
        mt: 3,
        p: 3,
        position: 'relative', 
        backgroundColor: 'background.paper', // This ensures white background in MUI theme
      }}
    >
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          width: '100%',
          flexWrap: 'wrap',
          alignItems: 'flex-start',
          gap: 2,
        }}
      >
        {/* Left side */}
        <Box sx={{ flex: 1, minWidth: 0, paddingRight: 2 }}>
          <Stack spacing={0.5} sx={{ minWidth: 0 }}>
            <Typography
              sx={{
                fontFamily: 'Inter, sans-serif',
                fontWeight: 600,
                fontSize: 12,
                lineHeight: '24px',
                letterSpacing: '-0.1px',
                textTransform: 'uppercase',
                color: '#3B3B3B',
                whiteSpace: 'nowrap',
              }}
            >
              {status}
            </Typography>

            <Stack
              direction="row"
              spacing={2}
              alignItems="center"
              flexWrap="nowrap"
              sx={{ width: '100%' }}
            >
              <Typography
                sx={{
                  fontFamily: 'Inter, sans-serif',
                  fontWeight: 600,
                  fontSize: 28,
                  lineHeight: '38px',
                  letterSpacing: '-0.01em',
                  color: '#272D37',
                  whiteSpace: 'nowrap',
                }}
              >
                {caseId}
              </Typography>

              {overdueDays > 0 && (
                <Chip
                  icon={<EventIcon sx={{ fontSize: 16 }} />}
                  label={`Overdue by ${overdueDays} days`}
                  size="small"
                  sx={{
                    bgcolor: '#FFF2F0',
                    color: '#E2341D',
                    fontWeight: 500,
                    fontSize: 13,
                    lineHeight: '18px',
                    letterSpacing: '-0.1px',
                    fontFamily: 'Inter, sans-serif',
                    fontStyle: 'normal',
                    height: 24,
                    borderRadius: 1,
                    whiteSpace: 'nowrap',
                  }}
                />
              )}

              {/* Spacer to push button to right side */}
              <Box sx={{ flexGrow: 1 }} />

              {/* Approve and Send Button in this row */}
              <Button
                variant="contained"
                sx={{
                  textTransform: 'none',
                  background: '#0060D7',
                  fontFamily: 'Inter, sans-serif',
                  fontWeight: 600,
                  fontSize: 14,
                  lineHeight: '20px',
                  letterSpacing: 0,
                  color: '#FFFFFF',
                  height: 32,
                  '&:hover': {
                    backgroundColor: '#0050b5',
                  },
                  whiteSpace: 'nowrap',
                }}
                startIcon={<CheckIcon />}
                size="small"
                onClick={onApproveAndSend}
              >
                Approve and Send
              </Button>
            </Stack>
          </Stack>

          {/* Reporter and patient info grid */}
          <Grid container spacing={1} sx={{ mt: 1, alignItems: 'flex-start' }}>
            {/* Left block */}
            <Grid item xs={6} sm={3}>
              <Typography
                sx={{
                  fontFamily: 'Inter, sans-serif',
                  fontWeight: 400,
                  fontStyle: 'normal',
                  fontSize: 14,
                  lineHeight: '20px',
                  letterSpacing: '-0.1px',
                  color: '#5F6D7E',
                }}
              >
                Primary Reporter
              </Typography>
              <Typography
                sx={{
                  fontFamily: 'Inter, sans-serif',
                  fontWeight: 700,
                  fontStyle: 'normal',
                  fontSize: 16,
                  lineHeight: '22px',
                  letterSpacing: '-0.1px',
                  color: '#272D37',
                }}
              >
                {primaryReporter.name}
              </Typography>
              <Typography
                sx={{
                  fontFamily: 'Inter, sans-serif',
                  fontWeight: 500,
                  fontStyle: 'normal',
                  fontSize: 14,
                  lineHeight: '20px',
                  letterSpacing: '-0.1px',
                  color: '#5F6D7E',
                }}
              >
                {primaryReporter.location}
              </Typography>
            </Grid>

            {/* Right block with fields */}
            <Grid item xs={12} sm={8}>
              <Grid container spacing={2}>
                <Grid item xs={8} sm={3}>
                  <Typography
                    sx={{
                      fontFamily: 'Inter, sans-serif',
                      fontWeight: 400,
                      fontStyle: 'normal',
                      fontSize: 14,
                      lineHeight: '20px',
                      letterSpacing: '-0.1px',
                      color: '#5F6D7E',
                    }}
                  >
                    Patient Name
                  </Typography>
                  <Typography
                    sx={{
                      fontFamily: 'Inter, sans-serif',
                      fontWeight: 500,
                      fontStyle: 'normal',
                      fontSize: 14,
                      lineHeight: '20px',
                      letterSpacing: '-0.1px',
                      color: '#272D37',
                    }}
                  >
                    {patientName}
                  </Typography>
                </Grid>

                <Grid item xs={8} sm={3}>
                  <Typography
                    sx={{
                      fontFamily: 'Inter, sans-serif',
                      fontWeight: 400,
                      fontStyle: 'normal',
                      fontSize: 14,
                      lineHeight: '20px',
                      letterSpacing: '-0.1px',
                      color: '#5F6D7E',
                    }}
                  >
                    Physician
                  </Typography>
                  <Typography
                    sx={{
                      fontFamily: 'Inter, sans-serif',
                      fontWeight: 500,
                      fontStyle: 'normal',
                      fontSize: 14,
                      lineHeight: '20px',
                      letterSpacing: '-0.1px',
                      color: '#272D37',
                    }}
                  >
                    {physicianName}
                  </Typography>
                </Grid>

                <Grid item xs={8} sm={3}>
                  <Typography
                    sx={{
                      fontFamily: 'Inter, sans-serif',
                      fontWeight: 400,
                      fontStyle: 'normal',
                      fontSize: 14,
                      lineHeight: '20px',
                      letterSpacing: '-0.1px',
                      color: '#5F6D7E',
                    }}
                  >
                    Drug
                  </Typography>
                  <Typography
                    sx={{
                      fontFamily: 'Inter, sans-serif',
                      fontWeight: 500,
                      fontStyle: 'normal',
                      fontSize: 14,
                      lineHeight: '20px',
                      letterSpacing: '-0.1px',
                      color: '#272D37',
                    }}
                  >
                    {drug}
                  </Typography>
                </Grid>

                <Grid item xs={8} sm={3}>
                  <Typography
                    sx={{
                      fontFamily: 'Inter, sans-serif',
                      fontWeight: 400,
                      fontStyle: 'normal',
                      fontSize: 14,
                      lineHeight: '20px',
                      letterSpacing: '-0.1px',
                      color: '#5F6D7E',
                    }}
                  >
                    Lot #
                  </Typography>
                  <Typography
                    sx={{
                      fontFamily: 'Inter, sans-serif',
                      fontWeight: 500,
                      fontStyle: 'normal',
                      fontSize: 14,
                      lineHeight: '20px',
                      letterSpacing: '-0.1px',
                      color: '#272D37',
                    }}
                  >
                    {lotNumber}
                  </Typography>
                </Grid>

                <Grid item xs={8} sm={3}>
                  <Typography
                    sx={{
                      fontFamily: 'Inter, sans-serif',
                      fontWeight: 400,
                      fontStyle: 'normal',
                      fontSize: 14,
                      lineHeight: '20px',
                      letterSpacing: '-0.1px',
                      color: '#5F6D7E',
                    }}
                    mt={2}
                  >
                    Dose Amount
                  </Typography>
                  <Typography
                    sx={{
                      fontFamily: 'Inter, sans-serif',
                      fontWeight: 500,
                      fontStyle: 'normal',
                      fontSize: 14,
                      lineHeight: '20px',
                      letterSpacing: '-0.1px',
                      color: '#272D37',
                    }}
                  >
                    {doseAmount}
                  </Typography>
                </Grid>

                <Grid item xs={8} sm={3}>
                  <Typography
                    sx={{
                      fontFamily: 'Inter, sans-serif',
                      fontWeight: 400,
                      fontStyle: 'normal',
                      fontSize: 14,
                      lineHeight: '20px',
                      letterSpacing: '-0.1px',
                      color: '#5F6D7E',
                    }}
                    mt={2}
                  >
                    Expiration Date
                  </Typography>
                  <Typography
                    sx={{
                      fontFamily: 'Inter, sans-serif',
                      fontWeight: 500,
                      fontStyle: 'normal',
                      fontSize: 14,
                      lineHeight: '20px',
                      letterSpacing: '-0.1px',
                      color: '#272D37',
                    }}
                  >
                    {expirationDate}
                  </Typography>
                </Grid>

                <Grid item xs={8} sm={3}>
                  <Typography
                    sx={{
                      fontFamily: 'Inter, sans-serif',
                      fontWeight: 400,
                      fontStyle: 'normal',
                      fontSize: 14,
                      lineHeight: '20px',
                      letterSpacing: '-0.1px',
                      color: '#5F6D7E',
                    }}
                    mt={2}
                  >
                    Part Number
                  </Typography>
                  <Typography
                    sx={{
                      fontFamily: 'Inter, sans-serif',
                      fontWeight: 500,
                      fontStyle: 'normal',
                      fontSize: 14,
                      lineHeight: '20px',
                      letterSpacing: '-0.1px',
                      color: '#272D37',
                    }}
                  >
                    {partNumber}
                  </Typography>
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </Box>
      </Box>
    </Paper>
  );
};

export default ComplaintHeaderCard;