import React, { useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  CircularProgress,
  useTheme,
  Alert,
  Snackbar,
} from '@mui/material';

// Components
import MonitoringPanel from './components/MonitoringPanel';
import ContextViewer from './components/ContextViewer';
import WorkflowManager from './components/WorkflowManager';
import QRDisplay from '../qr-display/QRDisplay';
import ErrorBoundary from './components/ErrorBoundary';
import MCPStatus from '../src/components/MCPStatus';

// Store and Providers
import { useStore } from '../src/store';
import { MCPProvider } from '../src/contexts/MCPContext';

const DashboardContent: React.FC = () => {
  const theme = useTheme();
  const { context, isLoading, error, initializeApp, clearError } = useStore();

  // Initialize app on mount
  useEffect(() => {
    initializeApp();
  }, [initializeApp]);

  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3, backgroundColor: theme.palette.background.default }}>
      <ErrorBoundary>
        <Grid container spacing={3}>
          {/* Header */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Typography variant="h4" component="h1">
                  System Context Monitor
                </Typography>
                <MCPStatus />
              </Box>
            </Paper>
          </Grid>

          {/* Monitoring Panel */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 2, height: '400px' }}>
              <ErrorBoundary>
                <MonitoringPanel
                  screenshots={context.screenshots}
                  clipboard={context.clipboard}
                  network={context.network}
                />
              </ErrorBoundary>
            </Paper>
          </Grid>

          {/* Context Viewer */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2, height: '400px' }}>
              <ErrorBoundary>
                <ContextViewer context={context} />
              </ErrorBoundary>
            </Paper>
          </Grid>

          {/* Workflow Manager */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 2 }}>
              <ErrorBoundary>
                <WorkflowManager workflows={context.workflows} />
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
    <MCPProvider
      initialCapabilities={{
        screenshots: true,
        clipboard: true,
        network: true,
      }}
    >
      <DashboardContent />
    </MCPProvider>
  );
};

export default SystemContextDashboard; 