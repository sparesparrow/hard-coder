import React, { useState } from 'react';
import { 
  Card, 
  CardHeader, 
  CardTitle, 
  CardContent,
  CardDescription
} from '@/components/ui/card';
import { 
  Tabs, 
  TabsContent, 
  TabsList, 
  TabsTrigger 
} from '@/components/ui/tabs';

// Icons for the interface
const ICONS = {
  ADD: '➕',
  REMOVE: '❌',
  EDIT: '✏️',
  LINK: '🔗',
  COLOR: '🎨',
  SAVE: '💾',
  LAYOUT: '📐',
  EXPAND: '🔍',
};

// Color themes for the workflow
const COLOR_THEMES = {
  default: {
    input: { fill: '#1a365d', stroke: '#2b4c7e', text: '#ffffff' },
    process: { fill: '#064e3b', stroke: '#047857', text: '#ffffff' },
    output: { fill: '#7c2d12', stroke: '#9a3412', text: '#ffffff' }
  },
  neon: {
    input: { fill: '#2d1b69', stroke: '#6b46c1', text: '#ffffff' },
    process: { fill: '#044736', stroke: '#059669', text: '#ffffff' },
    output: { fill: '#5b21b6', stroke: '#7c3aed', text: '#ffffff' }
  },
  pastel: {
    input: { fill: '#dbeafe', stroke: '#3b82f6', text: '#1e3a8a' },
    process: { fill: '#dcfce7', stroke: '#22c55e', text: '#14532d' },
    output: { fill: '#fef3c7', stroke: '#d97706', text: '#78350f' }
  }
};

