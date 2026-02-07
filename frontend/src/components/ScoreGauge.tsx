'use client';

import React from 'react';
import { getScoreTier } from '../lib/sommeliers';

interface ScoreGaugeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  animate?: boolean;
}

export function ScoreGauge({ score, size = 'md', showLabel = true, animate = true }: ScoreGaugeProps) {
  const tier = getScoreTier(score);
  
  const sizeConfig = {
    sm: { width: 80, strokeWidth: 6, fontSize: 'text-lg' },
    md: { width: 120, strokeWidth: 8, fontSize: 'text-3xl' },
    lg: { width: 180, strokeWidth: 10, fontSize: 'text-5xl' },
  };
  
  const config = sizeConfig[size];
  const radius = (config.width - config.strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = (score / 100) * circumference;
  
  // Color based on score
  const getStrokeColor = (score: number) => {
    if (score >= 90) return '#722F37'; // Burgundy - Grand Cru
    if (score >= 80) return '#16a34a'; // Green - Premier Cru
    if (score >= 70) return '#2563eb'; // Blue - Village
    if (score >= 60) return '#9333ea'; // Purple - House Wine
    return '#dc2626'; // Red - Corked
  };

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: config.width, height: config.width }}>
        <svg
          width={config.width}
          height={config.width}
          className="transform -rotate-90"
        >
          {/* Background circle */}
          <circle
            cx={config.width / 2}
            cy={config.width / 2}
            r={radius}
            fill="none"
            stroke="#e5e7eb"
            strokeWidth={config.strokeWidth}
          />
          {/* Progress circle */}
          <circle
            cx={config.width / 2}
            cy={config.width / 2}
            r={radius}
            fill="none"
            stroke={getStrokeColor(score)}
            strokeWidth={config.strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={circumference - progress}
            className={animate ? 'transition-all duration-1000 ease-out' : ''}
            style={{
              filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))',
            }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`font-bold ${config.fontSize} text-gray-900`}>
            {score}
          </span>
          {size !== 'sm' && (
            <span className="text-xs text-gray-500 font-medium">/100</span>
          )}
        </div>
      </div>
      {showLabel && (
        <div className={`mt-2 flex items-center gap-1 px-3 py-1 rounded-full ${tier.bgColor}`}>
          <span>{tier.emoji}</span>
          <span className={`text-sm font-semibold ${tier.color}`}>{tier.name}</span>
        </div>
      )}
    </div>
  );
}
