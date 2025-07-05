// components/ChatSection.js
import React from 'react';
import { Paper, Typography, Box } from '@mui/material';

const ChatSection = ({ messages, scores }) => (
  <Paper elevation={4} sx={{
    height: 320,
    backgroundColor: '#fff',
    borderRadius: '16px',
    color: '#1e1e1e',
    p: 2,
    overflowY: 'auto',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-start'
  }}>
    <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
      聊天室
    </Typography>
    
    <Box sx={{ flex: 1, width: '100%' }}>
      {messages.map((msg, index) => (
        <Typography key={index} variant="body2" sx={{ mb: 0.5 }}>
          {msg.text}
        </Typography>
      ))}
    </Box>
  </Paper>
);

export default ChatSection;
