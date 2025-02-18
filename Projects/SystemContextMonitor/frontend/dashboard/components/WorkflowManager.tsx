import React, { useState, useCallback, useMemo } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Tooltip,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

interface WorkflowState {
  workflow_id: string;
  status: string;
  start_time: string;
  end_time?: string;
  results?: any;
  error?: string;
}

interface WorkflowManagerProps {
  workflows: WorkflowState[];
}

const WorkflowManager: React.FC<WorkflowManagerProps> = React.memo(({ workflows }) => {
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowState | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);

  const handleOpenDetails = useCallback((workflow: WorkflowState) => {
    setSelectedWorkflow(workflow);
    setDetailsOpen(true);
  }, []);

  const handleCloseDetails = useCallback(() => {
    setDetailsOpen(false);
    setSelectedWorkflow(null);
  }, []);

  const getStatusColor = useCallback((status: string) => {
    switch (status.toLowerCase()) {
      case 'running':
        return 'primary';
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  }, []);

  const getStatusIcon = useCallback((status: string) => {
    switch (status.toLowerCase()) {
      case 'running':
        return <PlayIcon />;
      case 'completed':
        return <RefreshIcon />;
      case 'failed':
        return <StopIcon />;
      default:
        return null;
    }
  }, []);

  const sortedWorkflows = useMemo(() => {
    return [...workflows].sort((a, b) => 
      new Date(b.start_time).getTime() - new Date(a.start_time).getTime()
    );
  }, [workflows]);

  const renderWorkflowDetails = useCallback(() => {
    if (!selectedWorkflow) return null;
    
    return (
      <Box>
        <Typography variant="subtitle1" gutterBottom>
          Workflow ID: {selectedWorkflow.workflow_id}
        </Typography>
        <Typography variant="body1" gutterBottom>
          Status:{' '}
          <Chip
            label={selectedWorkflow.status}
            color={getStatusColor(selectedWorkflow.status) as any}
            size="small"
          />
        </Typography>
        <Typography variant="body1" gutterBottom>
          Start Time: {new Date(selectedWorkflow.start_time).toLocaleString()}
        </Typography>
        {selectedWorkflow.end_time && (
          <Typography variant="body1" gutterBottom>
            End Time: {new Date(selectedWorkflow.end_time).toLocaleString()}
          </Typography>
        )}
        {selectedWorkflow.error && (
          <Typography variant="body1" color="error" gutterBottom>
            Error: {selectedWorkflow.error}
          </Typography>
        )}
        {selectedWorkflow.results && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Results:
            </Typography>
            <Paper sx={{ p: 2, backgroundColor: '#f5f5f5' }}>
              <pre>{JSON.stringify(selectedWorkflow.results, null, 2)}</pre>
            </Paper>
          </Box>
        )}
      </Box>
    );
  }, [selectedWorkflow, getStatusColor]);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">Workflow Management</Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<PlayIcon />}
          onClick={() => {
            // TODO: Implement workflow creation
            console.log('Create new workflow');
          }}
        >
          New Workflow
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Start Time</TableCell>
              <TableCell>End Time</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sortedWorkflows.map((workflow) => (
              <TableRow key={workflow.workflow_id}>
                <TableCell>{workflow.workflow_id}</TableCell>
                <TableCell>
                  <Chip
                    icon={getStatusIcon(workflow.status)}
                    label={workflow.status}
                    color={getStatusColor(workflow.status) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {new Date(workflow.start_time).toLocaleString()}
                </TableCell>
                <TableCell>
                  {workflow.end_time
                    ? new Date(workflow.end_time).toLocaleString()
                    : '-'}
                </TableCell>
                <TableCell>
                  <Tooltip title="View Details">
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDetails(workflow)}
                    >
                      <InfoIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={detailsOpen} onClose={handleCloseDetails} maxWidth="md">
        <DialogTitle>Workflow Details</DialogTitle>
        <DialogContent>
          {renderWorkflowDetails()}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDetails}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
});

WorkflowManager.displayName = 'WorkflowManager';

export default WorkflowManager; 