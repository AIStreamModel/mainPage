// ChatComponent.js
import React, {useEffect, useRef} from 'react';

function ChatComponent({ messages }) {
  const bottomRef = useRef(null);

  // 每次 messages 改變，就捲到底部
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div style={{ maxHeight: '365px', overflowY: 'auto', padding: '10px' }}>
      {messages.map((msg, idx) => (
        <div key={idx} style={{
          backgroundColor: msg.text.startsWith('🗣️') ? '#00ffff' : '#33ffff',
          padding: '6px 12px',
          borderRadius: '8px',
          marginBottom: '6px',
          fontFamily:'Noto Sans TC'
        }}>
          {msg.text}
        </div>
      ))}
      <div ref={bottomRef}/>
    </div>
  );
}

export default ChatComponent;
