import React, { createContext, useContext, useCallback, useEffect, useState } from 'react';
import { apiClient, SystemContext } from '../api/client';

interface MCPContextType {
  isConnected: boolean;
  isInitialized: boolean;
  lastError: Error | null;
  capabilities: Record<string, any>;
  connect: () => Promise<void>;
  disconnect: () => void;
  sendNotification: (method: string, params: Record<string, any>) => Promise<void>;
  clearError: () => void;
}

const MCPContext = createContext<MCPContextType | null>(null);

interface MCPProviderProps {
  children: React.ReactNode;
  initialCapabilities?: Record<string, any>;
}

export const MCPProvider: React.FC<MCPProviderProps> = ({
  children,
  initialCapabilities = {}
}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);
  const [lastError, setLastError] = useState<Error | null>(null);
  const [capabilities, setCapabilities] = useState(initialCapabilities);

  const connect = useCallback(async () => {
    try {
      setLastError(null);
      apiClient.connectWebSocket();
      
      // Send initialization message
      await apiClient.executeWorkflow('initialize', {
        capabilities,
        client_info: {
          type: 'web',
          version: '1.0.0',
          features: ['screenshots', 'clipboard', 'network']
        }
      });
      
      setIsConnected(true);
      setIsInitialized(true);
    } catch (error) {
      setLastError(error instanceof Error ? error : new Error('Connection failed'));
      setIsConnected(false);
    }
  }, [capabilities]);

  const disconnect = useCallback(() => {
    apiClient.disconnectWebSocket();
    setIsConnected(false);
    setIsInitialized(false);
  }, []);

  const sendNotification = useCallback(async (method: string, params: Record<string, any>) => {
    if (!isConnected) {
      throw new Error('Not connected to MCP server');
    }
    
    try {
      await apiClient.executeWorkflow(method, params);
    } catch (error) {
      setLastError(error instanceof Error ? error : new Error('Failed to send notification'));
      throw error;
    }
  }, [isConnected]);

  const clearError = useCallback(() => {
    setLastError(null);
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  const value: MCPContextType = {
    isConnected,
    isInitialized,
    lastError,
    capabilities,
    connect,
    disconnect,
    sendNotification,
    clearError
  };

  return (
    <MCPContext.Provider value={value}>
      {children}
    </MCPContext.Provider>
  );
};

export const useMCP = () => {
  const context = useContext(MCPContext);
  if (!context) {
    throw new Error('useMCP must be used within an MCPProvider');
  }
  return context;
};

export default MCPProvider; 