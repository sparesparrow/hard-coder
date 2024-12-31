import React, { useState, useRef, useEffect } from 'react';

declare global {
  interface Window {
    webkitSpeechRecognition: any;
    SpeechRecognition: any;
  }
}

const sendMessageToLLM = async (message: string): Promise<string> => {
try {
    const response = await fetch('/api/chat', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
    });

    if (!response.ok) {
    throw new Error('Failed to get response from LLM');
    }

    const data = await response.json();
    return data.response;
} catch (error) {
    console.error('Error sending message to LLM:', error);
    throw error;
}
};
  
interface Message {
    type: 'user' | 'assistant';
    content: string;
    timestamp?: Date;
}

const LLMChatInterface = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputText, setInputText] = useState('');
    const [isListening, setIsListening] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);


    const handleSendMessage = async () => {
        if (!inputText.trim()) return;
        
        const userMessage: Message = {
        type: 'user',
        content: inputText,
        timestamp: new Date()
        };

        try {
        setMessages(prev => [...prev, userMessage]);
        setIsProcessing(true);
        setError(null);
        
        // Replace setTimeout with actual API call
        const response = await sendMessageToLLM(inputText);
        
        setMessages(prev => [...prev, {
            type: 'assistant',
            content: response,
            timestamp: new Date()
        }]);
        } catch (err) {
        setError('Failed to send message. Please try again.');
        } finally {
        setIsProcessing(false);
        setInputText('');
        }
    };

    const toggleVoiceInput = async () => {
        if (!isListening) {
        try {
            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            setInputText(transcript);
            };
            recognition.start();
        } catch (err) {
            setError('Voice input not supported on this browser');
        }
        }
        setIsListening(!isListening);
    };
    return (
        <div className="flex flex-col h-screen bg-gray-900">
        {/* Header */}
        <div className="bg-gray-800 p-4 shadow-lg">
            {/* Add your header content here */}
        </div>
        
        {/* Add the rest of your component structure */}
        </div>
    );
};