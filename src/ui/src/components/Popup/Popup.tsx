import React, { useState, ChangeEvent, MouseEvent } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Typography,
  Box,
} from '@mui/material';

interface PopupProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (value: string) => void;
}

const Popup = ({ open, onClose, onSubmit }: PopupProps) => {
  const [inputValue, setInputValue] = useState<string>('');
  const MAX_LENGTH = 420;
  const handleInputChange = (event: ChangeEvent<HTMLInputElement>): void => {
  const newValue = event.target.value;
  if (newValue.length <= MAX_LENGTH) {
    setInputValue(newValue);
  } 
};

  const handleSubmit = (event: MouseEvent<HTMLButtonElement>): void => {
    event.preventDefault();
    onSubmit(inputValue);
    setInputValue('');
  };

  const handleCancel = (event: MouseEvent<HTMLButtonElement>): void => {
    event.preventDefault();
    setInputValue('');
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      PaperProps={{
        sx: {
          width: '508px',
          height: '513px',
          display: 'flex',
          flexDirection: 'column',
          boxSizing: 'border-box',
        },
      }}
    >
      <DialogTitle
        sx={{
          height: '64px',
          display: 'flex',
          alignItems: 'center',
          px: 2,
          borderBottom: '1px solid rgba(0,0,0,0.12)',
          fontFamily: `'Inter', sans-serif`,
          fontWeight: 600,
          fontSize: '20px',
          lineHeight: 1,
          letterSpacing: '0%',
          fontStyle: 'normal',
          boxSizing: 'border-box',
        }}
      >
        Add Narrative Manually
      </DialogTitle>
      <DialogContent
        sx={{
          flexGrow: 1,
          padding: 0,
          overflowY: 'auto',
          boxSizing: 'border-box',
          display: 'flex',
          flexDirection: 'column',
          marginTop: '20px',
          alignItems: 'center',        // <-- horizontal center 
        }}
      >
        <Box sx={{ width: '100%', maxWidth: '460px' }}>
          <Typography
            variant="body1"
            gutterBottom
            sx={{
              fontFamily: `'Roboto', sans-serif`,
              fontWeight: 500,
              fontSize: '14px',
              lineHeight: '20px',
              letterSpacing: '-0.1px',
              fontStyle: 'normal',   // font-style only supports normal, italic, oblique
            }}
          >
            Narrative
          </Typography>
          <TextField
            autoFocus
            type="text"
            variant="outlined"
            value={inputValue}
            onChange={handleInputChange}
            multiline
            sx={{
              width: '100%',
              '& .MuiOutlinedInput-root': {
                height: 276,
                alignItems: 'flex-start',
                paddingTop: '8px',
                paddingBottom: '8px',
              },
              '& .MuiOutlinedInput-input': {
                height: '100%',
                boxSizing: 'border-box',
                padding: '0 14px',
                whiteSpace: 'pre-wrap',
                overflowWrap: 'break-word',
              },
            }}
          />
          <Typography variant="body1" gutterBottom sx={{
            fontFamily: `'Roboto', sans-serif`,
            fontWeight: 400,
            fontSize: '14px',
            lineHeight: '20px',
            letterSpacing: '-0.1px',
            fontStyle: 'normal',
          }}>
            {`${inputValue.length}/${MAX_LENGTH}`}
          </Typography>
        </Box>
      </DialogContent>

      <DialogActions
        sx={{
          height: '79px',
          px: 2,
          pb: 2,
          pt: 1,
          boxSizing: 'border-box',
          borderTop: '1px solid rgba(0, 0, 0, 0.12)',
          display: 'flex',
          justifyContent: 'flex-end',
          alignItems: 'center',
          flexShrink: 0,
          gap: '12px',
        }}
      >
        <Button
          onClick={handleCancel}
          color="primary"
          sx={{
            width: '83px',
            height: '36px',
            fontFamily: `'Roboto', sans-serif`,
            paddingTop: '8px',
            paddingRight: '20px',
            paddingBottom: '8px',
            paddingLeft: '20px',
            borderRadius: '10px',
            border: '1px solid #DAE0E6',
            opacity: 1,
            color: '#272D37',
            transform: 'rotate(0deg)',
            gap: '8px',
            textTransform: 'none',
            '&:hover': {
              borderColor: '#BAC3D2',
              backgroundColor: 'rgba(218, 224, 230, 0.1)',
            },
          }}
        >
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          color="primary"
          variant="contained"
          sx={{
            width: '99px',
            height: '36px',
            fontFamily: `'Roboto', sans-serif`,
            paddingTop: '8px',
            paddingRight: '20px',
            paddingBottom: '8px',
            paddingLeft: '20px',
            borderRadius: '10px',
            backgroundColor: '#0089EB',
            opacity: 1,
            transform: 'rotate(0deg)',
            gap: '8px',
            textTransform: 'none',
            '&:hover': {
              backgroundColor: '#0076cc',
            },
          }}
        >
          Submit
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default Popup;