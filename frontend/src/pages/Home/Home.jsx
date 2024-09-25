import React from 'react';
import './Home.css';  
import AudioInputButton from '../../components/button/AudioInput/AudioInputButton';
import OutputBubble from '../../components/bubble/OutputBubble/OutputBubble';

function Home() {
  return (
    <div className="home-container">
      <OutputBubble text="Hello, this text is appearing one letter at a time!" side="left" delay={110} />
      <OutputBubble text="This is another message that shows up slowly." side="right" delay={50} />
    </div>
  );
}


export default Home;
