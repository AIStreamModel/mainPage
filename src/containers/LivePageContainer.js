import React, { useState, useEffect, useRef } from 'react';
import { Box } from '@mui/material';
import { io } from 'socket.io-client';
import LiveControlBar from '../components/LiveControlBar';
import VideoSection from '../components/VideoSection';
import ChatSection from '../components/ChatSection';
import ViewerTrendSection from '../components/ViewerTrendSection'; // 假設你將右上角人數圖表拆成這個 component

const LivePageContainer = ({ expanded }) => {
  const [messages, setMessages] = useState([]);
  const [isLive, setIsLive] = useState(true);
  const [pythonOutput, setPythonOutput] = useState('');
  const [scores, setScores] = useState([]);
  const socketRef = useRef(null);

  const runEmotion = async () => {
    const response = await fetch('http://localhost:5000/run-python');
    const data = await response.text();
    setPythonOutput(data);
  };

  useEffect(() => {
    const socket = io('http://localhost:5000');
    socketRef.current = socket;

    socket.on('aiResponse', (data) => {
      setPythonOutput(data.transcript);
      setMessages((prev) => [
        ...prev,
        { text: data.transcript.trim() },
        ...data.aiReplies
          .filter((reply) => reply.trim() !== '')
          .map((reply) => ({
            text: reply.replace(/^\[.*?\]:\s*/, '').trim(),
          })),
      ]);
    });

    return () => socket.disconnect();
  }, []);

  const startLive = () => {
    setIsLive(true);
    socketRef.current?.emit('startLive', { status: 'started' });
  };
  
  const stopLive = () => {
    setIsLive(false);
    socketRef.current?.emit('stopLive', { status: 'stopped' });
  };

  const sidebarWidth = expanded ? 220 : 64;

  return (
    <Box
      sx={{
        marginLeft: `${sidebarWidth}px`,
        position: 'relative',
        width: `calc(100% - ${sidebarWidth}px)`,
        height: '100vh',
        overflow: 'hidden',
        backgroundColor: 'lightgray',
      }}
    >
      {/* 主播畫面區域 */}
      <Box sx={{ width: '100%', height: '100%' }}>
        <VideoSection
          socket={socketRef.current}
          isLive={isLive}
          pythonOutput={pythonOutput}
        />
      </Box>

      {/* 控制按鈕 - 上方置中 */}
      <Box
        sx={{
          position: 'absolute',
          top: '90%',
          left: '47%',
          transform: 'translateX(-50%)',
          zIndex: 10,
        }}
      >
        <LiveControlBar
          isLive={isLive}
          startLive={startLive}
          stopLive={stopLive}
          runEmotion={runEmotion}
        />
      </Box>

      {/* 人數變化圖 - 右上 */}
      <Box
        sx={{
          position: 'absolute',
          top: 16,
          right: 16,
          width: 320,
          height: '30%',
          bgcolor: 'transparent',
          borderRadius: 2,
          p: 2,
        }}
      >
        <ViewerTrendSection />
      </Box>

      {/* 聊天室 - 右下 */}
      <Box
        sx={{
          position: 'absolute',
          bottom: 16,
          right: 16,
          width: 320,
          height: 400,
          bgcolor: 'transparent',
          borderRadius: 2,
          overflowY: 'auto',
          p: 2,
        }}
      >
        <ChatSection messages={messages} scores={scores} />
      </Box>
    </Box>
  );
};

export default LivePageContainer;
