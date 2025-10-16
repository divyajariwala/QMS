import React from 'react';
import { Paper, Stack, Typography } from '@mui/material';

const ComplaintNarrative: React.FC = () => {
  return (
    <Paper
      variant="outlined"
      sx={{
        p: 2,
        borderRadius: 2,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Stack direction="row" alignItems="center" spacing={1} p={2}>
        <Typography
          sx={{
            fontFamily: 'Roboto, sans-serif',
            fontWeight: 600,
            fontStyle: 'normal',
            fontSize: 16,
            lineHeight: 1,
            letterSpacing: '0.04em',
            color: '#29323A',
          }}
        >
          Narrative
        </Typography>
      </Stack>

      <Typography
        variant="body2"
        sx={{
          fontFamily: 'Helvetica, sans-serif',
          fontWeight: 400,
          fontStyle: 'normal',
          fontSize: 16,
          lineHeight: '21px',
          letterSpacing: '0.04em',
          color: '#29323A',
          whiteSpace: 'pre-line',
          overflowY: 'auto',
          p: 2,
        }}
      >
        Education{'\n'}
        Travenzil Pen Function: Dose Confirmation{'\n\n'}

        The patient can ensure that the dose was delivered by first observing the medication within the syringe prior
        to injection and visually confirming the medication is no longer in the syringe following the injection. Dose
        delivery for the Pen is confirmed by seeing the gray plunger at the top of the clear base. Additionally, patients
        hear two loud clicks when injecting (second loud click also indicates the injection is complete). While some
        patients may prefer to only rely on feeling a needle stick or hearing the 2nd loud click, the final plunger position
        confirms dose delivery. Travenzil Pen Components: Lock Ring Before beginning the injection steps, turning the Lock
        Ring back and forth from the "Lock" to "Unlock" position does not harm the pen. The Lock Ring is a safety feature
        to make sure you do not accidentally press the injection button before you are ready.
      </Typography>
    </Paper>
  );
};

export default ComplaintNarrative;