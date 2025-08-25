import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent } from "@/components/ui/card";
import { Zap, Gamepad2, Sparkles, ArrowRight, Play } from "lucide-react";

export default function Home() {
  const [prompt, setPrompt] = useState('');
  const navigate = useNavigate();

  const templates = [
    {
      title: "Voxel Forest",
      description: "Adventure games with blocky 3D worlds",
      icon: "🌲",
      prompt: "Create a voxel forest adventure game where players explore and collect items"
    },
    {
      title: "Aliens Platformer",
      description: "2D platformer with alien characters",
      icon: "👽",
      prompt: "Create a 2D platformer game with alien characters and space themed levels"
    },
    {
      title: "Create from Scratch",
      description: "Build your unique game concept",
      icon: "✨",
      prompt: "I want to create a unique game with custom mechanics"
    }
  ];

  const handleStart = (gamePrompt?: string) => {
    const finalPrompt = gamePrompt || prompt;
    if (finalPrompt.trim()) {
      // Navigate to chat interface with the prompt
      navigate('/create', { state: { initialPrompt: finalPrompt } });
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col overflow-hidden relative">
      {/* Background Effects */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute inset-0 opacity-5 cyber-grid"></div>
        <div className="absolute inset-0 scan-lines"></div>
      </div>

      {/* Header */}
      <header className="p-6 border-b border-border/50 bg-card/20 backdrop-blur relative z-10">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-primary to-secondary rounded-lg flex items-center justify-center">
              <Gamepad2 className="w-6 h-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-orbitron font-bold text-primary neon-pulse">
                MAYA AI
              </h1>
              <p className="text-xs text-muted-foreground">Game Creation Engine</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <Button variant="outline" className="border-primary/30 hover:border-primary/50">
              <Play className="w-4 h-4 mr-2" />
              Browse Games
            </Button>
            <Button className="bg-gradient-to-r from-primary to-secondary hover:from-primary/80 hover:to-secondary/80">
              <Zap className="w-4 h-4 mr-2" />
              Upgrade
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center p-6 relative z-10">
        <div className="max-w-6xl mx-auto w-full">
          <div className="text-center mb-12">
            <h1 className="text-6xl font-orbitron font-black text-transparent bg-clip-text bg-gradient-to-r from-primary via-secondary to-accent mb-4 neon-pulse">
              CREATE WITH MAYA AI
            </h1>
            <p className="text-xl text-muted-foreground font-rajdhani">
              Vibe Code Games
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-6 mb-12">
            {/* Main Creation Area */}
            <div className="lg:col-span-2">
              <Card className="bg-card/50 border-primary/30 backdrop-blur cyber-grid">
                <CardContent className="p-6">
                  <div className="mb-4">
                    <h3 className="text-lg font-orbitron font-bold text-primary mb-2 flex items-center">
                      <Sparkles className="w-5 h-5 mr-2" />
                      Describe Your Game
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      Tell Maya what kind of game you want to create. Be as detailed or simple as you like.
                    </p>
                  </div>
                  
                  <Textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Make the forest have horror vibes. The player should have a bright flashlight..."
                    className="min-h-[120px] bg-background/50 border-primary/30 focus:border-primary/50 resize-none text-base"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                        e.preventDefault();
                        handleStart();
                      }
                    }}
                  />
                  
                  <div className="flex items-center justify-between mt-4">
                    <div className="text-xs text-muted-foreground">
                      Ctrl+Enter to start creating
                    </div>
                    <Button
                      onClick={() => handleStart()}
                      disabled={!prompt.trim()}
                      className="bg-gradient-to-r from-primary to-secondary hover:from-primary/80 hover:to-secondary/80 shadow-[var(--shadow-cyber)]"
                    >
                      Start Creating
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Template Sidebar */}
            <div className="space-y-4">
              <h3 className="text-lg font-orbitron font-bold text-secondary">
                Quick Start Templates
              </h3>
              
              {templates.map((template, index) => (
                <Card 
                  key={index}
                  className="bg-card/30 border-secondary/30 backdrop-blur hover:border-secondary/50 transition-all cursor-pointer group"
                  onClick={() => handleStart(template.prompt)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start space-x-3">
                      <div className="text-2xl">{template.icon}</div>
                      <div className="flex-1 min-w-0">
                        <h4 className="font-orbitron font-semibold text-secondary group-hover:text-secondary/80 transition-colors">
                          {template.title}
                        </h4>
                        <p className="text-xs text-muted-foreground mt-1">
                          {template.description}
                        </p>
                      </div>
                      <ArrowRight className="w-4 h-4 text-secondary/50 group-hover:text-secondary transition-colors" />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Bottom CTA */}
          <div className="text-center">
            <p className="text-sm text-muted-foreground mb-4">
              Powered by advanced AI • Create games in minutes, not months
            </p>
            <div className="flex items-center justify-center space-x-6 text-xs text-muted-foreground">
              <span>🎮 Any Genre</span>
              <span>•</span>
              <span>⚡ Real-time Code</span>
              <span>•</span>
              <span>🎨 Custom Assets</span>
              <span>•</span>
              <span>📱 Export Ready</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}