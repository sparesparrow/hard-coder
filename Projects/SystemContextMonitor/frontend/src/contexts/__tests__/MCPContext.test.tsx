import React, { type ReactNode } from 'react';
import { render, screen, act, waitFor, renderHook } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { MCPProvider, useMCP } from '../MCPContext';
import { apiClient } from '../../api/client';

// Mock apiClient
vi.mock('../../api/client', () => ({
  apiClient: {
    connectWebSocket: vi.fn(),
    disconnectWebSocket: vi.fn(),
    executeWorkflow: vi.fn(),
  },
}));

// Test component that uses MCP context
const TestComponent = () => {
  const { isConnected, isInitialized, lastError, connect, disconnect } = useMCP();
  return (
    <div>
      <div data-testid="status">
        {isConnected ? 'Connected' : 'Disconnected'}
        {isInitialized ? ' and Initialized' : ''}
      </div>
      {lastError && <div data-testid="error">{lastError.message}</div>}
      <button onClick={connect}>Connect</button>
      <button onClick={disconnect}>Disconnect</button>
    </div>
  );
};

// Wrapper component with proper typing
const Wrapper = ({ children }: { children: ReactNode }) => (
  <MCPProvider>{children}</MCPProvider>
);

describe('MCPProvider', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should initialize with default state', () => {
    render(
      <MCPProvider>
        <TestComponent />
      </MCPProvider>
    );

    expect(screen.getByTestId('status')).toHaveTextContent('Disconnected');
    expect(screen.queryByTestId('error')).not.toBeInTheDocument();
  });

  it('should attempt to connect on mount', async () => {
    (apiClient.executeWorkflow as any).mockResolvedValueOnce({});

    render(
      <MCPProvider>
        <TestComponent />
      </MCPProvider>
    );

    await waitFor(() => {
      expect(apiClient.connectWebSocket).toHaveBeenCalled();
      expect(apiClient.executeWorkflow).toHaveBeenCalledWith('initialize', expect.any(Object));
    });
  });

  it('should handle successful connection', async () => {
    (apiClient.executeWorkflow as any).mockResolvedValueOnce({});

    render(
      <MCPProvider>
        <TestComponent />
      </MCPProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('status')).toHaveTextContent('Connected and Initialized');
    });
  });

  it('should handle connection failure', async () => {
    const error = new Error('Connection failed');
    (apiClient.executeWorkflow as any).mockRejectedValueOnce(error);

    render(
      <MCPProvider>
        <TestComponent />
      </MCPProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('error')).toHaveTextContent('Connection failed');
      expect(screen.getByTestId('status')).toHaveTextContent('Disconnected');
    });
  });

  it('should handle manual reconnection', async () => {
    (apiClient.executeWorkflow as any).mockResolvedValueOnce({});
    const user = userEvent.setup();

    render(
      <MCPProvider>
        <TestComponent />
      </MCPProvider>
    );

    // Simulate initial connection failure
    await waitFor(() => {
      expect(apiClient.connectWebSocket).toHaveBeenCalled();
    });

    // Clear mocks for reconnection attempt
    vi.clearAllMocks();
    (apiClient.executeWorkflow as any).mockResolvedValueOnce({});

    // Click connect button
    await user.click(screen.getByText('Connect'));

    await waitFor(() => {
      expect(apiClient.connectWebSocket).toHaveBeenCalled();
      expect(apiClient.executeWorkflow).toHaveBeenCalledWith('initialize', expect.any(Object));
      expect(screen.getByTestId('status')).toHaveTextContent('Connected and Initialized');
    });
  });

  it('should handle manual disconnection', async () => {
    (apiClient.executeWorkflow as any).mockResolvedValueOnce({});
    const user = userEvent.setup();

    render(
      <MCPProvider>
        <TestComponent />
      </MCPProvider>
    );

    // Wait for initial connection
    await waitFor(() => {
      expect(screen.getByTestId('status')).toHaveTextContent('Connected and Initialized');
    });

    // Click disconnect button
    await user.click(screen.getByText('Disconnect'));

    expect(apiClient.disconnectWebSocket).toHaveBeenCalled();
    expect(screen.getByTestId('status')).toHaveTextContent('Disconnected');
  });

  it('should handle notification sending', async () => {
    (apiClient.executeWorkflow as any).mockResolvedValueOnce({});
    
    const { result } = renderHook(() => useMCP(), {
      wrapper: Wrapper
    });

    // Wait for connection
    await waitFor(() => {
      expect(result.current.isConnected).toBe(true);
    });

    // Clear mocks for notification test
    vi.clearAllMocks();
    (apiClient.executeWorkflow as any).mockResolvedValueOnce({});

    // Send notification
    await act(async () => {
      await result.current.sendNotification('test', { data: 'test' });
    });

    expect(apiClient.executeWorkflow).toHaveBeenCalledWith('test', { data: 'test' });
  });

  it('should handle notification failure', async () => {
    (apiClient.executeWorkflow as any).mockResolvedValueOnce({});
    
    const { result } = renderHook(() => useMCP(), {
      wrapper: Wrapper
    });

    // Wait for connection
    await waitFor(() => {
      expect(result.current.isConnected).toBe(true);
    });

    // Clear mocks for notification test
    vi.clearAllMocks();
    const error = new Error('Notification failed');
    (apiClient.executeWorkflow as any).mockRejectedValueOnce(error);

    // Send notification
    await act(async () => {
      try {
        await result.current.sendNotification('test', { data: 'test' });
      } catch (e) {
        // Expected error
      }
    });

    expect(result.current.lastError).toBeTruthy();
    expect(result.current.lastError?.message).toBe('Failed to send notification');
  });
}); 