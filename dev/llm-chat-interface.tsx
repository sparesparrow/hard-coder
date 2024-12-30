import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, StopCircle } from 'lucide-react';

const LLMChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = () => {
    if (inputText.trim()) {
      setMessages([...messages, { 
        type: 'user',
        content: inputText
      }]);
      setIsProcessing(true);
      // Simulate LLM response
      setTimeout(() => {
        setMessages(prev => [...prev, {
          type: 'assistant',
          content: `Response to: ${inputText}`
        }]);
        setIsProcessing(false);
      }, 1000);
      setInputText('');
    }
  };

  const toggleVoiceInput = () => {
    setIsListening(!isListening);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800 p-4 shadow-lg">
        <h1 className="text-xl text-white font-semibold">AI Assistant</h1>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div key={index} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-3/4 p-3 rounded-lg ${
              message.type === 'user' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-700 text-white'
            }`}>
              {message.content}
            </div>
          </div>
        ))}
        {isProcessing && (
          <div className="flex justify-start">
            <div className="bg-gray-700 text-white p-3 rounded-lg">
              Thinking...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-gray-800 p-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Type your message..."
            className="flex-1 px-4 py-2 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={toggleVoiceInput}
            className={`p-2 rounded-lg ${
              isListening ? 'bg-red-500 hover:bg-red-600' : 'bg-blue-500 hover:bg-blue-600'
            }`}
          >
            {isListening ? <StopCircle size={24} /> : <Mic size={24} />}
          </button>
          <button
            onClick={handleSendMessage}
            className="bg-blue-500 hover:bg-blue-600 p-2 rounded-lg"
          >
            <Send size={24} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default LLMChatInterface;