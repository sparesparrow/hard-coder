import axios, { AxiosInstance } from 'axios';
import { io, Socket } from 'socket.io-client';

// Types
export interface SystemContext {
  screenshots: ScreenshotData[];
  clipboard: ClipboardData[];
  network: NetworkData[];
  workflows: WorkflowState[];
}

export interface ScreenshotData {
  timestamp: string;
  image_data: string;
  dimensions: [number, number];
}

export interface ClipboardData {
  timestamp: string;
  content: string;
}

export interface NetworkData {
  timestamp: string;
  type: 'request' | 'response' | 'error';
  data: {
    method?: string;
    url?: string;
    status?: number;
    headers?: Record<string, string>;
    body?: Record<string, unknown>;
    error?: {
      message: string;
      code?: string;
    };
  };
}

export interface WorkflowState {
  workflow_id: string;
  status: string;
  start_time: string;
  end_time?: string;
  results?: any;
  error?: string;
}

export interface WorkflowExecution {
  workflow_id: string;
  context: Record<string, any>;
}

export interface WorkflowList {
  available_workflows: string[];
  active_workflows: WorkflowState[];
}

class APIClient {
  private readonly api: AxiosInstance;
  private socket: Socket | null = null;
  private contextUpdateHandlers: Array<(context: Partial<SystemContext>) => void> = [];

  constructor(baseURL: string = 'http://localhost:8000') {
    // Initialize axios instance
    this.api = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error);
        return Promise.reject(error);
      }
    );
  }

  // Socket.IO connection management
  public connectWebSocket(): void {
    if (this.socket) {
      return;
    }

    this.socket = io('http://localhost:8000', {
      path: '/ws/socket.io',
      transports: ['websocket'],
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    this.socket.on('connect', () => {
      console.log('Connected to WebSocket server');
    });

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
    });

    this.socket.on('context_update', (data: Partial<SystemContext>) => {
      this.contextUpdateHandlers.forEach((handler) => {
        try {
          handler(data);
        } catch (error) {
          console.error('Error in context update handler:', error);
        }
      });
    });
  }

  public disconnectWebSocket(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  public onContextUpdate(handler: (context: Partial<SystemContext>) => void): () => void {
    this.contextUpdateHandlers.push(handler);
    return () => {
      this.contextUpdateHandlers = this.contextUpdateHandlers.filter((h) => h !== handler);
    };
  }

  // REST API methods
  public async getCurrentContext(): Promise<SystemContext> {
    const response = await this.api.get<SystemContext>('/api/context');
    return response.data;
  }

  public async executeWorkflow(execution: WorkflowExecution): Promise<{ execution_id: string; status: string }> {
    const response = await this.api.post('/api/workflows/execute', execution);
    return response.data;
  }

  public async getWorkflowStatus(executionId: string): Promise<WorkflowState> {
    const response = await this.api.get(`/api/workflows/${executionId}/status`);
    return response.data;
  }

  public async listWorkflows(): Promise<WorkflowList> {
    const response = await this.api.get('/api/workflows');
    return response.data;
  }
}

// Create and export singleton instance
export const apiClient = new APIClient();
export default apiClient; 