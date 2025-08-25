import React from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Code, FileText, Palette } from 'lucide-react';

interface CodeStreamBoxProps {
  codeContent: string;
  currentType?: 'html' | 'css' | 'js';
  className?: string;
}

const typeIcons = {
  html: FileText,
  css: Palette,
  js: Code
};

const typeLabels = {
  html: 'HTML Structure',
  css: 'CSS Styling', 
  js: 'JavaScript Logic'
};

export function CodeStreamBox({ codeContent, currentType = 'html', className = '' }: CodeStreamBoxProps) {
  if (!codeContent.trim()) return null;

  const Icon = typeIcons[currentType];

  // Simplified code formatting to avoid nested span issues
  const formatCode = (code: string, type: 'html' | 'css' | 'js') => {
    // Just escape HTML and show as plain text for now - no syntax highlighting
    // This prevents the broken nested spans issue
    return code
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;');
  };

  const formattedContent = formatCode(codeContent, currentType);

  return (
    <Card className={`bg-card/80 backdrop-blur border-primary/20 w-full ${className}`}>
      <CardHeader className="pb-1 px-3 py-2">
        <div className="flex items-center gap-2">
          <Icon className="w-3 h-3 text-primary" />
          <span className="text-xs font-medium text-primary">
            {typeLabels[currentType]}
          </span>
          <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div>
        </div>
      </CardHeader>
      <CardContent className="pt-0 px-3 pb-2">
        <div className="relative">
          <div className="h-48 overflow-y-auto rounded border" style={{ backgroundColor: '#1a1a1a', borderColor: '#333' }}>
            <pre 
              className="text-xs font-mono p-4 whitespace-pre-wrap leading-relaxed m-0"
              style={{ 
                backgroundColor: '#1a1a1a',
                color: '#e5e5e5',
                fontFamily: '"SF Mono", "Monaco", "Inconsolata", "Roboto Mono", "Source Code Pro", monospace',
                lineHeight: '1.4'
              }}
            >
              <code 
                dangerouslySetInnerHTML={{ __html: formattedContent }}
                style={{ fontSize: 'inherit', fontFamily: 'inherit' }}
              />
            </pre>
          </div>
          <div className="absolute bottom-1 right-1">
            <div className="text-[8px] text-green-400 animate-pulse">●</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}