import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { Header } from "@/components/layout/Header";
import { ChatInterface } from "@/components/chat/ChatInterface";
import { GamePanel } from "@/components/panels/GamePanel";
import { GameProvider } from "@/contexts/GameContext";

const Create = () => {
  const location = useLocation();
  const [initialPrompt, setInitialPrompt] = useState<string>('');

  useEffect(() => {
    // Get initial prompt from navigation state
    if (location.state?.initialPrompt) {
      setInitialPrompt(location.state.initialPrompt);
    }
  }, [location.state]);

  return (
    <GameProvider>
      <div className="min-h-screen bg-background flex flex-col">
        <Header />
        
        <div className="flex-1 flex min-h-0">
          {/* Left Panel - Chat Interface */}
          <div className="w-1/2 border-r border-border/50 bg-card/20 backdrop-blur">
            <ChatInterface initialPrompt={initialPrompt} />
          </div>
          
          {/* Right Panel - Game Panel */}
          <div className="w-1/2 bg-card/10 backdrop-blur">
            <GamePanel />
          </div>
        </div>
        
        {/* Background Effects */}
        <div className="fixed inset-0 pointer-events-none">
          <div className="absolute inset-0 opacity-5 cyber-grid"></div>
          <div className="absolute inset-0 scan-lines"></div>
        </div>
      </div>
    </GameProvider>
  );
};

export default Create;