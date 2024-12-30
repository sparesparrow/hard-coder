import React, { useState, useEffect, useCallback, useRef } from 'react';

interface GameWord {
  id: string;
  text: string;
  position: {
    left: number;
    top: number;
  };
}

interface PlayerPosition {
  x: number;
  y: number;
}

const GAME_SPEED = 5;
const PLAYER_SIZE = 32;
const SPAWN_RATE = 0.01;

const words = [
  'ability', 'able', 'about', 'above', 'accept', 'according', 'account', 
  'across', 'action', 'activity'
]; // Shortened for brevity

const TypingGame = () => {
  const [score, setScore] = useState(0);
  const [gameWords, setGameWords] = useState<GameWord[]>([]);
  const [currentWord, setCurrentWord] = useState<string>('');
  const [typedWord, setTypedWord] = useState('');
  const [playerPos, setPlayerPos] = useState<PlayerPosition>({ x: 10, y: 10 });
  const [showInput, setShowInput] = useState(false);
  const [startTime, setStartTime] = useState<number | null>(null);
  
  const gameRef = useRef<HTMLDivElement>(null);
  const frameRef = useRef<number>();

  const createWord = useCallback(() => {
    if (!gameRef.current) return;
    
    const gameWidth = gameRef.current.offsetWidth;
    const gameHeight = gameRef.current.offsetHeight;
    
    return {
      id: Math.random().toString(36).substring(7),
      text: words[Math.floor(Math.random() * words.length)],
      position: {
        left: gameWidth + 10,
        top: Math.random() * (gameHeight - 50)
      }
    };
  }, []);

  const checkCollision = useCallback((word: GameWord) => {
    const playerRight = playerPos.x + PLAYER_SIZE;
    const playerBottom = playerPos.y + PLAYER_SIZE;
    const wordRight = word.position.left + 100; // Approximate word width
    const wordBottom = word.position.top + 30; // Approximate word height

    return !(
      playerRight < word.position.left ||
      playerPos.x > wordRight ||
      playerBottom < word.position.top ||
      playerPos.y > wordBottom
    );
  }, [playerPos]);

  const handleWordSubmit = useCallback(() => {
    if (typedWord === currentWord) {
      const endTime = Date.now();
      const timeBonus = Math.max(2000 - (endTime - (startTime || endTime)), 0);
      setScore(prev => prev + Math.round(1000 + timeBonus));
      setShowInput(false);
      setTypedWord('');
      setCurrentWord('');
    }
  }, [typedWord, currentWord, startTime]);

  const gameLoop = useCallback(() => {
    setGameWords(prevWords => {
      const updatedWords = prevWords.map(word => ({
        ...word,
        position: {
          ...word.position,
          left: word.position.left - GAME_SPEED
        }
      })).filter(word => word.position.left > -100);

      if (Math.random() < SPAWN_RATE) {
        const newWord = createWord();
        if (newWord) {
          updatedWords.push(newWord);
        }
      }

      updatedWords.forEach(word => {
        if (checkCollision(word) && !showInput) {
          setCurrentWord(word.text);
          setShowInput(true);
          setStartTime(Date.now());
        }
      });

      return updatedWords;
    });

    frameRef.current = requestAnimationFrame(gameLoop);
  }, [checkCollision, createWord, showInput]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case 'w': setPlayerPos(prev => ({ ...prev, y: Math.max(0, prev.y - GAME_SPEED) })); break;
        case 's': setPlayerPos(prev => ({ ...prev, y: prev.y + GAME_SPEED })); break;
        case 'a': setPlayerPos(prev => ({ ...prev, x: Math.max(0, prev.x - GAME_SPEED) })); break;
        case 'd': setPlayerPos(prev => ({ ...prev, x: prev.x + GAME_SPEED })); break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    frameRef.current = requestAnimationFrame(gameLoop);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      if (frameRef.current) {
        cancelAnimationFrame(frameRef.current);
      }
    };
  }, [gameLoop]);

  return (
    <div className="bg-gray-900 text-white h-screen w-screen overflow-hidden relative">
      <div className="fixed top-4 right-4 text-2xl">
        Score: <span>{score}</span>
      </div>
      
      <div ref={gameRef} className="h-full w-full">
        <div
          className="absolute w-8 h-8 bg-blue-500"
          style={{
            transform: `translate(${playerPos.x}px, ${playerPos.y}px)`
          }}
        />
        
        {gameWords.map(word => (
          <div
            key={word.id}
            className="absolute text-2xl"
            style={{
              left: word.position.left + 'px',
              top: word.position.top + 'px'
            }}
          >
            {word.text}
          </div>
        ))}
      </div>

      {showInput && (
        <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white text-black p-4 rounded">
          <input
            type="text"
            value={typedWord}
            onChange={(e) => setTypedWord(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleWordSubmit()}
            className="border border-gray-300 rounded px-2 py-1 mb-2 w-full"
            autoFocus
          />
          <button
            onClick={handleWordSubmit}
            className="bg-blue-500 text-white px-4 py-2 rounded"
          >
            Submit
          </button>
        </div>
      )}
    </div>
  );
};

export default TypingGame;