'use client';

import React from 'react';
import { cn } from '@/lib/utils';

type ScoreTier = 'grand_cru' | 'premier_cru' | 'village' | 'table_wine';

interface ScoreCircleProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showTier?: boolean;
}

const sizeClasses = {
  sm: 'w-24 h-24',
  md: 'w-32 h-32',
  lg: 'w-40 h-40',
};

const textSizeClasses = {
  sm: 'text-2xl',
  md: 'text-3xl',
  lg: 'text-4xl',
};

function getScoreTier(score: number): ScoreTier {
  if (score >= 90) return 'grand_cru';
  if (score >= 80) return 'premier_cru';
  if (score >= 70) return 'village';
  return 'table_wine';
}

const tierConfig: Record<ScoreTier, {
  label: string;
  stroke: string;
  text: string;
  bg: string;
  glow: string;
}> = {
  grand_cru: {
    label: 'Grand Cru',
    stroke: 'stroke-[#722F37]',
    text: 'text-[#722F37]',
    bg: 'bg-[#722F37]/20',
    glow: 'shadow-[0_0_60px_rgba(114,47,55,0.4)]',
  },
  premier_cru: {
    label: 'Premier Cru',
    stroke: 'stroke-emerald-500',
    text: 'text-emerald-600',
    bg: 'bg-emerald-500/20',
    glow: 'shadow-[0_0_60px_rgba(16,185,129,0.3)]',
  },
  village: {
    label: 'Village',
    stroke: 'stroke-blue-500',
    text: 'text-blue-600',
    bg: 'bg-blue-500/20',
    glow: 'shadow-[0_0_60px_rgba(59,130,246,0.3)]',
  },
  table_wine: {
    label: 'Table Wine',
    stroke: 'stroke-gray-400',
    text: 'text-gray-600',
    bg: 'bg-gray-400/20',
    glow: 'shadow-[0_0_60px_rgba(156,163,175,0.3)]',
  },
};

export function ScoreCircle({ score, size = 'lg', showTier = true }: ScoreCircleProps) {
  const clampedScore = Math.max(0, Math.min(100, score));
  const tier = getScoreTier(clampedScore);
  const config = tierConfig[tier];
  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (clampedScore / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-3">
      <div 
        className={cn(
          'relative rounded-full transition-all duration-500',
          sizeClasses[size],
          config.glow
        )}
        data-testid="score-circle"
      >
        <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            className="text-gray-200"
          />
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            className={cn('transition-all duration-1000 ease-out', config.stroke)}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={cn('font-bold text-gray-900', textSizeClasses[size])}>
            {score}
          </span>
          <span className="text-xs text-gray-500">/100</span>
        </div>
      </div>
      
      {showTier && (
        <div
          className={cn(
            'px-3 py-1 rounded-full text-sm font-medium',
            config.bg,
            config.text
          )}
          data-testid="score-tier"
        >
          {config.label}
        </div>
      )}
    </div>
  );
}
