import React, { createContext, useContext, useState, ReactNode } from 'react';
import { GameCode, SSEEvent, mayaAPI } from '@/services/api';

export interface StatusBoxState {
  phase: 'analyzing' | 'thinking' | 'outlining' | 'generating' | 'previewing' | 'completed' | 'suggesting' | 'idle';
  bullets: string[];
  tip?: string;
}

export interface BuildingState {
  bullets: string[];
  isBuilding: boolean;
}

export interface CodeStreamState {
  content: string;
  currentType: 'html' | 'css' | 'js';
  isStreaming: boolean;
}

export interface PublisherState {
  status: 'idle' | 'validating' | 'preparing' | 'deploying' | 'published' | 'error';
  liveUrl?: string;
  siteName?: string;
  error?: string;
  isPublishing: boolean;
}

export interface GameState {
  code: GameCode | null;
  isGenerating: boolean;
  status: 'idle' | 'thinking' | 'generating' | 'completed' | 'error';
  error: string | null;
  statusBox: StatusBoxState;
  buildingStatus: BuildingState;
  codeStream: CodeStreamState;
  suggestions: string[]; // LLM-generated suggestions
  publisher: PublisherState;
  operationType: 'game_creation' | 'publishing' | 'idle'; // Track what operation is active
}

interface GameContextType {
  gameState: GameState;
  generateGame: (prompt: string, useRealAgent?: boolean) => Promise<void>;
  cancelGeneration: () => void;
  clearGame: () => void;
  updateStatusBox: (update: Partial<StatusBoxState>) => void;
}

const GameContext = createContext<GameContextType | undefined>(undefined);

