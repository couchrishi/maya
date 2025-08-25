import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Lightbulb, Gamepad2, Palette, Zap } from 'lucide-react';

interface SuggestionCardsProps {
  suggestions?: string[];
  onSuggestionClick: (suggestion: string) => void;
  className?: string;
}

const defaultSuggestions = [
  "Add sound effects and background music",
  "Change the visual theme to retro/neon",
  "Increase difficulty with more enemies",
  "Add power-ups and special abilities",
  "Create a multiplayer version",
  "Add particle effects and animations"
];

const suggestionIcons = [Zap, Palette, Gamepad2, Lightbulb, Gamepad2, Zap];

export function SuggestionCards({ 
  suggestions = defaultSuggestions, 
  onSuggestionClick, 
  className = '' 
}: SuggestionCardsProps) {
  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <Lightbulb className="w-3 h-3 text-yellow-500" />
        <span>Try asking for:</span>
      </div>
      
      <div className="flex flex-wrap gap-2">
        {suggestions.slice(0, 6).map((suggestion, index) => (
          <Button
            key={index}
            variant="outline"
            size="sm"
            className="h-7 px-3 text-xs bg-card/50 border-primary/20 hover:border-primary/50 hover:bg-primary/10 transition-all duration-200"
            onClick={() => onSuggestionClick(suggestion)}
          >
            {suggestion}
          </Button>
        ))}
      </div>
    </div>
  );
}