import React, { useEffect, useState } from 'react';
import Chat from './pages/Chat/Chat';
import './styles/global.css';

function App() {
  const [username, setUsername] = useState('testuser');
  const [userCreated, setUserCreated] = useState(false);

  // create the test user when the app loads
  // TODO: improve duplicate user logic
  // TODO: abstract to a custom react hook
  useEffect(() => {
    const createTestUser = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_SERVER_URL}/user/create/${username}`, {
          method: 'GET',
        });

        const data = await response.json();

        if (response.status === 201) {
          console.log(`User ${username} created successfully`);
          setUserCreated(true);
        } else if (response.status === 409) {
          console.log('User already exists');
          setUserCreated(true); //proceed since user already exists
        } else {
          console.error('Error creating user:', data.message);
        }
      } catch (error) {
        console.error('Error creating user:', error);
      }
    };

    createTestUser();
  }, [username]); 

  //TODO: pass the username as a useContext
  return (
    <div>
      {userCreated ? <Chat username={username} /> : <p>Loading...</p>}
    </div>
  );
}

export default App;

