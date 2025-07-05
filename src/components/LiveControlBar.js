// components/LiveControlBar.js
import React from 'react';
import { Box, Button } from '@mui/material';

const LiveControlBar = ({ isLive, startLive, stopLive, runEmotion }) => {
  return (
    <Box display="flex" gap={2}>
      <Button variant="contained" color="primary" onClick={startLive} disabled={isLive}>
        開始直播
      </Button>
      <Button variant="contained" color="secondary" onClick={stopLive} disabled={!isLive}>
        結束直播
      </Button>
      <Button variant="outlined" onClick={runEmotion}>
        進行情緒分析
      </Button>
    </Box>
  );
};

export default LiveControlBar;