export function GameProvider({ children }: { children: ReactNode }) {
  const [gameState, setGameState] = useState<GameState>({
    code: null,
    isGenerating: false,
    status: 'idle',
    error: null,
    statusBox: {
      phase: 'idle',
      bullets: [],
      tip: undefined
    },
    buildingStatus: {
      bullets: [],
      isBuilding: false
    },
    codeStream: {
      content: '',
      currentType: 'html',
      isStreaming: false
    },
    suggestions: [],
    publisher: {
      status: 'idle',
      isPublishing: false
    },
    operationType: 'idle'
  });

  // Generate a persistent session ID for this conversation
  const [sessionId] = useState(() => 
    `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  );

  const generateGame = async (
    prompt: string, 
    useRealAgent: boolean = true,
    onChatEvent?: (event: SSEEvent) => void
  ) => {
    // Reset state only for game creation, not for publishing
    setGameState(prev => ({
      ...prev,
      isGenerating: true,
      status: 'thinking',
      error: null,
      statusBox: {
        phase: 'analyzing',
        bullets: ['Starting...'],
        tip: 'Analyzing your request...'
      },
      buildingStatus: {
        bullets: prev.buildingStatus.bullets, // Keep previous bullets until new ones arrive
        isBuilding: false
      },
      codeStream: {
        content: prev.codeStream.content, // Keep previous content until new content arrives
        currentType: prev.codeStream.currentType,
        isStreaming: false
      },
      suggestions: prev.suggestions, // Keep previous suggestions until new ones arrive
      publisher: {
        ...prev.publisher,
        isPublishing: false,
        error: undefined
      },
      operationType: 'idle' // Let the event handler set the correct operation type
    }));

    const handleEvent = (event: SSEEvent) => {
      // Detect operation type based on event types
      if (['publish_status', 'publish_success', 'publish_error', 'publish_message'].includes(event.type)) {
        setGameState(prev => ({ ...prev, operationType: 'publishing' }));
      } else if (['status', 'explanation', 'code', 'features'].includes(event.type)) {
        setGameState(prev => ({ ...prev, operationType: 'game_creation' }));
      }

      switch (event.type) {
        // Publisher events
        case 'publish_status':
          const publishStatus = event.payload as 'validating' | 'preparing' | 'deploying';
          setGameState(prev => ({
            ...prev,
            publisher: {
              ...prev.publisher,
              status: publishStatus,
              isPublishing: true,
              error: undefined
            },
            statusBox: {
              ...prev.statusBox,
              phase: publishStatus === 'validating' ? 'analyzing' : 
                     publishStatus === 'preparing' ? 'thinking' : 'generating',
              tip: publishStatus === 'validating' ? 'Checking if a game has been created...' :
                   publishStatus === 'preparing' ? 'Game found! Preparing for deployment...' :
                   'Deploying to Firebase hosting...'
            }
          }));
          break;

        case 'publish_success':
          const successData = event.payload as { live_url: string; site_name: string; message: string };
          setGameState(prev => ({
            ...prev,
            publisher: {
              ...prev.publisher,
              status: 'published',
              isPublishing: false,
              liveUrl: successData.live_url,
              siteName: successData.site_name,
              error: undefined
            },
            statusBox: {
              ...prev.statusBox,
              phase: 'completed',
              tip: 'Your game is now live!'
            }
          }));
          break;

        case 'publish_error':
          const errorType = event.payload as string;
          setGameState(prev => ({
            ...prev,
            publisher: {
              ...prev.publisher,
              status: 'error',
              isPublishing: false,
              error: errorType
            },
            statusBox: {
              ...prev.statusBox,
              phase: 'idle',
              tip: undefined
            }
          }));
          break;

        case 'publish_message':
          // Forward publisher messages to chat
          if (onChatEvent) {
            onChatEvent(event);
          }
          break;

        case 'status':
          const status = event.payload as 'thinking' | 'generating';
          setGameState(prev => ({
            ...prev,
            status,
            statusBox: {
              ...prev.statusBox,
              phase: status === 'thinking' ? 'thinking' : 'generating',
              bullets: []
            }
          }));
          break;

        case 'explanation':
          // Update status to outlining when explanation arrives
          setGameState(prev => ({
            ...prev,
            statusBox: {
              ...prev.statusBox,
              phase: 'outlining',
              tip: 'Designing your game concept...'
            }
          }));
          // Forward to chat interface
          if (typeof event.payload === 'string' && event.payload.trim()) {
            if (onChatEvent) {
              onChatEvent(event);
            }
          }
          break;

        case 'features':
          // Forward features to chat interface for formatting
          if (typeof event.payload === 'string' && event.payload.trim()) {
            if (onChatEvent) {
              onChatEvent(event);
            }
          }
          break;

        case 'suggestions':
          // Parse suggestions from LLM text and store them
          if (typeof event.payload === 'string') {
            const suggestionsText = event.payload;
            
            // Extract bullet points from suggestions text
            const lines = suggestionsText.split('\n');
            const parsedSuggestions: string[] = [];
            
            for (const line of lines) {
              const trimmed = line.trim();
              // Match bullet points (- or * or numbered lists)
              if (trimmed.match(/^[-*]\s+(.+)/) || trimmed.match(/^\d+\.\s+(.+)/)) {
                const content = trimmed.replace(/^[-*]\s+/, '').replace(/^\d+\.\s+/, '');
                if (content) {
                  parsedSuggestions.push(content);
                }
              }
            }
            
            // Use parsed suggestions or fallback to defaults
            const finalSuggestions = parsedSuggestions.length > 0 ? parsedSuggestions : [
              "Add sound effects",
              "Change colors to neon theme", 
              "Increase difficulty",
              "Add particle effects",
              "Create power-ups",
              "Add multiplayer mode"
            ];
            
            setGameState(prev => ({
              ...prev,
              suggestions: finalSuggestions,
              statusBox: {
                ...prev.statusBox,
                phase: 'completed',
                tip: 'Your game is ready! Try the suggestions below.'
              }
            }));
          }
          break;

        case 'code_chunk':
          // Handle real code streaming - this goes to CodeStreamBox
          if (typeof event.payload === 'string' && event.payload.trim()) {
            const codeContent = event.payload;
            
            setGameState(prev => {
              // Build up bullets progressively
              let newBuildingBullets = [...prev.buildingStatus.bullets];
              
              if (!prev.buildingStatus.isBuilding) {
                newBuildingBullets = ['🔧 Setting up HTML structure'];
              }
              
              // Add bullets based on what we detect in the code
              const allBullets = [
                '🔧 Setting up HTML structure',
                '🎨 Adding CSS styling and animations', 
                '⚡ Implementing game logic',
                '🎮 Setting up event handlers',
                '✨ Adding interactive features',
                '🚀 Optimizing performance'
              ];
              
              if (codeContent.includes('style') || codeContent.includes('css') || codeContent.includes('color:')) {
                if (!newBuildingBullets.includes(allBullets[1])) {
                  newBuildingBullets.push(allBullets[1]);
                }
              }
              
              if (codeContent.includes('function') || codeContent.includes('const ') || codeContent.includes('let ')) {
                if (!newBuildingBullets.includes(allBullets[2])) {
                  newBuildingBullets.push(allBullets[2]);
                }
              }
              
              if (codeContent.includes('addEventListener') || codeContent.includes('keydown') || codeContent.includes('click')) {
                if (!newBuildingBullets.includes(allBullets[3])) {
                  newBuildingBullets.push(allBullets[3]);
                }
              }
              
              // Determine code type for syntax highlighting
              let codeType: 'html' | 'css' | 'js' = 'html';
              if (codeContent.includes('function') || codeContent.includes('const ') || codeContent.includes('addEventListener')) {
                codeType = 'js';
              } else if (codeContent.includes('color:') || codeContent.includes('background:') || codeContent.includes('font-')) {
                codeType = 'css';
              }

              // Clear previous content if this is the first chunk of a new generation
              const isFirstChunk = !prev.codeStream.isStreaming;
              
              return {
                ...prev,
                statusBox: {
                  ...prev.statusBox,
                  phase: 'generating',
                  tip: 'Writing your game code...'
                },
                buildingStatus: {
                  bullets: newBuildingBullets,
                  isBuilding: true
                },
                codeStream: {
                  content: isFirstChunk ? codeContent : prev.codeStream.content + codeContent,
                  currentType: codeType,
                  isStreaming: true
                }
              };
            });
          }
          break;

        case 'command':
          // Extract command info for status tips
          if (typeof event.payload === 'string' && event.payload.includes('<')) {
            const commandMatch = event.payload.match(/<(\w+)>([^<]+)</);
            if (commandMatch) {
              setGameState(prev => ({
                ...prev,
                statusBox: {
                  ...prev.statusBox,
                  tip: commandMatch[2]
                }
              }));
            }
          }
          // Forward to chat interface if handler provided
          if (onChatEvent) {
            onChatEvent(event);
          }
          break;

        case 'code':
          setGameState(prev => ({
            ...prev,
            code: event.payload as GameCode,
            isGenerating: false,
            status: 'completed',
            statusBox: {
              phase: 'suggesting',
              bullets: [
                'Game generated successfully!',
                'Ready for testing and modifications',
                'Try asking for specific changes'
              ],
              tip: 'Your game is ready to play! What would you like to modify?'
            },
            buildingStatus: {
              bullets: [
                '✅ HTML structure created',
                '✅ CSS styling applied', 
                '✅ JavaScript logic implemented',
                '✅ Game mechanics configured',
                '✅ Interactive features added',
                '🎮 Game ready to play!'
              ],
              isBuilding: false // Keep false but show completion bullets
            },
            codeStream: {
              content: prev.codeStream.content, // Keep the streamed content visible
              currentType: prev.codeStream.currentType,
              isStreaming: false
            }
          }));
          break;

        case 'error':
          setGameState(prev => ({
            ...prev,
            isGenerating: false,
            status: 'error',
            error: event.payload,
            statusBox: {
              phase: 'idle',
              bullets: [],
              tip: undefined
            },
            buildingStatus: {
              bullets: [],
              isBuilding: false
            },
            codeStream: {
              content: '',
              currentType: 'html',
              isStreaming: false
            },
            suggestions: []
          }));
          // Forward error to chat too
          if (onChatEvent) {
            onChatEvent(event);
          }
          break;
      }
    };

    try {
      await mayaAPI.generateGame(
        { 
          prompt,
          session_id: sessionId,
          user_id: 'maya_user' 
        },
        handleEvent,
        useRealAgent
      );
    } catch (error) {
      setGameState(prev => ({
        ...prev,
        isGenerating: false,
        status: 'error',
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        suggestions: []
      }));
    }
  };

  const cancelGeneration = () => {
    mayaAPI.cancelRequest();
    setGameState(prev => ({
      ...prev,
      isGenerating: false,
      status: 'idle',
      statusBox: {
        phase: 'idle',
        bullets: [],
        tip: undefined
      },
      buildingStatus: {
        bullets: [],
        isBuilding: false
      },
      codeStream: {
        content: '',
        currentType: 'html',
        isStreaming: false
      },
      suggestions: []
    }));
  };

  const updateStatusBox = (update: Partial<StatusBoxState>) => {
    setGameState(prev => ({
      ...prev,
      statusBox: {
        ...prev.statusBox,
        ...update
      }
    }));
  };

  const clearGame = () => {
    setGameState({
      code: null,
      isGenerating: false,
      status: 'idle',
      error: null,
      statusBox: {
        phase: 'idle',
        bullets: [],
        tip: undefined
      },
      buildingStatus: {
        bullets: [],
        isBuilding: false
      },
      codeStream: {
        content: '',
        currentType: 'html',
        isStreaming: false
      },
      suggestions: [],
      publisher: {
        status: 'idle',
        isPublishing: false
      },
      operationType: 'idle'
    });
  };

  return (
    <GameContext.Provider value={{
      gameState,
      generateGame,
      cancelGeneration,
      clearGame,
      updateStatusBox,
    }}>
      {children}
    </GameContext.Provider>
  );
}

export function useGame() {
  const context = useContext(GameContext);
  if (context === undefined) {
    throw new Error('useGame must be used within a GameProvider');
  }
  return context;
}