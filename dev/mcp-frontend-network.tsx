import React, { useState } from 'react';
import { 
  Card, 
  CardHeader, 
  CardTitle, 
  CardContent,
  CardDescription
} from '@/components/ui/card';
import { 
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle
} from '@/components/ui/alert-dialog';
import { 
  Tabs, 
  TabsContent, 
  TabsList, 
  TabsTrigger 
} from '@/components/ui/tabs';

// Icons as a constant outside the component
const ICONS = {
  ADD: '➕',
  SETTINGS: '⚙️',
  PLAY: '▶️',
  REMOVE: '❌',
  COPY: '📋',
  COPIED: '✅',
  TOOL: '🔧',
  MESSAGE: '💬',
  SAVE: '💾',
  SCAN: '🔍',
  NETWORK: '🌐',
  CONNECTED: '🟢',
  DISCONNECTED: '🔴'
};

const MCPManager = () => {
  // Network discovery state
  const [isScanning, setIsScanning] = useState(false);
  const [discoveredServers, setDiscoveredServers] = useState([]);
  
  // Server management state
  const [servers, setServers] = useState([]);
  const [activeServer, setActiveServer] = useState(null);
  const [showAddDialog, setShowAddDialog] = useState(false);
  
  // Input/Output state
  const [inputs, setInputs] = useState([{ id: 1, value: '' }]);
  const [outputs, setOutputs] = useState([]);
  const [copiedItems, setCopiedItems] = useState({});

  // Tool and prompt state
  const [selectedTool, setSelectedTool] = useState(null);
  const [toolParams, setToolParams] = useState({});

  const scanNetwork = async () => {
    setIsScanning(true);
    try {
      // Simulate network scan
      await new Promise(resolve => setTimeout(resolve, 1500));
      const mockServers = [
        { id: 'net1', name: 'Database MCP', address: '192.168.1.100', port: 8080 },
        { id: 'net2', name: 'File Server MCP', address: '192.168.1.101', port: 8080 }
      ];
      setDiscoveredServers(mockServers);
    } finally {
      setIsScanning(false);
    }
  };

  const addServer = (server) => {
    setServers([...servers, server]);
    setShowAddDialog(false);
  };

  const copyToClipboard = async (text, id) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedItems(prev => ({ ...prev, [id]: true }));
      setTimeout(() => {
        setCopiedItems(prev => ({ ...prev, [id]: false }));
      }, 2000);
    } catch (error) {
      console.error('Copy failed:', error);
    }
  };

  const addInput = () => {
    const newId = Math.max(0, ...inputs.map(i => i.id)) + 1;
    setInputs([...inputs, { id: newId, value: '' }]);
  };

  const removeInput = (id) => {
    if (inputs.length > 1) {
      setInputs(inputs.filter(input => input.id !== id));
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto bg-zinc-900 min-h-screen">
      {/* Server Management */}
      <Card className="mb-6 bg-zinc-800 border-zinc-700">
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle className="text-zinc-100">MCP Servers</CardTitle>
              <CardDescription className="text-zinc-400">
                Manage local and network MCP servers
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <button 
                onClick={scanNetwork}
                disabled={isScanning}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-zinc-700 
                         rounded-lg transition-colors text-white flex items-center gap-2"
              >
                {ICONS.SCAN} {isScanning ? 'Scanning...' : 'Scan Network'}
              </button>
              <button 
                onClick={() => setShowAddDialog(true)}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 
                         rounded-lg transition-colors text-white flex items-center gap-2"
              >
                {ICONS.ADD} Add Server
              </button>
            </div>
          </div>
        </CardHeader>
        
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Local Servers */}
            {servers.map((server, index) => (
              <div 
                key={server.id}
                className={`p-4 border rounded-lg cursor-pointer transition-colors
                          ${activeServer === index 
                            ? 'border-indigo-500 bg-zinc-700' 
                            : 'border-zinc-600 hover:border-indigo-400'}`}
                onClick={() => setActiveServer(index)}
              >
                <div className="flex justify-between items-center">
                  <span className="font-medium text-zinc-100">{server.name}</span>
                  <span>{ICONS.SETTINGS}</span>
                </div>
                <div className="text-sm text-zinc-400 mt-2">{server.address}</div>
                <div className="text-xs text-zinc-500 mt-1">Local Server</div>
              </div>
            ))}
            
            {/* Discovered Network Servers */}
            {discoveredServers.map(server => (
              <div 
                key={server.id}
                className="p-4 border border-zinc-600 rounded-lg hover:border-indigo-400 
                         transition-colors cursor-pointer"
              >
                <div className="flex justify-between items-center">
                  <span className="font-medium text-zinc-100">{server.name}</span>
                  <span>{ICONS.NETWORK}</span>
                </div>
                <div className="text-sm text-zinc-400 mt-2">
                  {server.address}:{server.port}
                </div>
                <div className="text-xs text-zinc-500 mt-1">Network Server</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Main Content Area */}
      <Tabs defaultValue="io" className="space-y-4">
        <TabsList className="bg-zinc-800 border-zinc-700">
          <TabsTrigger 
            value="io" 
            className="data-[state=active]:bg-zinc-700 text-zinc-100"
          >
            Input/Output
          </TabsTrigger>
          <TabsTrigger 
            value="tools"
            className="data-[state=active]:bg-zinc-700 text-zinc-100"
          >
            Tools
          </TabsTrigger>
          <TabsTrigger 
            value="prompts"
            className="data-[state=active]:bg-zinc-700 text-zinc-100"
          >
            Prompts
          </TabsTrigger>
        </TabsList>

        <TabsContent value="io">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Inputs Card */}
            <Card className="bg-zinc-800 border-zinc-700">
              <CardHeader>
                <CardTitle className="flex justify-between items-center text-zinc-100">
                  <span>Inputs</span>
                  <button 
                    onClick={addInput}
                    className="p-2 bg-indigo-600 hover:bg-indigo-700 rounded-lg"
                  >
                    {ICONS.ADD}
                  </button>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {inputs.map(input => (
                  <div key={input.id} className="flex mb-4">
                    <input
                      value={input.value}
                      onChange={(e) => {
                        setInputs(inputs.map(i => 
                          i.id === input.id ? { ...i, value: e.target.value } : i
                        ));
                      }}
                      className="flex-1 p-2 bg-zinc-700 border-zinc-600 rounded-lg mr-2 
                               text-zinc-100 focus:border-indigo-500"
                      placeholder="Enter input..."
                    />
                    <button
                      onClick={() => copyToClipboard(input.value, `input-${input.id}`)}
                      className="p-2 hover:bg-zinc-700 rounded-lg mr-2"
                    >
                      {copiedItems[`input-${input.id}`] ? ICONS.COPIED : ICONS.COPY}
                    </button>
                    {inputs.length > 1 && (
                      <button
                        onClick={() => removeInput(input.id)}
                        className="p-2 hover:bg-red-900/50 rounded-lg"
                      >
                        {ICONS.REMOVE}
                      </button>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Outputs Card */}
            <Card className="bg-zinc-800 border-zinc-700">
              <CardHeader>
                <CardTitle className="text-zinc-100">Outputs</CardTitle>
              </CardHeader>
              <CardContent>
                {outputs.map(output => (
                  <div key={output.id} className="mb-4 p-4 bg-zinc-700 rounded-lg">
                    <div className="flex justify-between items-start">
                      <div className="text-sm text-zinc-400">
                        {new Date(output.timestamp).toLocaleString()}
                      </div>
                      <button
                        onClick={() => copyToClipboard(output.content, `output-${output.id}`)}
                        className="p-2 hover:bg-zinc-600 rounded-lg"
                      >
                        {copiedItems[`output-${output.id}`] ? ICONS.COPIED : ICONS.COPY}
                      </button>
                    </div>
                    <div className="mt-2 text-zinc-100">{output.content}</div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Add Server Dialog */}
      <AlertDialog open={showAddDialog} onOpenChange={setShowAddDialog}>
        <AlertDialogContent className="bg-zinc-800 border-zinc-700">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-zinc-100">Add MCP Server</AlertDialogTitle>
            <AlertDialogDescription className="text-zinc-400">
              Configure a new MCP server connection
            </AlertDialogDescription>
          </AlertDialogHeader>
          <div className="space-y-4 py-4">
            <input
              type="text"
              placeholder="Server Name"
              className="w-full p-2 bg-zinc-700 border-zinc-600 rounded-lg text-zinc-100"
            />
            <input
              type="text"
              placeholder="Server Address"
              className="w-full p-2 bg-zinc-700 border-zinc-600 rounded-lg text-zinc-100"
            />
          </div>
          <AlertDialogFooter>
            <AlertDialogCancel className="bg-zinc-700 text-zinc-100 hover:bg-zinc-600">
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction className="bg-indigo-600 hover:bg-indigo-700">
              Add Server
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default MCPManager;