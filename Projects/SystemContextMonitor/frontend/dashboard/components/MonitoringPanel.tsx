import React from 'react';
import {
  Box,
  Tabs,
  Tab,
  Typography,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
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

interface MonitoringPanelProps {
  screenshots: ScreenshotData[];
  clipboard: ClipboardData[];
  network: NetworkData[];
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`monitoring-tabpanel-${index}`}
      aria-labelledby={`monitoring-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const MonitoringPanel: React.FC<MonitoringPanelProps> = ({
  screenshots,
  clipboard,
  network,
}) => {
  const [value, setValue] = React.useState(0);

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={value} onChange={handleChange} aria-label="monitoring tabs">
          <Tab label="Screenshots" />
          <Tab label="Clipboard" />
          <Tab label="Network" />
        </Tabs>
      </Box>

      {/* Screenshots Panel */}
      <TabPanel value={value} index={0}>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
          {screenshots.map((screenshot, index) => (
            <Card key={index} sx={{ maxWidth: 345 }}>
              <img
                src={`data:image/jpeg;base64,${screenshot.image_data}`}
                alt={`Screenshot ${index}`}
                style={{ width: '100%', height: 'auto' }}
              />
              <CardContent>
                <Typography variant="body2" color="text.secondary">
                  Captured: {new Date(screenshot.timestamp).toLocaleString()}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Dimensions: {screenshot.dimensions[0]}x{screenshot.dimensions[1]}
                </Typography>
              </CardContent>
            </Card>
          ))}
        </Box>
      </TabPanel>

      {/* Clipboard Panel */}
      <TabPanel value={value} index={1}>
        <List>
          {clipboard.map((item, index) => (
            <ListItem key={index}>
              <ListItemText
                primary={item.content}
                secondary={new Date(item.timestamp).toLocaleString()}
              />
            </ListItem>
          ))}
        </List>
      </TabPanel>

      {/* Network Panel */}
      <TabPanel value={value} index={2}>
        <List>
          {network.map((item, index) => (
            <ListItem key={index}>
              <ListItemText
                primary={item.type}
                secondary={
                  <>
                    <Typography component="span" variant="body2">
                      {new Date(item.timestamp).toLocaleString()}
                    </Typography>
                    <pre style={{ marginTop: 8 }}>
                      {JSON.stringify(item.data, null, 2)}
                    </pre>
                  </>
                }
              />
            </ListItem>
          ))}
        </List>
      </TabPanel>
    </Box>
  );
};

export default MonitoringPanel; 