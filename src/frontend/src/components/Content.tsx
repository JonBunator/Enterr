import { useEffect } from 'react'
import axios from 'axios'
import { useWebSocket } from './WebSocketProvider';

export default function Content() {
    const { emit, on } = useWebSocket();
    
  const fetchAPI = async () => {
    const response = await axios.get("/api/users");
    console.log(response.data.users);
  }

  useEffect(() => {
    fetchAPI();
  }, []);

  function handleClick() {
    emit('custom_event', { message: 'Hello from React!' });
  }

  useEffect(() => {
    on('message', (data) => {
      console.log(data);
    });
    emit('custom_event', { message: 'Hello from React!' });
  }, [on, emit]);

  return (
        <button onClick={handleClick}>
          Send message
        </button>
  )
}