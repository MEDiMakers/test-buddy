import Sidebar from '@/src/components/sidebar/Sidebar';
import ChatContainer from '@/src/components/chatContainer/chatContainer';

import Style from './Chat.module.css';

function Chat() {
  return (
    <div className={Style.container}>
      <div className={Style.sidebar}>
        <Sidebar />
      </div>
      <div className={Style.chat}>
        <ChatContainer />
      </div>
    </div>
  )
}

export default Chat;