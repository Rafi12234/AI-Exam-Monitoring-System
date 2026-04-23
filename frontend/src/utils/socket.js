import { io } from 'socket.io-client';

export const socket = io('http://localhost:5000', {
  reconnection: true,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 5000,
  reconnectionAttempts: 5
});

socket.on('connect', () => {
  console.log('Connected to backend via Socket.IO');
});

socket.on('disconnect', () => {
  console.log('Disconnected from backend');
});

socket.on('connect_error', (error) => {
  console.error('Socket.IO connection error:', error);
});
