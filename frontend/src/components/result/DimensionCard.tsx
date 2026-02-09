import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { cn } from '@/lib/utils';
import { DimensionData } from '@/types';
import { ItemTile } from './ItemTile';

interface DimensionCardProps {
  dimension: DimensionData;
  className?: string;
}

export function DimensionCard({ dimension, className }: DimensionCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const percentage = dimension.maxScore > 0
    ? Math.round((dimension.score / dimension.maxScore) * 100)
    : 0;

  const getProgressColor = (percent: number) => {
    if (percent >= 80) return 'bg-green-500';
    if (percent >= 60) return 'bg-amber-500';
    return 'bg-red-500';
  };

  return (
    <div className={cn("bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden", className)}>
      <div className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-[#722F37]/10 flex items-center justify-center text-[#722F37] font-bold">
              {dimension.id}
            </div>
            <div>
              <h3 className="font-bold text-gray-900 text-sm">{dimension.name}</h3>
              <p className="text-xs text-gray-500">{dimension.items.length} items</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-lg font-bold text-gray-900">
              {dimension.score}
              <span className="text-sm text-gray-400 font-normal">/{dimension.maxScore}</span>
            </div>
          </div>
        </div>

        <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden mb-4">
          <div 
            className={cn("h-full rounded-full transition-all duration-1000 ease-out", getProgressColor(percentage))}
            style={{ width: `${percentage}%` }}
          />
        </div>

        <button 
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center justify-center gap-1 text-xs font-medium text-gray-500 hover:text-gray-900 py-1 transition-colors"
        >
          {isExpanded ? 'Hide Details' : 'Show Details'}
          {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </button>
      </div>

      {isExpanded && (
        <div className="bg-gray-50 border-t border-gray-100 p-3 space-y-2">
          {dimension.items.map((item) => (
            <ItemTile key={item.id} item={item} />
          ))}
        </div>
      )}
    </div>
  );
}
