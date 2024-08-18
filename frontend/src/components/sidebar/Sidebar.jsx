import Style from './SideBar.module.css';
import { RiMenuUnfold3Line2, RiMenuUnfold4Line2 } from 'react-icons/ri';
import { useState } from 'react';

const Sidebar = () => {
  
  const [isHidden, setIsHidden] = useState(false);
  const chatArray = [
    {
      name: 'user1',
      message: 'message1',
    },
    {
      name: 'user2',
      message: 'message2',
    },
    {
      name: 'user3',
      message: 'message3',
    },
    {
      name: 'user4',
      message: 'message4',
    },
    {
      name: 'user5',
      message: 'message5',
    },
  ];

  const toggleSidebar = () => {
    setIsHidden(!isHidden);
  };

  return (
    <div className={`${Style.sidebar} ${isHidden ? Style.sidebarHidden : ''}`}>
      <button className={Style.toggleButton} onClick={toggleSidebar}>
        {isHidden ? <RiMenuUnfold3Line2 /> : <RiMenuUnfold4Line2 />}
      </button>
      
      {!isHidden && 
        <div className={Style.chats}>
          {chatArray.map((chat, i) => (
            <div 
              key={i}  
              className={Style.chatBox}
            >
              <span>{chat.name}</span>
              <p>{chat.message}</p>
            </div>
          ))}
        </div>
      }
    </div>
  )
}

export default Sidebar;