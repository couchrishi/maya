import { Header } from "@/components/layout/Header";
import { ChatInterface } from "@/components/chat/ChatInterface";
import { GamePanel } from "@/components/panels/GamePanel";

const Index = () => {
  return (
    <div className="h-screen bg-background flex flex-col overflow-hidden">
      <Header />
      
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Chat Interface */}
        <div className="w-1/2 border-r border-border/50 bg-card/20 backdrop-blur">
          <ChatInterface />
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
  );
};

export default Index;
