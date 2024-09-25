import React, { useState, useEffect, useCallback, useRef } from 'react';
import './OutputBubble.css';

const OutputBubble = ({ text, side, delay = 50 }) => {
  const [displayedText, setDisplayedText] = useState('');
  const timeoutRef = useRef(null);

  const animateText = useCallback(() => {
    let currentIndex = 0;
    const textLength = text.length;

    const updateText = () => {
      if (currentIndex < textLength) {
        setDisplayedText(text.slice(0, currentIndex + 1));
        currentIndex++;

        // Calculate dynamic delay based on remaining characters
        const remainingChars = textLength - currentIndex;
        const dynamicDelay = Math.max(10, Math.min(delay, 200 / remainingChars));

        timeoutRef.current = setTimeout(updateText, dynamicDelay);
      }
    };

    updateText();

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [text, delay]);

  useEffect(() => {
    setDisplayedText('');
    const cleanup = animateText();
    return cleanup;
  }, [animateText, text]);

  return (
    <div className={`output-bubble ${side}`}>
      <div className={`output-bubble-tip ${side}`} />
      <p>{displayedText}</p>
    </div>
  );
};

export default OutputBubble;