import React from 'react';

export interface FormattedTextProps {
  children: string;
  className?: string;
}

export function FormattedText({ children, className = '' }: FormattedTextProps) {
  const formatText = (text: string) => {
    // Split text into lines for processing
    const lines = text.split('\n');
    const elements: React.ReactNode[] = [];
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      
      // Skip empty lines but preserve spacing
      if (line.trim() === '') {
        if (i < lines.length - 1) {
          elements.push(<br key={`br-${i}`} />);
        }
        continue;
      }
      
      // Bullet points (- or *)
      if (line.match(/^\s*[-*]\s+/)) {
        const content = line.replace(/^\s*[-*]\s+/, '');
        const formattedContent = formatInlineStyles(content);
        elements.push(
          <div key={i} className="flex items-start gap-2 mb-2">
            <span className="text-primary mt-1 text-sm">•</span>
            <span className="text-sm leading-relaxed">{formattedContent}</span>
          </div>
        );
      }
      // Headers (##)
      else if (line.match(/^##\s+/)) {
        const content = line.replace(/^##\s+/, '');
        elements.push(
          <h3 key={i} className="text-lg font-semibold text-primary mt-4 mb-2">
            {content}
          </h3>
        );
      }
      // Regular paragraphs
      else {
        const formattedContent = formatInlineStyles(line);
        elements.push(
          <p key={i} className="text-sm leading-relaxed mb-2">
            {formattedContent}
          </p>
        );
      }
    }
    
    return elements;
  };
  
  const formatInlineStyles = (text: string): React.ReactNode[] => {
    const parts: React.ReactNode[] = [];
    let currentIndex = 0;
    
    // Bold text (**text**)
    const boldRegex = /\*\*(.*?)\*\*/g;
    let match;
    
    while ((match = boldRegex.exec(text)) !== null) {
      // Add text before the match
      if (match.index > currentIndex) {
        parts.push(text.slice(currentIndex, match.index));
      }
      
      // Add the bold text
      parts.push(
        <strong key={`bold-${match.index}`} className="font-semibold text-foreground">
          {match[1]}
        </strong>
      );
      
      currentIndex = match.index + match[0].length;
    }
    
    // Add remaining text
    if (currentIndex < text.length) {
      parts.push(text.slice(currentIndex));
    }
    
    return parts.length > 0 ? parts : [text];
  };
  
  return (
    <div className={`formatted-text ${className}`}>
      {formatText(children)}
    </div>
  );
}

// Utility function for simple text formatting without React components
export function formatTextSimple(text: string): string {
  return text
    .replace(/^\s*[-*]\s+/gm, '• ') // Convert - or * to bullets
    .replace(/\*\*(.*?)\*\*/g, '$1'); // Remove markdown bold markers for plain text
}