import { useCallback, useEffect, useRef, useState } from 'react';

interface WebSocketConfig {
  url: string;
  headers?: Record<string, string>;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

type ConnectionStatus = 'connecting' | 'connected' | 'disconnected';

interface UseWebSocketReturn {
  connect: () => void;
  disconnect: () => void;
  sendMessage: (message: any) => void;
  lastMessage: string | null;
  connectionStatus: ConnectionStatus;
  error: Error | null;
}

export const useWebSocket = ({
  url,
  headers = {},
  reconnectInterval = 5000,
  maxReconnectAttempts = 5
}: WebSocketConfig): UseWebSocketReturn => {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected');
  const [lastMessage, setLastMessage] = useState<string | null>(null);
  const [error, setError] = useState<Error | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isManualDisconnectRef = useRef(false);

  const cleanup = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const connect = useCallback(() => {
    cleanup();
    isManualDisconnectRef.current = false;
    setConnectionStatus('connecting');
    setError(null);

    try {
      // Create WebSocket connection
      const ws = new WebSocket(url);
      wsRef.current = ws;

      // Add headers to WebSocket connection
      if (headers && Object.keys(headers).length > 0) {
        const headerString = Object.entries(headers)
          .map(([key, value]) => `${key}: ${value}`)
          .join('\r\n');
        
        ws.addEventListener('open', () => {
          ws.send(headerString);
        });
      }

      // Connection opened
      ws.addEventListener('open', () => {
        setConnectionStatus('connected');
        reconnectAttemptsRef.current = 0;
      });

      // Listen for messages
      ws.addEventListener('message', (event) => {
        setLastMessage(event.data);
      });

      // Listen for errors
      ws.addEventListener('error', (event) => {
        const wsError = new Error('WebSocket error');
        setError(wsError);
        console.error('WebSocket error:', event);
      });

      // Connection closed
      ws.addEventListener('close', () => {
        setConnectionStatus('disconnected');
        wsRef.current = null;

        // Attempt to reconnect if not manually disconnected
        if (!isManualDisconnectRef.current && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++;
            connect();
          }, reconnectInterval);
        }
      });
    } catch (err) {
      setError(err as Error);
      setConnectionStatus('disconnected');
    }
  }, [url, headers, cleanup, maxReconnectAttempts, reconnectInterval]);

  const disconnect = useCallback(() => {
    isManualDisconnectRef.current = true;
    cleanup();
    setConnectionStatus('disconnected');
  }, [cleanup]);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      try {
        const messageString = typeof message === 'string' 
          ? message 
          : JSON.stringify(message);
        wsRef.current.send(messageString);
      } catch (err) {
        setError(err as Error);
        console.error('Error sending message:', err);
      }
    } else {
      setError(new Error('WebSocket is not connected'));
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      cleanup();
    };
  }, [cleanup]);

  return {
    connect,
    disconnect,
    sendMessage,
    lastMessage,
    connectionStatus,
    error
  };
};

export default useWebSocket; 