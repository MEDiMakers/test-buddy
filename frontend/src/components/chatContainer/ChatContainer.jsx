import Style from './ChatContainer.module.css';
import Header from '@/src/components/header/Header';


const ChatContainer = () => {
  return (
    <div className={Style.container}>
      <div className={Style.header}>
        <Header />
      </div>
      <div className={Style.body}>
        body
      </div>
      <div className={Style.audio}>
        audio
      </div>
    </div>
  )
}

export default ChatContainer