import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect } from 'vitest';
import MCPStatus from '../MCPStatus';
import { MCPProvider } from '../../contexts/MCPContext';

// Mock useMCP hook
vi.mock('../../contexts/MCPContext', () => ({
  MCPProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  useMCP: vi.fn(),
}));

describe('MCPStatus', () => {
  const mockConnect = vi.fn();
  const defaultProps = {
    isConnected: false,
    isInitialized: false,
    lastError: null,
    capabilities: {},
    connect: mockConnect,
  };

  beforeEach(() => {
    vi.clearAllMocks();
    (vi.mocked(require('../../contexts/MCPContext').useMCP)).mockReturnValue(defaultProps);
  });

  it('should render disconnected state', () => {
    render(<MCPStatus />);
    
    expect(screen.getByText('Disconnected')).toBeInTheDocument();
    expect(screen.getByTestId('warning-icon')).toBeInTheDocument();
  });

  it('should render connecting state', () => {
    (vi.mocked(require('../../contexts/MCPContext').useMCP)).mockReturnValue({
      ...defaultProps,
      isConnected: true,
      isInitialized: false,
    });

    render(<MCPStatus />);
    
    expect(screen.getByText('Initializing...')).toBeInTheDocument();
    expect(screen.getByTestId('progress')).toBeInTheDocument();
  });

  it('should render connected state', () => {
    (vi.mocked(require('../../contexts/MCPContext').useMCP)).mockReturnValue({
      ...defaultProps,
      isConnected: true,
      isInitialized: true,
    });

    render(<MCPStatus />);
    
    expect(screen.getByText('Connected')).toBeInTheDocument();
    expect(screen.getByTestId('check-icon')).toBeInTheDocument();
  });

  it('should render error state', () => {
    const error = new Error('Connection failed');
    (vi.mocked(require('../../contexts/MCPContext').useMCP)).mockReturnValue({
      ...defaultProps,
      lastError: error,
    });

    render(<MCPStatus />);
    
    expect(screen.getByText('Connection Error')).toBeInTheDocument();
    expect(screen.getByText('Connection failed')).toBeInTheDocument();
    expect(screen.getByTestId('error-icon')).toBeInTheDocument();
  });

  it('should render capabilities', () => {
    (vi.mocked(require('../../contexts/MCPContext').useMCP)).mockReturnValue({
      ...defaultProps,
      isConnected: true,
      isInitialized: true,
      capabilities: {
        screenshots: true,
        clipboard: true,
      },
    });

    render(<MCPStatus />);
    
    expect(screen.getByText('screenshots')).toBeInTheDocument();
    expect(screen.getByText('clipboard')).toBeInTheDocument();
  });

  it('should handle reconnect click', () => {
    render(<MCPStatus />);
    
    fireEvent.click(screen.getByLabelText('Reconnect'));
    expect(mockConnect).toHaveBeenCalled();
  });

  it('should disable reconnect button when connected', () => {
    (vi.mocked(require('../../contexts/MCPContext').useMCP)).mockReturnValue({
      ...defaultProps,
      isConnected: true,
      isInitialized: true,
    });

    render(<MCPStatus />);
    
    expect(screen.getByLabelText('Reconnect')).toBeDisabled();
  });

  it('should enable reconnect button when error occurs', () => {
    (vi.mocked(require('../../contexts/MCPContext').useMCP)).mockReturnValue({
      ...defaultProps,
      isConnected: true,
      isInitialized: true,
      lastError: new Error('Connection failed'),
    });

    render(<MCPStatus />);
    
    expect(screen.getByLabelText('Reconnect')).not.toBeDisabled();
  });
}); 