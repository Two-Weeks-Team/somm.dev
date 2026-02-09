import React, { useState } from 'react';
import { ChevronDown, ChevronUp, CheckCircle2, AlertCircle, HelpCircle, Search } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ItemData } from '@/types';

interface ItemTileProps {
  item: ItemData;
}

export function ItemTile({ item }: ItemTileProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const getConfidenceColor = (confidence: string) => {
    const c = confidence.toLowerCase();
    if (c === 'high') return 'text-green-600 bg-green-50 border-green-200';
    if (c === 'medium') return 'text-amber-600 bg-amber-50 border-amber-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  const getScoreColor = (score: number, max: number) => {
    const ratio = score / max;
    if (ratio >= 0.8) return 'text-green-700';
    if (ratio >= 0.5) return 'text-amber-700';
    return 'text-red-700';
  };

  const confidenceStyle = getConfidenceColor(item.confidence);
  const scoreStyle = getScoreColor(item.score, item.maxScore);

  return (
    <div 
      className={cn(
        "border rounded-lg transition-all duration-200 overflow-hidden bg-white hover:shadow-md",
        isExpanded ? "ring-2 ring-[#722F37]/20 border-[#722F37]/30" : "border-gray-200"
      )}
    >
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-3 text-left"
      >
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center font-bold text-gray-600 text-xs">
            {item.id}
          </div>
          <div className="min-w-0 flex-1">
            <h4 className="font-medium text-gray-900 text-sm truncate pr-2" title={item.name}>
              {item.name}
            </h4>
          </div>
        </div>

        <div className="flex items-center gap-3 flex-shrink-0">
          <div className={cn("text-sm font-bold", scoreStyle)}>
            {item.score}<span className="text-gray-400 text-xs font-normal">/{item.maxScore}</span>
          </div>
          {isExpanded ? <ChevronUp size={16} className="text-gray-400" /> : <ChevronDown size={16} className="text-gray-400" />}
        </div>
      </button>

      {isExpanded && (
        <div className="px-3 pb-3 pt-0 border-t border-gray-100 bg-gray-50/50">
          <div className="mt-3 flex items-center gap-2 mb-3">
            <span className={cn("text-[10px] uppercase font-bold px-2 py-0.5 rounded-full border", confidenceStyle)}>
              {item.confidence} Confidence
            </span>
          </div>

          {item.rationale && (
            <div className="mb-3 text-xs text-gray-600 leading-relaxed">
              <span className="font-semibold text-gray-900 block mb-1">Rationale:</span>
              {item.rationale}
            </div>
          )}

          {item.evidence && item.evidence.length > 0 && (
            <div className="space-y-1">
              <span className="font-semibold text-gray-900 text-xs block mb-1 flex items-center gap-1">
                <Search size={12} /> Evidence:
              </span>
              <ul className="space-y-1">
                {item.evidence.map((ev, idx) => (
                  <li key={idx} className="text-xs text-gray-500 pl-3 border-l-2 border-gray-200 py-0.5">
                    {ev}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
