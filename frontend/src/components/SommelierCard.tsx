'use client';

import React, { useState } from 'react';
import Image from 'next/image';
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
      className="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition-all duration-300 animate-fadeIn"
      style={{ animationDelay: `${delay}ms` }}
    >
      {/* Character Header with Image */}
      <div
        className="relative h-32 overflow-hidden"
        style={{ backgroundColor: theme.color }}
      >
        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-black/30 to-transparent z-10" />
        
        {/* Character Image */}
        <div className="absolute right-0 top-0 h-full w-32">
          <Image
            src={theme.image}
            alt={theme.name}
            fill
            className="object-cover object-top"
            sizes="128px"
          />
        </div>
        
        {/* Name and Score */}
        <div className="absolute inset-0 z-20 p-4 flex justify-between items-start">
          <div>
            <h3 className="text-xl font-bold text-white drop-shadow-md">
              {theme.name}
            </h3>
            <p className="text-sm text-white/80">{theme.description}</p>
          </div>
          <div className="bg-white/20 backdrop-blur-sm rounded-xl px-3 py-1">
            <span className="text-2xl font-bold text-white">{score}</span>
            <span className="text-sm text-white/70">/100</span>
          </div>
        </div>
      </div>

      {/* Feedback content */}
      <div className="p-5">
        <p className={`text-gray-700 leading-relaxed ${isExpanded ? '' : 'line-clamp-4'}`}>
          {feedback}
        </p>
        
        {feedback.length > 250 && (
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
