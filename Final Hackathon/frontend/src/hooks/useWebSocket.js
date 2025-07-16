import { useEffect, useState, useRef } from 'react';
import { io } from 'socket.io-client';

export const useWebSocket = (url, onMessage) => {
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const isConnecting = useRef(false);

  useEffect(() => {
    // Prevent multiple connections
    if (isConnecting.current || socketRef.current?.connected) {
      return;
    }

    isConnecting.current = true;

    // Create socket connection with improved configuration
    socketRef.current = io(url, {
      transports: ['websocket', 'polling'],
      timeout: 10000,
      reconnectionAttempts: 3, // Reduced from 5 to 3
      reconnectionDelay: 4000, // Increased delay
      reconnectionDelayMax: 15000, // Increased max delay
      autoConnect: true,
      forceNew: false
    });

    const socket = socketRef.current;

    // Connection event handlers
    socket.on('connect', () => {
      console.log('✅ WebSocket connected to', url);
      setIsConnected(true);
      isConnecting.current = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
    });

    socket.on('disconnect', (reason) => {
      console.log('❌ WebSocket disconnected:', reason);
      setIsConnected(false);
      isConnecting.current = false;
      if (reason === 'io server disconnect' || reason === 'transport close') {
        console.log('🔄 Attempting to reconnect...');
        reconnectTimeoutRef.current = setTimeout(() => {
          if (!socket.connected && !isConnecting.current) {
            socket.connect();
          }
        }, 4000);
      }
    });

    socket.on('connect_error', (error) => {
      console.error('❌ WebSocket connection error:', error.message);
      setIsConnected(false);
      isConnecting.current = false;
    });

    socket.on('reconnect', (attemptNumber) => {
      console.log(`🔄 Reconnected after ${attemptNumber} attempts`);
      setIsConnected(true);
    });

    socket.on('reconnect_error', (error) => {
      console.error('❌ Reconnection failed:', error.message);
    });

    socket.on('reconnect_failed', () => {
      console.error('❌ All reconnection attempts failed');
      setIsConnected(false);
    });

    // Dashboard update handler
    socket.on('dashboard-update', (data) => {
      console.log('📊 Dashboard update received');
      if (onMessage && typeof onMessage === 'function') {
        onMessage(data);
      }
    });

    // Cleanup function
    return () => {
      console.log('🧹 Cleaning up WebSocket connection');
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      socket.removeAllListeners();
      if (socket.connected) {
        socket.disconnect();
      }
      socketRef.current = null;
      isConnecting.current = false;
      setIsConnected(false);
    };
  }, [url]); // Only depend on URL, not onMessage to prevent recreation

  // Handle onMessage changes without recreating the connection
  useEffect(() => {
    if (socketRef.current) {
      socketRef.current.off('dashboard-update');
      socketRef.current.on('dashboard-update', (data) => {
        console.log('📊 Dashboard update received');
        if (onMessage && typeof onMessage === 'function') {
          onMessage(data);
        }
      });
    }
  }, [onMessage]);

  const sendMessage = (event, data) => {
    if (socketRef.current && socketRef.current.connected) {
      socketRef.current.emit(event, data);
      return true;
    } else {
      console.warn('⚠️ Cannot send message: WebSocket not connected');
      return false;
    }
  };

  const forceReconnect = () => {
    if (socketRef.current && !isConnecting.current) {
      console.log('🔄 Force reconnecting...');
      socketRef.current.disconnect();
      setTimeout(() => {
        if (socketRef.current && !socketRef.current.connected) {
          socketRef.current.connect();
        }
      }, 1000);
    }
  };

  return {
    isConnected,
    sendMessage,
    forceReconnect
  };
};