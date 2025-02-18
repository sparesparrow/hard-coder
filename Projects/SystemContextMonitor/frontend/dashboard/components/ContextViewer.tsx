import React from 'react';
import {
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  Divider,
  Chip,
} from '@mui/material';

interface SystemContext {
  screenshots: ScreenshotData[];
  clipboard: ClipboardData[];
  network: NetworkData[];
  workflows: WorkflowState[];
}

interface ScreenshotData {
  timestamp: string;
  image_data: string;
  dimensions: [number, number];
}

interface ClipboardData {
  timestamp: string;
  content: string;
}

interface NetworkData {
  timestamp: string;
  type: string;
  data: any;
}

interface WorkflowState {
  workflow_id: string;
  status: string;
  start_time: string;
  end_time?: string;
  results?: any;
  error?: string;
}

interface ContextViewerProps {
  context: SystemContext;
}

const ContextViewer: React.FC<ContextViewerProps> = ({ context }) => {
  const getStatusColor = (status: string) => {
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
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        System Context Overview
      </Typography>

      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="subtitle1" gutterBottom>
          Active Monitoring
        </Typography>
        <List dense>
          <ListItem>
            <ListItemText
              primary="Screenshots"
              secondary={`${context.screenshots.length} captures`}
            />
          </ListItem>
          <ListItem>
            <ListItemText
              primary="Clipboard Events"
              secondary={`${context.clipboard.length} entries`}
            />
          </ListItem>
          <ListItem>
            <ListItemText
              primary="Network Activity"
              secondary={`${context.network.length} events`}
            />
          </ListItem>
        </List>
      </Paper>

      <Paper sx={{ p: 2 }}>
        <Typography variant="subtitle1" gutterBottom>
          Active Workflows
        </Typography>
        <List dense>
          {context.workflows.map((workflow, index) => (
            <React.Fragment key={workflow.workflow_id}>
              {index > 0 && <Divider />}
              <ListItem>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {workflow.workflow_id}
                      <Chip
                        label={workflow.status}
                        size="small"
                        color={getStatusColor(workflow.status) as any}
                      />
                    </Box>
                  }
                  secondary={
                    <>
                      <Typography variant="body2" component="span">
                        Started: {new Date(workflow.start_time).toLocaleString()}
                      </Typography>
                      {workflow.end_time && (
                        <Typography variant="body2" component="div">
                          Ended: {new Date(workflow.end_time).toLocaleString()}
                        </Typography>
                      )}
                      {workflow.error && (
                        <Typography
                          variant="body2"
                          component="div"
                          color="error"
                        >
                          Error: {workflow.error}
                        </Typography>
                      )}
                    </>
                  }
                />
              </ListItem>
            </React.Fragment>
          ))}
        </List>
      </Paper>
    </Box>
  );
};

export default ContextViewer; 