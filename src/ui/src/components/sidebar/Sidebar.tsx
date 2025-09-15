import * as React from 'react';
import Box from '@mui/material/Box';
import List from '@mui/material/List';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Divider from '@mui/material/Divider';
import Collapse from '@mui/material/Collapse';
import HomeOutlinedIcon from '@mui/icons-material/HomeOutlined';
import ChatBubbleOutlineOutlinedIcon from '@mui/icons-material/ChatBubbleOutlineOutlined';
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined';
import TimelineOutlinedIcon from '@mui/icons-material/TimelineOutlined';
import MoreHorizOutlinedIcon from '@mui/icons-material/MoreHorizOutlined';
import CallSplitOutlinedIcon from '@mui/icons-material/CallSplitOutlined';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';
import { useNavigate } from 'react-router-dom';

export default function Sidebar() {
  const [selectedIndex, setSelectedIndex] = React.useState<number>(0);
  const [deviationsOpen, setDeviationsOpen] = React.useState<boolean>(false);

  const navigate = useNavigate();

  const handleListItemClick = (
    _event: React.MouseEvent<HTMLDivElement, MouseEvent>,
    index: number
  ) => {
    setSelectedIndex(index);
    switch(index) {
      case 0:
        navigate('/');
        break;
      case 1:
        navigate('/narratives');
        break;
      case 2:
        navigate('/product-complaints');
        break;
      case 3:
        navigate('/adverse-events');
        break;
      case 4:
        navigate('/others-category');
        break;
      case 5:
        navigate('/deviations');
        break;
      case 6:
        navigate('/deviations/new');
        break;
      default:
        break;
    }
  };

const toggleDeviations = () => {
  setDeviationsOpen(open => !open);
};

  return (
    <Box
      component="nav"
      sx={{
        width: 280,
        bgcolor: 'background.paper',
        borderTopRightRadius: 16,
        borderBottomRightRadius: 16,
        borderRight: 1,
        borderColor: 'divider',
        flexShrink: 0,
        height: 'calc(100vh - 65px)', 
        overflowY: 'auto',
        p: 1,
      }}
      aria-label="Sidebar navigation"
    >
      <List disablePadding>
        <ListItemButton
          selected={selectedIndex === 0}
          onClick={e => handleListItemClick(e, 0)}
        >
          <ListItemIcon>
            <HomeOutlinedIcon />
          </ListItemIcon>
          <ListItemText primary="Home" />
        </ListItemButton>
        <Divider />

        <ListItemButton
          selected={selectedIndex === 1}
          onClick={e => handleListItemClick(e, 1)}
        >
          <ListItemIcon>
            <ChatBubbleOutlineOutlinedIcon />
          </ListItemIcon>
          <ListItemText primary="Narratives" />
        </ListItemButton>
        <Divider />

        <ListItemButton
          selected={selectedIndex === 2}
          onClick={e => handleListItemClick(e, 2)}
        >
          <ListItemIcon>
            <DescriptionOutlinedIcon />
          </ListItemIcon>
          <ListItemText primary="Product complaints" />
        </ListItemButton>
        <Divider />

        <ListItemButton
          selected={selectedIndex === 3}
          onClick={e => handleListItemClick(e, 3)}
        >
          <ListItemIcon>
            <TimelineOutlinedIcon />
          </ListItemIcon>
          <ListItemText primary="Adverse events" />
        </ListItemButton>
        <Divider />

        <ListItemButton
          selected={selectedIndex === 4}
          onClick={e => handleListItemClick(e, 4)}
        >
          <ListItemIcon>
            <MoreHorizOutlinedIcon />
          </ListItemIcon>
          <ListItemText primary="Others category" />
        </ListItemButton>
        <Divider />

        {/* Deviations with collapse */}
        <ListItemButton onClick={toggleDeviations}>
          <ListItemIcon>
            <CallSplitOutlinedIcon />
          </ListItemIcon>
          <ListItemText primary="Deviations" />
          {deviationsOpen ? <ExpandLess /> : <ExpandMore />}
        </ListItemButton>
        <Collapse in={deviationsOpen} timeout="auto" unmountOnExit>
          <List component="div" disablePadding>
            <ListItemButton
              sx={{ pl: 4 }}
              selected={selectedIndex === 5}
              onClick={e => handleListItemClick(e, 5)}
            >
              <ListItemText primary="View all deviations" />
            </ListItemButton>
            <ListItemButton
              sx={{ pl: 4 }}
              selected={selectedIndex === 6}
              onClick={e => handleListItemClick(e, 6)}
            >
              <ListItemText primary="Create new deviation" />
            </ListItemButton>
          </List>
        </Collapse>
      </List>
    </Box>
  );
}
