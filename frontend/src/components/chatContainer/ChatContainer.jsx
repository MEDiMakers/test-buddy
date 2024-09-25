import React, { useState, useEffect } from 'react';
import OutputBubble from '../bubble/OutputBubble/OutputBubble';
import Style from './ChatContainer.module.css';
import Header from '@/src/components/header/Header';
import AudioInputButton from "../button/AudioInput/AudioInputButton";
import AudioInputBasic from '../button/AudioInput/AudioInputBasic';

const ChatContainer = () => {

  const [leftBubbleText, setLeftBubbleText] = useState('');  // Left bubble text state
  const [rightBubbleText, setRightBubbleText] = useState('');  // Right bubble text state
  const [loading, setLoading] = useState(true);  

  // fetch data from backend when the component is rendered
  useEffect(() => {
  const fetchData = async () => {
    try {
      // fetch bot message
      const responseLeft = await fetch(`${import.meta.env.VITE_SERVER_URL}/api/get-text`);
      const dataLeft = await responseLeft.json();
      setLeftBubbleText(dataLeft.text); 

      // fetch user bubble message
      const responseRight = await fetch(`${import.meta.env.VITE_SERVER_URL}/api/get-text`);
      const dataRight = await responseRight.json();
      setRightBubbleText(dataRight.text); // Set right bubble text

      setLoading(false); 
    } catch (error) {
      console.error('Error fetching text from backend:', error);
      setLoading(false);
    }
  };

  fetchData();
  }, []);

  return (
    <div className={Style.container}>
      <div className={Style.header}>
        <Header />
      </div>
      <div className={Style.body}>
      <OutputBubble text={leftBubbleText || "Error loading text"} side="left" delay={10} />
      <OutputBubble text={rightBubbleText || "Error loading text"} side="right" delay={10} />
      </div>
      <div className={Style.audio}>
          <AudioInputBasic></AudioInputBasic>
      </div>
    </div>
  )
}

export default ChatContainer