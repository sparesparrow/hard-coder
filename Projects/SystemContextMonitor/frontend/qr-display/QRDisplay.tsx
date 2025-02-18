import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper } from '@mui/material';
import QRCode from 'qrcode.react';

interface QRDisplayData {
  contextId: string | undefined;
  timestamp: string;
  activeWorkflows: number;
}

interface QRDisplayProps {
  data: QRDisplayData;
}

const QRDisplay: React.FC<QRDisplayProps> = ({ data }) => {
  const [qrValue, setQrValue] = useState<string>('');

  useEffect(() => {
    // Create a JSON string of the data for the QR code
    const qrData = JSON.stringify({
      ...data,
      type: 'system-context',
      version: '1.0',
    });
    setQrValue(qrData);
  }, [data]);

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Context QR Code
      </Typography>
      <Paper
        sx={{
          p: 2,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        {data.contextId ? (
          <>
            <QRCode
              value={qrValue}
              size={200}
              level="H"
              includeMargin={true}
              renderAs="svg"
            />
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              Scan to access context
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Last updated: {new Date(data.timestamp).toLocaleString()}
            </Typography>
          </>
        ) : (
          <Typography variant="body1" color="text.secondary">
            Waiting for context connection...
          </Typography>
        )}
      </Paper>
    </Box>
  );
};

export default QRDisplay; 