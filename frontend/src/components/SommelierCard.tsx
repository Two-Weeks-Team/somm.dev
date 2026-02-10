'use client';

import React, { useState } from 'react';
import Image from 'next/image';
import { ChevronDown, ChevronUp, Lightbulb, CheckCircle2, XCircle, MinusCircle } from 'lucide-react';
import { getSommelierTheme } from '../lib/sommeliers';
import { TechniqueDetail } from '../types';

interface SommelierCardProps {
  id: string;
  name: string;
  role: string;
  score: number;
  feedback: string;
  recommendations?: string[];
  pairingSuggestion?: string;
  techniqueDetails?: TechniqueDetail[];
  delay?: number;
}

// Format feedback: split into paragraphs
// Uses stable keys based on content hash to prevent React DOM reconciliation errors
function formatFeedback(text: string): React.ReactNode {
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
  
  // Wrap in a single container to avoid DOM reconciliation issues when toggling expansion
  // This prevents the "insertBefore" error caused by React trying to reconcile
  // multiple paragraph elements when the parent's className changes
  return (
    <div className="space-y-3">
      {paragraphs.map((p, idx) => (
        <p key={`feedback-${idx}-${p.slice(0, 20).replace(/\s/g, '')}`}>{p}</p>
      ))}
    </div>
  );
}

export function SommelierCard({
  id,
  score,
  feedback,
  recommendations,
  pairingSuggestion,
  techniqueDetails,
  delay = 0,
}: SommelierCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showTechniques, setShowTechniques] = useState(false);
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
        <div 
          className={`text-gray-700 leading-relaxed transition-[max-height] duration-300 ease-in-out overflow-hidden ${
            isExpanded ? 'max-h-[2000px]' : 'max-h-36'
          }`}
        >
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

      {/* Technique Details - Expandable */}
      {techniqueDetails && techniqueDetails.length > 0 && (
        <div className="border-t border-gray-100">
          <button
            onClick={() => setShowTechniques(!showTechniques)}
            className="w-full px-5 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
          >
            <span className="text-xs font-bold uppercase tracking-wider text-gray-500">
              Technique Details ({techniqueDetails.length})
            </span>
            {showTechniques ? (
              <ChevronUp size={16} className="text-gray-400" />
            ) : (
              <ChevronDown size={16} className="text-gray-400" />
            )}
          </button>

          {showTechniques && (
            <div className="px-5 pb-4 space-y-2 max-h-64 overflow-y-auto">
              {techniqueDetails.map((tech) => (
                <div
                  key={tech.id}
                  className="flex items-center gap-2 py-1.5 px-2 rounded-lg bg-gray-50"
                >
                  {tech.status === 'success' && (
                    <CheckCircle2 size={14} className="text-green-500 flex-shrink-0" />
                  )}
                  {tech.status === 'failed' && (
                    <XCircle size={14} className="text-red-500 flex-shrink-0" />
                  )}
                  {tech.status === 'skipped' && (
                    <MinusCircle size={14} className="text-gray-400 flex-shrink-0" />
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-gray-700 truncate">
                      {tech.name}
                    </p>
                    {tech.error && (
                      <p className="text-xs text-red-500 truncate">{tech.error}</p>
                    )}
                  </div>
                  {tech.score !== undefined && tech.maxScore !== undefined && (
                    <span className="text-xs text-gray-500 flex-shrink-0">
                      {tech.score}/{tech.maxScore}
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
