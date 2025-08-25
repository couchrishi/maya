import React from 'react';
import { Loader2, Code, Palette, Zap } from 'lucide-react';

interface BuildingStatusProps {
  bullets: string[];
  className?: string;
  isCompleted?: boolean;
}

export function BuildingStatus({ bullets, className = '', isCompleted = false }: BuildingStatusProps) {
  if (bullets.length === 0) return null;

  // Check if bullets contain completion indicators (✅ or 🎮)
  const hasCompletionBullets = bullets.some(bullet => bullet.includes('✅') || bullet.includes('🎮'));
  const showAsCompleted = isCompleted || hasCompletionBullets;

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex items-center gap-2 text-sm text-primary">
        {showAsCompleted ? (
          <Zap className="w-4 h-4 text-green-500" />
        ) : (
          <Loader2 className="w-4 h-4 animate-spin" />
        )}
        <span className="font-medium">
          {showAsCompleted ? 'Game completed!' : 'Building your game...'}
        </span>
      </div>
      
      <ul className="space-y-1 ml-6">
        {bullets.map((bullet, index) => (
          <li 
            key={index}
            className="text-sm text-muted-foreground flex items-start gap-2 animate-in slide-in-from-left duration-300"
            style={{ animationDelay: `${index * 150}ms` }}
          >
            {showAsCompleted ? (
              <span className="text-xs mt-1"></span>
            ) : (
              <span className="text-primary text-xs mt-1">•</span>
            )}
            <span>{bullet}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}