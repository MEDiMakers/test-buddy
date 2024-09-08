import React, { useState, useEffect } from 'react';
import './TextBubble.css';

const TextBubble = ({ text, side, delay = 50 }) => {
  const [displayedText, setDisplayedText] = useState('');

  useEffect(() => {
    setDisplayedText(''); // Reset displayed text when the text prop changes
    let index = 0;

    const intervalId = setInterval(() => {
      if (index < text.length) {
        setDisplayedText((prev) => prev + text.charAt(index));
        index++;
      } else {
        clearInterval(intervalId);
      }
    }, delay);

    return () => clearInterval(intervalId); // Cleanup on unmount or when text changes
  }, [text, delay]);

  return (
    <div className={`speech-bubble ${side}`}>
      <div className={`speech-bubble-tip ${side}`} />
      <p>{displayedText}</p>
    </div>
  );
};

export default TextBubble;
