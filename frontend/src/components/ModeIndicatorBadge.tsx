import React from 'react';
import { Wine, Trophy } from 'lucide-react';
import { GraphEvaluationMode } from '@/types/graph';

interface ModeIndicatorBadgeProps {
  mode: GraphEvaluationMode | string;
}

export function ModeIndicatorBadge({ mode }: ModeIndicatorBadgeProps) {
  const isGrandTasting = mode === 'full_techniques';

  if (isGrandTasting) {
    return (
      <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-amber-50 to-yellow-50 border border-amber-200 shadow-sm">
        <div className="p-1.5 bg-amber-100 rounded-full text-amber-700">
          <Trophy size={16} />
        </div>
        <div className="flex flex-col">
          <span className="text-xs font-bold text-amber-800 uppercase tracking-wider">Grand Tasting</span>
          <span className="text-xs text-amber-700 font-medium">Sommelier Masterclass · 75 techniques · ~5min</span>
        </div>
      </div>
    );
  }

  return (
    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-[#F7E7CE]/30 to-[#F7E7CE]/10 border border-[#F7E7CE] shadow-sm">
      <div className="p-1.5 bg-[#722F37]/10 rounded-full text-[#722F37]">
        <Wine size={16} />
      </div>
      <div className="flex flex-col">
        <span className="text-xs font-bold text-[#722F37] uppercase tracking-wider">Standard Tasting</span>
        <span className="text-xs text-[#722F37]/80 font-medium">Six Sommeliers · ~2min</span>
      </div>
    </div>
  );
}
