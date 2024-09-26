import React, { useState, useEffect } from 'react';
import OutputBubble from '../bubble/OutputBubble/OutputBubble';
import Style from './ChatContainer.module.css';
import Header from '@/src/components/header/Header';
import AudioInputBasic from '../button/AudioInput/AudioInputBasic';

const ChatContainer = ({ username }) => {
  const [leftBubbleText, setLeftBubbleText] = useState('');  // Left bubble text state (bot message)
  const [rightBubbleText, setRightBubbleText] = useState('');  // Right bubble text state (user message)
  const [loading, setLoading] = useState(true);

  // fetch data from the backend when the component is rendered
  useEffect(() => {
    const fetchData = async () => {
      try {
        //fetch chatbot prompt
        const responseNewChat = await fetch(`${import.meta.env.VITE_SERVER_URL}/chat/${username}/new`);
        const dataNewChat = await responseNewChat.json();

        if (dataNewChat.success) {
          setLeftBubbleText(dataNewChat.prompt);
        } else {
          console.error('Failed to create new chat:', dataNewChat.message);
        }

        // fetch user-related messages (not implemented rn)
        const responseFetchChat = await fetch(`${import.meta.env.VITE_SERVER_URL}/chat/fetch/all/${username}`);
        const dataFetchChat = await responseFetchChat.json();

        if (dataFetchChat.success && dataFetchChat.result.length > 0) {
          
          setRightBubbleText(dataFetchChat.result[0].prompt || 'No user message available');
        } else {
          console.error('Failed to fetch chat messages:', dataFetchChat.message);
        }

        setLoading(false); 
      } catch (error) {
        console.error('Error fetching chat data from backend:', error);
        setLoading(false);
      }
    };

    fetchData();
  }, [username]);

  //TODO: improve UI
  if (loading) {
    return <div>Loading ChatContainer.jsx...</div>;
  }

  return (
    <div className={Style.container}>
      <div className={Style.header}>
        <Header />
      </div>
      <div className={Style.body}>
        <OutputBubble text={leftBubbleText || "Error loading bot message"} side="left" delay={10} />
        <OutputBubble text={rightBubbleText || "Error loading user message"} side="right" delay={10} />
      </div>
      <div className={Style.audio}>
        <AudioInputBasic />
      </div>
    </div>
  );
};

export default ChatContainer;
