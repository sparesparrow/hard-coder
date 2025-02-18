import React from 'react';
import {
  Box,
  Chip,
  Typography,
  IconButton,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Check as CheckIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { useMCP } from '../contexts/MCPContext';

interface MCPStatusProps {
  className?: string;
}

const MCPStatus: React.FC<MCPStatusProps> = ({ className }) => {
  const {
    isConnected,
    isInitialized,
    lastError,
    capabilities,
    connect,
  } = useMCP();

  const getStatusIcon = () => {
    if (lastError) return <ErrorIcon data-testid="error-icon" color="error" />;
    if (!isConnected) return <WarningIcon data-testid="warning-icon" color="warning" />;
    if (isInitialized) return <CheckIcon data-testid="check-icon" color="success" />;
    return <CircularProgress data-testid="progress" size={20} />;
  };

  const getStatusText = () => {
    if (lastError) return 'Connection Error';
    if (!isConnected) return 'Disconnected';
    if (isInitialized) return 'Connected';
    return 'Initializing...';
  };

  return (
    <Box
      className={className}
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 2,
        p: 1,
        borderRadius: 1,
        bgcolor: 'background.paper',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        {getStatusIcon()}
        <Typography variant="body2">{getStatusText()}</Typography>
      </Box>

      {isInitialized && (
        <Box sx={{ display: 'flex', gap: 1 }}>
          {Object.entries(capabilities).map(([key, value]) => (
            <Tooltip
              key={key}
              title={`${key}: ${JSON.stringify(value)}`}
              arrow
            >
              <Chip
                label={key}
                size="small"
                color="primary"
                variant="outlined"
              />
            </Tooltip>
          ))}
        </Box>
      )}

      <Tooltip title="Reconnect">
        <span>
          <IconButton
            size="small"
            onClick={() => connect()}
            disabled={isInitialized && !lastError}
            aria-label="Reconnect"
          >
            <RefreshIcon />
          </IconButton>
        </span>
      </Tooltip>

      {lastError && (
        <Typography
          variant="caption"
          color="error"
          sx={{ ml: 'auto' }}
        >
          {lastError.message}
        </Typography>
      )}
    </Box>
  );
};

export default MCPStatus; 