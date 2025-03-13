import * as React from 'react';
import Box from '@mui/material/Box';
import List from '@mui/material/List';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import Divider from '@mui/material/Divider';

/**
 * Render a sidebar.
 *
 * @returns A react component.
 */
export default function Sidebar() {

    const [selectedIndex, setSelectedIndex] = React.useState(1);

    /**
     * Hnadles the list item click event.
     *
     * @param event - MouseEvent
     * @param index - The element index.
     */
    const handleListItemClick = (
        event: React.MouseEvent<HTMLDivElement, MouseEvent>,
        index: number,
    ) => {
        setSelectedIndex(index);
    };

    return (
        <Box sx={{ width: '100%', maxWidth: 360, bgcolor: 'background.paper' }}>
            <Divider />
            <nav aria-label="sidebar" className='sidebar'>
                <List>
                    <ListItemButton
                        selected={selectedIndex === 2}
                        onClick={(event) => handleListItemClick(event, 2)}
                    >
                        <ListItemText primary="Home" />
                    </ListItemButton>
                </List>
            </nav>
        </Box>
    );
}
