import React, { useEffect, useCallback } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  CircularProgress,
  useTheme,
  Alert,
  Snackbar,
  Button,
} from '@mui/material';
import { Refresh as RefreshIcon } from '@mui/icons-material';

// Components
import MonitoringPanel from './components/MonitoringPanel';
import ContextViewer from './components/ContextViewer';
import WorkflowManager from './components/WorkflowManager';
import QRDisplay from '../qr-display/QRDisplay';
import ErrorBoundary from './components/ErrorBoundary';
import MCPStatus from '../src/components/MCPStatus';

// Store and Providers
import { useStore } from '../src/store';
import { useMCP, MCPProvider } from '../src/contexts/MCPContext';

// Constants
const INITIAL_CAPABILITIES = {
  screenshots: true,
  clipboard: true,
  network: true,
} as const;

const DashboardContent: React.FC = () => {
  const theme = useTheme();
  const {
    context,
    isLoading,
    error,
    initializeApp,
    clearError,
    executeWorkflow,
    deleteWorkflow,
    refreshContext,
  } = useStore();

  const {
    isConnected,
    isInitialized,
    lastError: mcpError,
    capabilities,
    connect: mcpConnect,
  } = useMCP();

  // Initialize app on mount
  useEffect(() => {
    initializeApp();
    return () => {
      // Cleanup any subscriptions or resources
      clearError();
    };
  }, [initializeApp, clearError]);

  const handleRefreshContext = useCallback(async () => {
    try {
      await refreshContext();
    } catch (error) {
      console.error('Failed to refresh context:', error);
      throw error;
    }
  }, [refreshContext]);

  const handleDeleteWorkflow = useCallback(async (workflowId: string) => {
    try {
      await deleteWorkflow(workflowId);
    } catch (error) {
      console.error('Failed to delete workflow:', error);
      throw error;
    }
  }, [deleteWorkflow]);

  const handleRestartWorkflow = useCallback(async (workflowId: string) => {
    try {
      await executeWorkflow(workflowId, {
        restart: true,
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      console.error('Failed to restart workflow:', error);
      throw error;
    }
  }, [executeWorkflow]);

  const handleMCPReconnect = useCallback(async () => {
    try {
      await mcpConnect();
      await initializeApp();
    } catch (error) {
      console.error('Failed to reconnect:', error);
    }
  }, [mcpConnect, initializeApp]);

  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
        data-testid="loading-spinner"
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box 
      sx={{ flexGrow: 1, p: 3, backgroundColor: theme.palette.background.default }}
      data-testid="dashboard-content"
    >
      <ErrorBoundary>
        <Grid container spacing={3}>
          {/* Header */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="h4" component="h1">
                    System Context Monitor
                  </Typography>
                  <Button
                    startIcon={<RefreshIcon />}
                    onClick={handleRefreshContext}
                    disabled={!isConnected || isLoading}
                    data-testid="refresh-button"
                  >
                    Refresh
                  </Button>
                </Box>
                <MCPStatus />
                {!isConnected && (
                  <Alert
                    severity="warning"
                    action={
                      <Button
                        color="inherit"
                        size="small"
                        onClick={handleMCPReconnect}
                        disabled={isLoading}
                        data-testid="reconnect-button"
                      >
                        Reconnect
                      </Button>
                    }
                  >
                    Not connected to MCP server. Some features may be unavailable.
                  </Alert>
                )}
                {mcpError && (
                  <Alert severity="error" data-testid="mcp-error">
                    MCP Error: {mcpError.message}
                  </Alert>
                )}
              </Box>
            </Paper>
          </Grid>

          {/* Monitoring Panel */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 2, height: '400px', overflow: 'auto' }}>
              <ErrorBoundary>
                <MonitoringPanel
                  screenshots={context.screenshots}
                  clipboard={context.clipboard}
                  network={context.network}
                  isLoading={isLoading}
                  error={error}
                />
              </ErrorBoundary>
            </Paper>
          </Grid>

          {/* Context Viewer */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2, height: '400px', overflow: 'auto' }}>
              <ErrorBoundary>
                <ContextViewer
                  context={context}
                  onRefresh={handleRefreshContext}
                  isLoading={isLoading}
                  error={error}
                />
              </ErrorBoundary>
            </Paper>
          </Grid>

          {/* Workflow Manager */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 2, overflow: 'auto' }}>
              <ErrorBoundary>
                <WorkflowManager
                  workflows={context.workflows}
                  onDeleteWorkflow={handleDeleteWorkflow}
                  onRestartWorkflow={handleRestartWorkflow}
                  isLoading={isLoading}
                  error={error}
                />
              </ErrorBoundary>
            </Paper>
          </Grid>

          {/* QR Display */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2 }}>
              <ErrorBoundary>
                <QRDisplay
                  data={{
                    contextId: context.workflows[0]?.workflow_id,
                    timestamp: new Date().toISOString(),
                    activeWorkflows: context.workflows.length,
                  }}
                  onRefresh={handleRefreshContext}
                  isLoading={isLoading}
                  error={error}
                />
              </ErrorBoundary>
            </Paper>
          </Grid>
        </Grid>

        {/* Error Snackbar */}
        <Snackbar
          open={error !== null}
          autoHideDuration={6000}
          onClose={clearError}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          data-testid="error-snackbar"
        >
          <Alert onClose={clearError} severity="error" sx={{ width: '100%' }}>
            {error?.message || 'An error occurred'}
          </Alert>
        </Snackbar>
      </ErrorBoundary>
    </Box>
  );
};

const SystemContextDashboard: React.FC = () => {
  return (
    <MCPProvider initialCapabilities={INITIAL_CAPABILITIES}>
      <DashboardContent />
    </MCPProvider>
  );
};

export default SystemContextDashboard; 