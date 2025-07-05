// VideoComponent.js
import React, { useEffect, useRef, useState } from 'react';

function VideoComponent({socket, isLive}) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [hasCameraAccess, setHasCameraAccess] = useState(true);
  useEffect(() => {
    if(!isLive) return;
    let isMounted = true;
    if (socket&&isLive){
      const constraints = {
      video: {
        width: { ideal: 1920 },
        height: { ideal: 1080 }
      },
      audio: true
    };
    navigator.mediaDevices.getUserMedia(constraints)
      .then((stream) => {
        if (isMounted&&videoRef.current) {
          videoRef.current.srcObject = stream;
          streamRef.current = stream;
          setHasCameraAccess(true);
          socket?.emit('startLive', { status: 'started' });
        }
      })
      .catch((err) => {
        console.log("Error accessing media devices.", err);
        setHasCameraAccess(false);
      });
    }
    return () => {
      if(streamRef.current){
        streamRef.current.getTracks().forEach((track) => track.stop());
        socket?.emit('stopLive', { status: 'stopped' });
      }
      isMounted = false;
    }
  }, [socket, isLive]);

  return (
    <div
      style={{
        position: 'fixed',              // 固定在視窗
        top: 0,
        left: 0,
        width: '100vw',                 // 滿版寬
        height: '100vh',                // 滿版高
        border: 'none',
        backgroundColor: isLive ? 'black' : 'gray',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      {isLive ? (
        <video
          ref={videoRef}
          autoPlay
          muted
          playsInline
          style={{ width: '90%', height: '90%', objectFit: 'cover' }}
        />

      ) : (
        <span style={{ color: '#aaa', fontSize: '1.1rem' }}>尚未開始直播</span>
      )}
    </div>
  );
}

export default VideoComponent;
