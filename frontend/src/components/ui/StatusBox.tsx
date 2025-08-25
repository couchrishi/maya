import React from 'react';
import { Loader2, CheckCircle, AlertCircle, Lightbulb } from 'lucide-react';

export interface StatusBoxProps {
  phase: 'analyzing' | 'thinking' | 'outlining' | 'generating' | 'previewing' | 'completed' | 'suggesting' | 'idle';
  bullets?: string[];
  tip?: string;
  className?: string;
}

const phaseConfig = {
  analyzing: {
    icon: Loader2,
    title: 'Analyzing...',
    color: 'text-blue-500',
    bgColor: 'bg-blue-50 border-blue-200',
    description: 'Understanding your request and current context'
  },
  thinking: {
    icon: Loader2,
    title: 'Thinking...',
    color: 'text-purple-500',
    bgColor: 'bg-purple-50 border-purple-200',
    description: 'Planning the best approach for your game'
  },
  outlining: {
    icon: Loader2,
    title: 'Outlining the game...',
    color: 'text-indigo-500',
    bgColor: 'bg-indigo-50 border-indigo-200',
    description: 'Designing the game concept and structure'
  },
  generating: {
    icon: Loader2,
    title: 'Generating code...',
    color: 'text-green-500',
    bgColor: 'bg-green-50 border-green-200',
    description: 'Writing the game code and logic'
  },
  previewing: {
    icon: Loader2,
    title: 'Previewing the game...',
    color: 'text-orange-500',
    bgColor: 'bg-orange-50 border-orange-200',
    description: 'Preparing the game for testing'
  },
  completed: {
    icon: CheckCircle,
    title: 'Completed!',
    color: 'text-emerald-500',
    bgColor: 'bg-emerald-50 border-emerald-200',
    description: 'Your game is ready to play!'
  },
  suggesting: {
    icon: Lightbulb,
    title: 'Here are some suggestions',
    color: 'text-yellow-500',
    bgColor: 'bg-yellow-50 border-yellow-200',
    description: 'What would you like to try next?'
  },
  idle: {
    icon: CheckCircle,
    title: 'Ready',
    color: 'text-gray-500',
    bgColor: 'bg-gray-50 border-gray-200',
    description: 'Waiting for your next request'
  }
};

export function StatusBox({ phase, bullets = [], tip, className = '' }: StatusBoxProps) {
  const config = phaseConfig[phase];
  const Icon = config.icon;
  const isAnimated = ['analyzing', 'thinking', 'outlining', 'generating', 'previewing'].includes(phase);

  if (phase === 'idle' && bullets.length === 0 && !tip) {
    return null;
  }

  return (
    <div className={`rounded-lg border p-4 transition-all duration-300 ${config.bgColor} ${className}`}>
      <div className="flex items-start gap-3">
        <div className={`flex-shrink-0 ${config.color}`}>
          <Icon 
            className={`h-5 w-5 ${isAnimated ? 'animate-spin' : ''}`}
          />
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className={`text-sm font-medium ${config.color}`}>
              {config.title}
            </h3>
          </div>
          
          <p className="text-xs text-gray-600 mb-3">
            {config.description}
          </p>

          {bullets.length > 0 && (
            <ul className="space-y-1 mb-3">
              {bullets.map((bullet, index) => (
                <li 
                  key={index}
                  className="text-xs text-gray-700 flex items-start gap-1.5 animate-in slide-in-from-left duration-300"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <span className="text-gray-400 text-[10px] mt-0.5">•</span>
                  <span>{bullet}</span>
                </li>
              ))}
            </ul>
          )}

          {tip && (
            <div className="bg-white/50 rounded px-2 py-1 animate-in fade-in duration-500">
              <p className="text-xs text-gray-600 italic">
                💡 {tip}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}