import React from 'react';
import './Home.css';  
import AudioInputButton from '../../components/button/AudioInput/AudioInputButton';
import TextBubble from '../../components/bubble/OutputBubble/TextBubble';

function Home() {
  return (
    <div className="home-container">
      <TextBubble text="Hello, this text is appearing one letter at a time!" side="left" delay={110} />
      <TextBubble text="This is another message that shows up slowly." side="right" delay={50} />
    </div>
  );
}


export default Home;
