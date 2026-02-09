'use client';

import React, { useState } from 'react';
import Image from 'next/image';
import { ChevronDown, ChevronUp, Lightbulb } from 'lucide-react';
import { getSommelierTheme } from '../lib/sommeliers';

interface SommelierCardProps {
  id: string;
  name: string;
  role: string;
  score: number;
  feedback: string;
  recommendations?: string[];
  pairingSuggestion?: string;
  delay?: number;
}

// Format feedback: split into paragraphs
function formatFeedback(text: string): React.ReactNode[] {
  // Split into sentences - but only at sentence boundaries
  // A sentence ends with .!? followed by space and uppercase letter
  // This avoids breaking "Next.js", "e.g.", "i.e.", etc.
  const sentencePattern = /(?<=[.!?])\s+(?=[A-Z])/;
  const sentences = text.split(sentencePattern).filter(s => s.trim());
  
  // Group into paragraphs (2-3 sentences each)
  const paragraphs: string[] = [];
  let currentParagraph = '';
  
  sentences.forEach((sentence, idx) => {
    currentParagraph += (currentParagraph ? ' ' : '') + sentence.trim();
    // Create new paragraph every 2-3 sentences
    if ((idx + 1) % 2 === 0 || idx === sentences.length - 1) {
      paragraphs.push(currentParagraph.trim());
      currentParagraph = '';
    }
  });
  
  return paragraphs.map((p, idx) => (
    <p key={idx} className={idx > 0 ? 'mt-3' : ''}>{p}</p>
  ));
}

export function SommelierCard({
  id,
  name: _name,
  score,
  feedback,
  recommendations,
  pairingSuggestion,
  delay = 0,
}: SommelierCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const theme = getSommelierTheme(id);

  return (
    <div
      className="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition-all duration-300 animate-fadeIn"
      style={{ animationDelay: `${delay}ms` }}
    >
      {/* Character Header with Image */}
      <div
        className="relative h-32 overflow-hidden"
        style={{ backgroundColor: theme.color }}
      >
        {/* Character Image */}
        <div className="absolute right-0 top-0 h-full w-40">
          <Image
            src={theme.image}
            alt={theme.name}
            fill
            className={`object-cover ${id === 'isabella' ? 'object-[center_15%]' : 'object-top'}`}
            sizes="160px"
          />
          {/* Soft edge blend */}
          <div 
            className="absolute inset-y-0 left-0 w-16"
            style={{ 
              background: `linear-gradient(to right, ${theme.color}, transparent)` 
            }}
          />
        </div>
        
        {/* Name and Score - stacked to avoid overlap with character */}
        <div className="absolute inset-0 z-20 p-4 flex flex-col justify-between">
          <div>
            <h3 className="text-xl font-bold text-white drop-shadow-md">
              {theme.name}
            </h3>
            <p className="text-sm text-white/80">{theme.description}</p>
          </div>
          <div className="bg-white/20 backdrop-blur-sm rounded-lg px-2.5 py-0.5 self-start">
            <span className="text-lg font-bold text-white">{score}</span>
            <span className="text-xs text-white/70">/100</span>
          </div>
        </div>
      </div>

      {/* Feedback content */}
      <div className="p-5">
        <div className={`text-gray-700 leading-relaxed ${isExpanded ? '' : 'line-clamp-6'}`}>
          {formatFeedback(feedback)}
        </div>
        
        {feedback.length > 300 && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="mt-3 text-sm font-medium flex items-center gap-1 hover:opacity-80 transition-opacity"
            style={{ color: theme.color }}
          >
            {isExpanded ? (
              <span className="flex items-center gap-1">
                <ChevronUp size={16} />
                Show less
              </span>
            ) : (
              <span className="flex items-center gap-1">
                <ChevronDown size={16} />
                Read more
              </span>
            )}
          </button>
        )}
      </div>

      {/* Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <div className="px-5 py-3 border-t border-gray-100" style={{ backgroundColor: `${theme.color}08` }}>
          <div className="flex items-center gap-2 mb-2">
            <Lightbulb size={14} style={{ color: theme.color }} />
            <span className="text-xs font-bold uppercase tracking-wider text-gray-500">
              Techniques Applied
            </span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {recommendations.slice(0, 4).map((rec, idx) => (
              <span
                key={idx}
                className="text-xs px-2 py-1 rounded-full font-medium"
                style={{
                  backgroundColor: `${theme.color}15`,
                  color: theme.color,
                }}
              >
                {rec}
              </span>
            ))}
            {recommendations.length > 4 && (
              <span className="text-xs px-2 py-1 text-gray-500">
                +{recommendations.length - 4} more
              </span>
            )}
          </div>
        </div>
      )}

      {/* Pairing suggestion */}
      {pairingSuggestion && (
        <div className="px-5 py-3 border-t border-gray-100 bg-gray-50">
          <p className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-1">
            Pairing Suggestion
          </p>
          <p className="text-sm font-medium" style={{ color: theme.color }}>
            {pairingSuggestion}
          </p>
        </div>
      )}
    </div>
  );
}
