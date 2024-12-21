import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Mic, Volume2, VolumeX } from 'lucide-react';
import { useConversation } from '@11labs/react';

const IntegratedAIInterface = () => {
  const [userInput, setUserInput] = useState('');
  const [responses, setResponses] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [currentAudioResponse, setCurrentAudioResponse] = useState(null);
  const [volume, setVolume] = useState(0.8);
  const [isMuted, setIsMuted] = useState(false);

  // Initialize ElevenLabs conversation
  const conversation = useConversation({
    clientTools: {
      triggerClaudeRequest: async (parameters) => {
        try {
          // Make API call to your backend that handles Claude API
          const response = await fetch('/api/claude', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(parameters)
          });
          const data = await response.json();
          return data.response;
        } catch (error) {
          console.error('Error triggering Claude:', error);
          return 'Failed to process request';
        }
      }
    },
    onMessage: (message) => {
      if (message.type === 'response') {
        setResponses(prev => [...prev, message.content]);
      }
    }
  });

  const handleSubmit = async () => {
    if (!userInput.trim() || isProcessing) return;
    
    setIsProcessing(true);
    try {
      // Start streaming response from Claude
      const response = await fetch('/api/stream-claude', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: userInput })
      });

      const reader = response.body.getReader();
      let accumulatedResponse = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const text = new TextDecoder().decode(value);
        accumulatedResponse += text;
        
        setResponses(prev => {
          const newResponses = [...prev];
          newResponses[newResponses.length - 1] = accumulatedResponse;
          return newResponses;
        });
      }

      // Generate text-to-speech for the response
      const audioResponse = await fetch('/api/text-to-speech', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: accumulatedResponse })
      });

      const audioBlob = await audioResponse.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      setCurrentAudioResponse(audioUrl);
      
      if (!isMuted) {
        const audio = new Audio(audioUrl);
        audio.volume = volume;
        audio.play();
        setIsSpeaking(true);
        audio.onended = () => setIsSpeaking(false);
      }

    } catch (error) {
      console.error('Error processing request:', error);
      setResponses(prev => [...prev, 'An error occurred while processing your request.']);
    } finally {
      setIsProcessing(false);
      setUserInput('');
    }
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle>AI Assistant</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center space-x-2">
            <Button 
              variant="outline" 
              size="icon"
              onClick={toggleMute}
            >
              {isMuted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
            </Button>
            {!isMuted && (
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={volume}
                onChange={(e) => setVolume(parseFloat(e.target.value))}
                className="w-24"
              />
            )}
          </div>

          <div className="h-96 overflow-y-auto border rounded-lg p-4 bg-gray-50">
            {responses.map((response, idx) => (
              <div key={idx} className="mb-4">
                <p className="whitespace-pre-wrap">{response}</p>
              </div>
            ))}
            {isProcessing && (
              <div className="animate-pulse">Processing...</div>
            )}
          </div>

          <div className="flex items-center space-x-2">
            <Textarea
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              placeholder="Type your message..."
              className="flex-1"
              rows={3}
            />
            <Button
              onClick={handleSubmit}
              disabled={isProcessing || !userInput.trim()}
            >
              Send
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default IntegratedAIInterface;