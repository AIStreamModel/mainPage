//component/VideoSection.js
import React from 'react';
import { Card, CardContent, Typography, Divider } from '@mui/material';
import VideoComponent from './VideoComponent';

const VideoSection = ({ socket, isLive, pythonOutput }) => {
  return (
    <Card elevation={3}>
      <CardContent>
        <Typography variant="h6" gutterBottom>直播畫面</Typography>
        <VideoComponent socket={socket} isLive={isLive} />
        <Divider sx={{ marginY: 2 }} />
        <Typography>{pythonOutput || '尚未執行分析'}</Typography>
        <video style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
      </CardContent>
    </Card>
  );
};

export default VideoSection;
