import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import SystemContextDashboard from '../SystemContextDashboard';

// Mock socket.io-client
jest.mock('socket.io-client', () => {
  const mockSocket = {
    on: jest.fn(),
    close: jest.fn(),
  };
  return {
    io: jest.fn(() => mockSocket),
  };
});

// Mock fetch API
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () =>
      Promise.resolve({
        screenshots: [],
        clipboard: [],
        network: [],
        workflows: [],
      }),
  })
) as jest.Mock;

describe('SystemContextDashboard', () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state initially', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SystemContextDashboard />
      </QueryClientProvider>
    );

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('renders dashboard after loading', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SystemContextDashboard />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('System Context Monitor')).toBeInTheDocument();
    });

    expect(screen.getByText('Context QR Code')).toBeInTheDocument();
  });

  it('handles fetch error', async () => {
    const errorMessage = 'Failed to fetch context';
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: false,
        statusText: errorMessage,
      })
    ) as jest.Mock;

    render(
      <QueryClientProvider client={queryClient}>
        <SystemContextDashboard />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(`Failed to fetch context: ${errorMessage}`)).toBeInTheDocument();
    });
  });
}); 