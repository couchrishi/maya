import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Zap, Settings, Share, User, Menu } from "lucide-react";

export function Header() {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="h-16 bg-card/80 backdrop-blur border-b border-border/50 px-6 flex items-center justify-between relative scan-lines">
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary to-secondary shadow-[var(--shadow-cyber)] flex items-center justify-center overflow-hidden">
            <span className="text-background font-orbitron font-black text-sm">M</span>
          </div>
          <div>
            <h1 
              className="text-2xl font-orbitron font-black text-primary neon-pulse glitch" 
              data-text="MAYA"
            >
              MAYA
            </h1>
            <p className="text-xs text-muted-foreground -mt-1">
              AI Game Creator
            </p>
          </div>
        </div>
        
        <Badge 
          variant="outline" 
          className="bg-primary/10 border-primary/30 text-primary text-xs font-mono"
        >
          v2.0.77
        </Badge>
      </div>

      <div className="flex items-center space-x-4">
        <div className="hidden md:flex items-center space-x-6 text-sm">
          <div className="text-center">
            <div className="text-primary font-mono">
              {currentTime.toLocaleTimeString()}
            </div>
            <div className="text-xs text-muted-foreground">
              SYSTEM TIME
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-secondary font-mono">
              ONLINE
            </div>
            <div className="text-xs text-muted-foreground">
              STATUS
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <Button 
            size="sm" 
            variant="outline" 
            className="border-accent/30 hover:border-accent/50 hover:bg-accent/10"
          >
            <Share className="w-4 h-4 mr-2" />
            Share
          </Button>
          
          <Button 
            size="sm" 
            variant="outline" 
            className="border-secondary/30 hover:border-secondary/50 hover:bg-secondary/10"
          >
            <Settings className="w-4 h-4" />
          </Button>
          
          <Button 
            size="sm" 
            className="bg-gradient-to-r from-primary to-secondary hover:from-primary/80 hover:to-secondary/80 shadow-[var(--shadow-cyber)]"
          >
            <Zap className="w-4 h-4 mr-2" />
            Upgrade
          </Button>
        </div>

        <Button 
          size="sm" 
          variant="ghost" 
          className="md:hidden"
        >
          <Menu className="w-4 h-4" />
        </Button>
      </div>

      {/* Cyberpunk grid overlay */}
      <div className="absolute inset-0 pointer-events-none opacity-10 cyber-grid"></div>
    </header>
  );
}