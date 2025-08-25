import { useState, useEffect, useRef, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent } from "@/components/ui/card";
import { Send, Zap, Gamepad2, Square } from "lucide-react";
import { mayaAPI, SSEEvent } from "@/services/api";
import { useGame } from "@/contexts/GameContext";
import { StatusBox } from "@/components/ui/StatusBox";
import { SuggestionCards } from "@/components/ui/SuggestionCards";
import { BuildingStatus } from "@/components/ui/BuildingStatus";
import { CodeStreamBox } from "@/components/ui/CodeStreamBox";
import { FormattedText } from "@/utils/textFormatter";

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  showSuggestions?: boolean;
  suggestions?: string[];
  codeStream?: {
    content: string;
    currentType: 'html' | 'css' | 'js';
  };
  gameStatus?: {
    isCompleted: boolean;
    bullets: string[];
  };
}


interface ChatInterfaceProps {
  initialPrompt?: string;
}

export function ChatInterface({ initialPrompt }: ChatInterfaceProps) {
  const { gameState, generateGame, cancelGeneration } = useGame();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: 'Hey there! I\'m Maya, your AI game creation companion. Ready to bring your game idea to life? I\'ll generate the code and help you iterate on your concept.',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [currentAssistantMessage, setCurrentAssistantMessage] = useState<string>('');
  const [pendingMessageId, setPendingMessageId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Get overall status bullets based on current operation type and phase
  const getOverallStatusBullets = useCallback((): string[] => {
    const { phase } = gameState.statusBox;
    const { isGenerating, status, operationType, publisher } = gameState;
    
    // Handle publisher operations
    if (operationType === 'publishing') {
      if (publisher.status === 'published') {
        return [
          '✅ Game verified',
          '✅ Deployment prepared',
          '✅ Files uploaded to Firebase',
          '✅ Hosting configured',
          '🎉 Game is now live on Firebase!'
        ];
      }
      
      if (!publisher.isPublishing) return [];
      
      switch (publisher.status) {
        case 'validating':
          return ['🔍 Checking if a game has been created...'];
        
        case 'preparing':
          return [
            '✓ Game found!',
            '🚀 Preparing for deployment...'
          ];
        
        case 'deploying':
          return [
            '✓ Game found!',
            '✓ Deployment prepared',
            '📤 Uploading to Firebase hosting...'
          ];
        
        default:
          return ['🚀 Preparing to publish...'];
      }
    }
    
    // Handle game creation operations (existing logic)
    if (status === 'completed') {
      return [
        '✅ Request analyzed',
        '✅ Game concept designed', 
        '✅ Code generated',
        '✅ Features implemented',
        '🎮 Game completed!'
      ];
    }
    
    if (!isGenerating) return [];
    
    switch (phase) {
      case 'analyzing':
        return ['🔍 Analyzing your request...'];
      
      case 'thinking':
        return [
          '✓ Request analyzed',
          '🧠 Planning game concept...'
        ];
      
      case 'outlining':
        return [
          '✓ Request analyzed',
          '✓ Game concept designed',
          '📝 Outlining implementation...'
        ];
      
      case 'generating':
        return [
          '✓ Request analyzed',
          '✓ Game concept designed', 
          '✓ Implementation outlined',
          '⚡ Generating code...'
        ];
      
      case 'previewing':
        return [
          '✓ Request analyzed',
          '✓ Game concept designed', 
          '✓ Implementation outlined',
          '✓ Code generated',
          '🎬 Preparing preview...'
        ];
      
      default:
        return ['🚀 Starting up...'];
    }
  }, [gameState.statusBox.phase, gameState.isGenerating, gameState.status, gameState.operationType, gameState.publisher]);

  useEffect(() => {
    if (initialPrompt) {
      handleSend(initialPrompt);
    }
  }, [initialPrompt]);

  const handleSend = async (promptOverride?: string) => {
    const prompt = promptOverride || input;
    if (!prompt.trim() || gameState.isGenerating || gameState.publisher.isPublishing) return;

    // Save any existing streaming message to permanent history before starting new one
    if (currentAssistantMessage.trim()) {
      const existingMessage: Message = {
        id: Date.now().toString(),
        type: 'assistant',
        content: currentAssistantMessage,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, existingMessage]);
    }

    const userMessage: Message = {
      id: (Date.now() + 1).toString(),
      type: 'user',
      content: prompt,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setCurrentAssistantMessage('');

    // Create a new assistant message that will be updated in real-time
    const assistantMessageId = (Date.now() + 2).toString();
    setPendingMessageId(assistantMessageId);
    
    // Handle chat streaming events
    const handleChatEvent = (event: SSEEvent) => {
      switch (event.type) {
        case 'explanation':
          if (typeof event.payload === 'string') {
            setCurrentAssistantMessage(prev => prev + event.payload);
          }
          break;
        
        case 'features':
          if (typeof event.payload === 'string') {
            setCurrentAssistantMessage(prev => prev + `\n\n## Game Features\n${event.payload}`);
          }
          break;
        
        // suggestions are handled by GameContext and shown as cards only
        case 'suggestions':
          // Don't add suggestions to chat text - they appear as cards
          break;
        
        case 'command':
          if (typeof event.payload === 'string') {
            const commandMatch = event.payload.match(/<(\w+)>([^<]+)</);
            if (commandMatch) {
              const commandContent = commandMatch[2];
              setCurrentAssistantMessage(prev => prev + `\n\n🔧 ${commandContent}\n`);
            } else {
              setCurrentAssistantMessage(prev => prev + `\n\n🔧 ${event.payload}\n`);
            }
          }
          break;
        
        case 'error':
          setCurrentAssistantMessage(prev => prev + `\n\n❌ Error: ${event.payload}`);
          break;
        
        case 'publish_message':
          // Handle publisher responses (URLs, success messages)
          if (typeof event.payload === 'string') {
            setCurrentAssistantMessage(prev => prev + event.payload);
          }
          break;

        // We explicitly ignore 'code_chunk' here, as it's handled by the GameContext
        case 'code_chunk':
        default:
          break;
      }
    };

    try {
      // Use the unified game generation that handles both game state and chat
      await generateGame(prompt, true, handleChatEvent);

      // Final message will be created by useEffect when generation completes

    } catch (error) {
      const errorMessage: Message = {
        id: assistantMessageId,
        type: 'assistant',
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
      setCurrentAssistantMessage('');
    }
  };

  const handleNextStep = (step: string) => {
    setInput(step);
  };

  const handleCancel = () => {
    cancelGeneration();
    setCurrentAssistantMessage('');
    setPendingMessageId(null);
  };

  // Auto-scroll to bottom when messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentAssistantMessage]);

  // Capture completed operations and create final message
  useEffect(() => {
    if ((gameState.status === 'completed' && !gameState.isGenerating && pendingMessageId) || 
        (gameState.publisher.status === 'published' && !gameState.publisher.isPublishing && pendingMessageId)) {
      console.log('Generation completed, creating final message with status:', gameState.status);
      console.log('Available data:', {
        codeStream: gameState.codeStream.content?.length,
        suggestions: gameState.suggestions?.length,
        currentMessage: currentAssistantMessage.length
      });

      const finalMessage: Message = {
        id: pendingMessageId,
        type: 'assistant',
        content: currentAssistantMessage,
        timestamp: new Date(),
        showSuggestions: true,
        codeStream: (gameState.codeStream.content && gameState.operationType === 'game_creation') ? {
          content: gameState.codeStream.content,
          currentType: gameState.codeStream.currentType
        } : undefined,
        suggestions: gameState.suggestions.length > 0 ? gameState.suggestions : undefined,
        gameStatus: {
          isCompleted: true,
          bullets: getOverallStatusBullets()
        }
      };
      
      setMessages(prev => [...prev, finalMessage]);
      setCurrentAssistantMessage('');
      setPendingMessageId(null);
    }
  }, [gameState.status, gameState.isGenerating, gameState.publisher.status, gameState.publisher.isPublishing, gameState.codeStream.content, gameState.suggestions, currentAssistantMessage, pendingMessageId, getOverallStatusBullets]);

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-border bg-card/50 backdrop-blur">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 rounded-full bg-primary animate-pulse"></div>
          <h2 className="text-lg font-orbitron font-bold text-primary neon-pulse">
            MAYA AI
          </h2>
          <Zap className="w-4 h-4 text-accent" />
        </div>
        <p className="text-sm text-muted-foreground mt-1">
          Game Creation Assistant
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div key={message.id} className="space-y-4">
            <div className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              <Card className={`max-w-[80%] ${ 
                message.type === 'user' 
                  ? 'bg-primary/20 border-primary/50' 
                  : 'bg-secondary/20 border-secondary/50'
              } backdrop-blur cyber-grid`}>
                <CardContent className="p-3">
                  {message.type === 'assistant' ? (
                    <FormattedText className="text-sm">
                      {message.content}
                    </FormattedText>
                  ) : (
                    <p className="text-sm whitespace-pre-wrap">
                      {message.content}
                    </p>
                  )}
                  <div className="text-xs text-muted-foreground mt-2">
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </CardContent>
              </Card>
            </div>
            
            {/* Show saved game status for assistant messages */}
            {message.type === 'assistant' && message.gameStatus && (
              <BuildingStatus
                bullets={message.gameStatus.bullets}
                isCompleted={message.gameStatus.isCompleted}
                className="mb-4"
              />
            )}
            
            {/* Show code stream for assistant messages */}
            {message.type === 'assistant' && message.codeStream && (
              <CodeStreamBox
                codeContent={message.codeStream.content}
                currentType={message.codeStream.currentType}
                className="mb-4 max-w-[98%]"
              />
            )}
            
            {/* Show suggestions for assistant messages */}
            {message.type === 'assistant' && message.showSuggestions && message.suggestions && (
              <SuggestionCards
                suggestions={message.suggestions}
                onSuggestionClick={handleNextStep}
                className="mt-2"
              />
            )}
          </div>
        ))}

        {/* Live Status - during active generation or publishing (not when completed) */}
        {(gameState.isGenerating || gameState.publisher.isPublishing) && 
         !(gameState.status === 'completed' || gameState.publisher.status === 'published') && (
          <div className="max-w-[90%]">
            <BuildingStatus
              bullets={getOverallStatusBullets()}
              isCompleted={false}
              className=""
            />
          </div>
        )}

        {/* Current streaming message */}
        {currentAssistantMessage && (
          <div className="flex justify-start">
            <Card className="max-w-[80%] bg-secondary/20 border-secondary/50 backdrop-blur cyber-grid">
              <CardContent className="p-3">
                <div className="text-sm">
                  <FormattedText className="">
                    {currentAssistantMessage}
                  </FormattedText>
                  <span className="animate-pulse ml-1">▋</span>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Removed - replaced by overall status above */}

        {/* Live Code Stream Box - only during active code generation streaming */}
        {gameState.codeStream.content && gameState.codeStream.isStreaming && gameState.operationType === 'game_creation' && (
          <CodeStreamBox
            codeContent={gameState.codeStream.content}
            currentType={gameState.codeStream.currentType}
            className="mb-4 max-w-[98%]"
          />
        )}

        {/* Dynamic Status Box - only for analyzing/thinking phases */}
        {gameState.statusBox && ['analyzing', 'thinking'].includes(gameState.statusBox.phase) && (
          <StatusBox
            phase={gameState.statusBox.phase}
            bullets={gameState.statusBox.bullets || []}
            tip={gameState.statusBox.tip}
            className="max-w-[80%]"
          />
        )}

        
        {/* Auto-scroll anchor */}
        <div ref={messagesEndRef} />
      </div>


      {/* Input */}
      <div className="p-4 border-t border-border bg-card/50 backdrop-blur">
        <div className="flex space-x-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Describe your game idea... (e.g., 'Create a puzzle game where players match colors')"
            className="flex-1 min-h-[60px] bg-background/50 border-primary/30 focus:border-primary/50 resize-none"
            disabled={gameState.isGenerating || gameState.publisher.isPublishing}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
          />
          {(gameState.isGenerating || gameState.publisher.isPublishing) ? (
            <Button
              onClick={handleCancel}
              variant="destructive"
              className="px-6"
            >
              <Square className="w-4 h-4" />
            </Button>
          ) : (
            <Button
              onClick={() => handleSend()}
              disabled={!input.trim()}
              className="bg-gradient-to-r from-primary to-secondary hover:from-primary/80 hover:to-secondary/80 shadow-[var(--shadow-cyber)] px-6"
            >
              <Send className="w-4 h-4" />
            </Button>
          )}
        </div>
        
        <div className="text-xs text-muted-foreground mt-2 flex items-center space-x-4">
          <span>Press Enter to send, Shift+Enter for new line</span>
          <span className="text-accent">•</span>
          <span>Powered by Maya AI</span>
        </div>
      </div>
    </div>
  );
}