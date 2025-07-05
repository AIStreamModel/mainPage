import React from 'react';
import { Box, IconButton, Tooltip } from '@mui/material';
import {
  Home,
  ShowChart,
  BarChart,
  AttachMoney,
  Public,
  InsertDriveFile,
  TrendingUp,
  Settings,
  ChevronLeft,
  ChevronRight,
} from '@mui/icons-material';

const menuItems = [
  { icon: <Home />, label: 'Dashboard' },
  { icon: <ShowChart />, label: 'Stocks' },
  { icon: <BarChart />, label: 'Markets' },
  { icon: <AttachMoney />, label: 'Currencies' },
  { icon: <Public />, label: 'Global' },
  { icon: <InsertDriveFile />, label: 'Portfolio' },
  { icon: <TrendingUp />, label: 'Performance' },
  { icon: <Settings />, label: 'Settings' },
];

const SidebarMenu = ({ expanded, toggleSidebar }) => {
  return (
    <Box
      sx={{
        width: expanded ? 220 : 64,
        height: '100vh',
        backgroundColor: '#1E1E1E',
        color: '#fff',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'flex-start',
        transition: 'width 0.3s ease',
        position: 'fixed',
        zIndex: 1000,
      }}
    >
      {/* Toggle Button */}
      <Box sx={{ display: 'flex', justifyContent: expanded ? 'flex-end' : 'center', p: 1 }}>
        <Tooltip title={expanded ? '收合側邊欄' : '展開側邊欄'}>
          <IconButton
            onClick={toggleSidebar}
            sx={{
              color: '#fff',
              transition: 'transform 0.2s',
              '&:hover': {
                transform: 'scale(1.2)',
                backgroundColor: 'rgba(255,255,255,0.1)',
              },
            }}
          >
            {expanded ? <ChevronLeft /> : <ChevronRight />}
          </IconButton>
        </Tooltip>
      </Box>

      {/* Menu Items */}
      <Box sx={{ mt: 2 }}>
        {menuItems.map((item, index) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              alignItems: 'center',
              px: 2,
              py: 1.5,
              cursor: 'pointer',
              transition: 'background 0.2s',
              '&:hover': {
                backgroundColor: 'rgba(255,255,255,0.1)',
              },
            }}
          >
            {item.icon}
            {expanded && (
              <Box component="span" sx={{ ml: 2, whiteSpace: 'nowrap', fontSize: 14 }}>
                {item.label}
              </Box>
            )}
          </Box>
        ))}
      </Box>
    </Box>
  );
};

export default SidebarMenu;
