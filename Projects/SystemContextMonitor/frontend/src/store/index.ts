import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { SystemContext, WorkflowState, apiClient } from '../api/client';

interface AppState {
  // Context data
  context: SystemContext;
  isLoading: boolean;
  error: Error | null;
  
  // Actions
  initializeApp: () => Promise<void>;
  updateContext: (update: Partial<SystemContext>) => void;
  executeWorkflow: (workflowId: string, context: Record<string, any>) => Promise<string>;
  clearError: () => void;
}

const initialContext: SystemContext = {
  screenshots: [],
  clipboard: [],
  network: [],
  workflows: [],
};

export const useStore = create<AppState>()(
  devtools(
    (set, get) => ({
      // Initial state
      context: initialContext,
      isLoading: false,
      error: null,

      // Actions
      initializeApp: async () => {
        set({ isLoading: true, error: null });
        try {
          // Connect WebSocket
          apiClient.connectWebSocket();

          // Register context update handler
          apiClient.onContextUpdate((update) => {
            get().updateContext(update);
          });

          // Fetch initial context
          const context = await apiClient.getCurrentContext();
          set({ context, isLoading: false });
        } catch (error) {
          set({
            error: error instanceof Error ? error : new Error('Failed to initialize app'),
            isLoading: false,
          });
        }
      },

      updateContext: (update) => {
        set((state) => ({
          context: {
            ...state.context,
            ...update,
          },
        }));
      },

      executeWorkflow: async (workflowId: string, context: Record<string, any>) => {
        try {
          const result = await apiClient.executeWorkflow({
            workflow_id: workflowId,
            context,
          });
          return result.execution_id;
        } catch (error) {
          set({
            error: error instanceof Error ? error : new Error('Failed to execute workflow'),
          });
          throw error;
        }
      },

      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: 'app-store',
    }
  )
); 