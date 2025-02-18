import React, { useState, useEffect } from 'react';
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

type ExampleType = 'flowchart' | 'sequence' | 'gantt' | 'class';

const MermaidEditor = () => {
  // State for source code and error handling
  const [sourceCode, setSourceCode] = useState(`graph TD
    A[Start] --> B[Process]
    B --> C[End]`);
  const [isValid, setIsValid] = useState(true);
  const [error, setError] = useState('');
  const [currentTab, setCurrentTab] = useState('editor');

  // Basic examples for quick insertion
  const examples = {
    flowchart: `graph TD
    A[Start] --> B[Process]
    B --> C[End]`,
    sequence: `sequenceDiagram
    Alice->>John: Hello John, how are you?
    John-->>Alice: Great!`,
    gantt: `gantt
    title A Gantt Diagram
    dateFormat  YYYY-MM-DD
    section Section
    A task           :a1, 2024-01-01, 30d
    Another task     :after a1, 20d`,
    class: `classDiagram
    Class01 <|-- Class02
    Class03 *-- Class04
    Class05 o-- Class06`,
  };

  // Handle source code changes
  const handleSourceChange = (newSource: string) => {
    setSourceCode(newSource);
    try {
      setIsValid(true);
      setError('');
    } catch (err: unknown) {
      setIsValid(false);
      setError(err instanceof Error ? err.message : 'Unknown error');
    }
  };

  // Insert example code
  const insertExample = (type: ExampleType) => {
    handleSourceChange(examples[type]);
  };

  return (
    <div className="p-6 max-w-6xl mx-auto bg-zinc-900 min-h-screen">
      <Tabs value={currentTab} onValueChange={setCurrentTab}>
        <TabsList className="bg-zinc-800">
          <TabsTrigger 
            value="editor" 
            className="data-[state=active]:bg-zinc-700 text-zinc-100"
          >
            Editor
          </TabsTrigger>
          <TabsTrigger 
            value="preview" 
            className="data-[state=active]:bg-zinc-700 text-zinc-100"
          >
            Preview
          </TabsTrigger>
        </TabsList>

        <TabsContent value="editor">
          <div className="grid gap-4">
            {/* Example Buttons */}
            <Card className="bg-zinc-800 border-zinc-700">
              <CardHeader>
                <CardTitle className="text-zinc-100">Quick Examples</CardTitle>
                <CardDescription className="text-zinc-400">
                  Insert example diagrams to get started
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {Object.keys(examples).map((type) => (
                    <button
                      key={type}
                      onClick={() => insertExample(type as ExampleType)}
                      className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 
                               rounded-lg text-zinc-100 transition-colors"
                    >
                      {type.charAt(0).toUpperCase() + type.slice(1)}
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Editor */}
            <Card className="bg-zinc-800 border-zinc-700">
              <CardHeader>
                <CardTitle className="text-zinc-100">Mermaid Source Code</CardTitle>
                <CardDescription className="text-zinc-400">
                  Enter your Mermaid diagram source code here
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="relative">
                  <textarea
                    value={sourceCode}
                    onChange={(e) => handleSourceChange(e.target.value)}
                    className="w-full h-96 p-4 bg-zinc-900 text-zinc-100 
                             font-mono rounded-lg resize-none border border-zinc-700
                             focus:outline-none focus:border-indigo-500"
                    spellCheck="false"
                  />
                  {!isValid && (
                    <div className="mt-2 p-2 bg-red-900/50 text-red-200 rounded-lg">
                      {error}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="preview">
          <Card className="bg-zinc-800 border-zinc-700">
            <CardHeader>
              <CardTitle className="text-zinc-100">Diagram Preview</CardTitle>
              <CardDescription className="text-zinc-400">
                Live preview of your Mermaid diagram
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="bg-zinc-900 p-4 rounded-lg overflow-x-auto min-h-[400px]">
                <pre className="text-zinc-100 whitespace-pre-wrap">{sourceCode}</pre>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default MermaidEditor;