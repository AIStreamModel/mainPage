import React, { useEffect, useState } from 'react';
import { Paper, Typography } from '@mui/material';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';

const generateMockViewerData = (prevData) => {
  const lastValue = prevData.length > 0 ? prevData[prevData.length - 1].viewers : 90000;
  const newValue = Math.max(100, Math.min(1200, lastValue + (Math.random() - 0.5) * 50));

  const now = new Date();
  const label = now.toLocaleTimeString([], { minute: '2-digit', second: '2-digit' });

  return [...prevData.slice(-19), { time: label, viewers: Math.floor(newValue) }];
};

const ViewerTrendSection = () => {
  const [viewerData, setViewerData] = useState([]);

  useEffect(() => {
    const interval = setInterval(() => {
      setViewerData(prev => generateMockViewerData(prev));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <Paper elevation={4} sx={{
      height: 240,
      backgroundColor: '#1e1e1e',
      borderRadius: '1px',
      color: '#fff',
      p: 2,
      mb: 2,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'flex-start'
    }}>
      <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
        Stream Performance(模擬直播人數)
      </Typography>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={viewerData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#444" />
          <XAxis dataKey="time" tick={{ fill: '#ccc', fontSize: 12 }} />
          <YAxis domain={[0, 1000]} tick={{ fill: '#ccc', fontSize: 12 }} tickFormatter={(v) => `${v.toLocaleString()}`} />
          <Tooltip formatter={(v) => `$${v.toLocaleString()}`} labelStyle={{ color: '#fff' }} contentStyle={{ backgroundColor: '#333', borderColor: '#555' }} />
          <Line type="monotone" dataKey="viewers" stroke="#8884d8" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </Paper>
  );
};

export default ViewerTrendSection;