// Main app component
const MCPWorkflowApp = () => {
  // State for MCP functionality
  const [inputs, setInputs] = useState([
    { id: 1, value: 'Sample Input 1' },
    { id: 2, value: 'Sample Input 2' }
  ]);
  const [outputs, setOutputs] = useState([
    { id: 1, content: 'Sample Output 1' },
    { id: 2, content: 'Sample Output 2' }
  ]);
  
  // State for workflow
  const [workflowDiagram, setWorkflowDiagram] = useState('');
  const [activeTab, setActiveTab] = useState('workflow');

  return (
    <div className="p-6 max-w-6xl mx-auto bg-zinc-900 min-h-screen">
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="bg-zinc-800">
          <TabsTrigger 
            value="workflow" 
            className="data-[state=active]:bg-zinc-700 text-zinc-100"
          >
            Workflow
          </TabsTrigger>
          <TabsTrigger 
            value="preview" 
            className="data-[state=active]:bg-zinc-700 text-zinc-100"
          >
            Preview
          </TabsTrigger>
        </TabsList>

        <TabsContent value="workflow">
          <WorkflowDesigner 
            inputs={inputs}
            outputs={outputs}
            workflowDiagram={workflowDiagram}
            setWorkflowDiagram={setWorkflowDiagram}
          />
        </TabsContent>

        <TabsContent value="preview">
          <Card className="bg-zinc-800 border-zinc-700">
            <CardHeader>
              <CardTitle className="text-zinc-100">Workflow Preview</CardTitle>
              <CardDescription className="text-zinc-400">
                Current workflow visualization
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="bg-zinc-900 p-4 rounded-lg overflow-x-auto">
                <pre className="text-zinc-100 whitespace-pre-wrap">{workflowDiagram}</pre>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

// Workflow designer component
const WorkflowDesigner = ({ inputs, outputs, workflowDiagram, setWorkflowDiagram }) => {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [colorTheme, setColorTheme] = useState('default');
  const [layout, setLayout] = useState('TB');
  const [showNodePanel, setShowNodePanel] = useState(false);
  
  // Store for saved nodes
  const [savedNodes, setSavedNodes] = useState({
    inputs: [],
    outputs: [],
    processes: []
  });

  // Generate the Mermaid diagram
  const updateDiagram = () => {
    const colors = COLOR_THEMES[colorTheme];
    
    const diagram = `graph ${layout}
      %% Style definitions
      classDef input fill:${colors.input.fill},stroke:${colors.input.stroke},color:${colors.input.text}
      classDef process fill:${colors.process.fill},stroke:${colors.process.stroke},color:${colors.process.text}
      classDef output fill:${colors.output.fill},stroke:${colors.output.stroke},color:${colors.output.text}

      %% Nodes
      ${nodes.map(node => `${node.id}[${node.label}]`).join('\n      ')}

      %% Edges
      ${edges.map(edge => `${edge.from} --> ${edge.to}`).join('\n      ')}

      %% Apply styles
      ${nodes.filter(n => n.type === 'input').map(n => `class ${n.id} input`).join('\n      ')}
      ${nodes.filter(n => n.type === 'process').map(n => `class ${n.id} process`).join('\n      ')}
      ${nodes.filter(n => n.type === 'output').map(n => `class ${n.id} output`).join('\n      ')}`;

    setWorkflowDiagram(diagram);
  };

  // Add a new node
  const addNode = (type, content) => {
    const newId = `node${nodes.length + 1}`;
    const newNode = {
      id: newId,
      type,
      label: content.value || content.content || content,
      data: content
    };
    setNodes([...nodes, newNode]);
    updateDiagram();
  };

  // Save a node for reuse
  const saveNode = (item, type) => {
    setSavedNodes(prev => ({
      ...prev,
      [type]: [...prev[type], item]
    }));
  };

  // Add an edge between nodes
  const addEdge = (fromId, toId) => {
    const newEdge = { from: fromId, to: toId };
    setEdges([...edges, newEdge]);
    updateDiagram();
  };

  return (
    <div className="space-y-4">
      {/* Controls Card */}
      <Card className="bg-zinc-800 border-zinc-700">
        <CardHeader>
          <CardTitle className="text-zinc-100 flex justify-between items-center">
            <span>Workflow Designer</span>
            <div className="flex gap-2">
              <button 
                onClick={() => setLayout(layout === 'TB' ? 'LR' : 'TB')}
                className="p-2 bg-zinc-700 hover:bg-zinc-600 rounded-lg text-zinc-100"
              >
                {ICONS.LAYOUT} {layout}
              </button>
              <button 
                onClick={() => setShowNodePanel(!showNodePanel)}
                className="p-2 bg-zinc-700 hover:bg-zinc-600 rounded-lg text-zinc-100"
              >
                {ICONS.ADD} Add Node
              </button>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* Theme Selection */}
          <div className="flex gap-4 mb-4">
            {Object.keys(COLOR_THEMES).map(theme => (
              <button
                key={theme}
                onClick={() => {
                  setColorTheme(theme);
                  updateDiagram();
                }}
                className={`p-2 rounded-lg text-zinc-100 ${
                  colorTheme === theme 
                    ? 'bg-indigo-600' 
                    : 'bg-zinc-700 hover:bg-zinc-600'
                }`}
              >
                {theme}
              </button>
            ))}
          </div>

          {/* Node Panel */}
          {showNodePanel && (
            <div className="mt-4 p-4 bg-zinc-700 rounded-lg">
              {/* Saved Inputs */}
              <div className="mb-4">
                <h4 className="text-zinc-300 mb-2">Available Inputs</h4>
                <div className="flex flex-wrap gap-2">
                  {savedNodes.inputs.map((input, idx) => (
                    <button
                      key={idx}
                      onClick={() => addNode('input', input)}
                      className="p-2 bg-zinc-600 hover:bg-zinc-500 rounded-lg text-zinc-100"
                    >
                      {input.value || input}
                    </button>
                  ))}
                  {inputs.map((input, idx) => (
                    <button
                      key={`current-${idx}`}
                      onClick={() => {
                        addNode('input', input);
                        saveNode(input, 'inputs');
                      }}
                      className="p-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-zinc-100"
                    >
                      {input.value}
                    </button>
                  ))}
                </div>
              </div>

              {/* Saved Outputs */}
              <div className="mb-4">
                <h4 className="text-zinc-300 mb-2">Available Outputs</h4>
                <div className="flex flex-wrap gap-2">
                  {savedNodes.outputs.map((output, idx) => (
                    <button
                      key={idx}
                      onClick={() => addNode('output', output)}
                      className="p-2 bg-zinc-600 hover:bg-zinc-500 rounded-lg text-zinc-100"
                    >
                      {output.content || output}
                    </button>
                  ))}
                  {outputs.map((output, idx) => (
                    <button
                      key={`current-${idx}`}
                      onClick={() => {
                        addNode('output', output);
                        saveNode(output, 'outputs');
                      }}
                      className="p-2 bg-orange-600 hover:bg-orange-700 rounded-lg text-zinc-100"
                    >
                      {output.content}
                    </button>
                  ))}
                </div>
              </div>

              {/* Process Creation */}
              <div>
                <h4 className="text-zinc-300 mb-2">Add Process Node</h4>
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="Process name..."
                    className="flex-1 p-2 bg-zinc-600 border-zinc-500 rounded-lg text-zinc-100"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && e.target.value) {
                        addNode('process', e.target.value);
                        saveNode(e.target.value, 'processes');
                        e.target.value = '';
                      }
                    }}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Node Connection Controls */}
          {nodes.length > 0 && (
            <div className="mt-4 p-4 bg-zinc-700 rounded-lg">
              <h3 className="text-zinc-100 mb-4">Connect Nodes</h3>
              <div className="flex gap-4">
                <select 
                  className="p-2 bg-zinc-600 border-zinc-500 rounded-lg text-zinc-100"
                  onChange={(e) => setSelectedNode(e.target.value)}
                  value={selectedNode || ''}
                >
                  <option value="">Select source node...</option>
                  {nodes.map(node => (
                    <option key={node.id} value={node.id}>
                      {node.label}
                    </option>
                  ))}
                </select>
                <select 
                  className="p-2 bg-zinc-600 border-zinc-500 rounded-lg text-zinc-100"
                  onChange={(e) => {
                    if (selectedNode && e.target.value) {
                      addEdge(selectedNode, e.target.value);
                      setSelectedNode(null);
                      e.target.value = '';
                    }
                  }}
                >
                  <option value="">Select target node...</option>
                  {nodes
                    .filter(node => node.id !== selectedNode)
                    .map(node => (
                      <option key={node.id} value={node.id}>
                        {node.label}
                      </option>
                    ))}
                </select>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Current Workflow */}
      <Card className="bg-zinc-800 border-zinc-700">
        <CardHeader>
          <CardTitle className="text-zinc-100">Current Workflow</CardTitle>
          <CardDescription className="text-zinc-400">
            {nodes.length} nodes, {edges.length} connections
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-zinc-900 p-4 rounded-lg overflow-x-auto">
            <pre className="text-zinc-100 whitespace-pre-wrap">{workflowDiagram}</pre>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default MCPWorkflowApp;