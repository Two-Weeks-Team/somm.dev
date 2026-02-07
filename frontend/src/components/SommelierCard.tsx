'use client';

import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Lightbulb } from 'lucide-react';
import { getSommelierTheme } from '../lib/sommeliers';
import { ScoreGauge } from './ScoreGauge';

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

export function SommelierCard({
  id,
  name,
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
      className={`
        bg-white rounded-xl shadow-sm border-2 overflow-hidden
        hover:shadow-lg transition-all duration-300 ease-out
        animate-fadeIn
      `}
      style={{
        borderColor: theme.color,
        animationDelay: `${delay}ms`,
      }}
    >
      {/* Header with sommelier identity */}
      <div
        className="px-5 py-4 flex items-center gap-4"
        style={{ backgroundColor: `${theme.color}10` }}
      >
        <div
          className="w-12 h-12 rounded-full flex items-center justify-center text-2xl shadow-md"
          style={{ backgroundColor: theme.color }}
        >
          {theme.emoji}
        </div>
        <div className="flex-1">
          <h3 className="font-bold text-lg" style={{ color: theme.color }}>
            {theme.name}
          </h3>
          <p className="text-sm text-gray-600">{theme.description}</p>
        </div>
        <ScoreGauge score={score} size="sm" showLabel={false} />
      </div>

      {/* Feedback content */}
      <div className="px-5 py-4">
        <p className={`text-gray-700 leading-relaxed ${isExpanded ? '' : 'line-clamp-3'}`}>
          {feedback}
        </p>
        
        {feedback.length > 200 && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="mt-2 text-sm font-medium flex items-center gap-1 hover:opacity-80 transition-opacity"
            style={{ color: theme.color }}
          >
            {isExpanded ? (
              <>
                <ChevronUp size={16} />
                Show less
              </>
            ) : (
              <>
                <ChevronDown size={16} />
                Read more
              </>
            )}
          </button>
        )}
      </div>

      {/* Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <div className="px-5 py-3 border-t border-gray-100" style={{ backgroundColor: `${theme.color}05` }}>
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
