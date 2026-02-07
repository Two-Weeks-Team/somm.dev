import React, { useState } from 'react';
import Image from 'next/image';
import { ChevronDown, ChevronUp, Info } from 'lucide-react';
import { GraphEvaluationMode } from '@/types/graph';
import { SIX_HATS_COLORS, FULL_TECHNIQUES_COLORS } from '@/lib/graphColors';
import { SOMMELIER_THEMES } from '@/lib/sommeliers';

interface GraphLegendProps {
  mode: GraphEvaluationMode | string;
}

export function GraphLegend({ mode }: GraphLegendProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const isGrandTasting = mode === 'full_techniques';

  return (
    <div className="absolute top-4 right-4 z-50 bg-white/95 backdrop-blur-sm border border-gray-200 rounded-lg shadow-lg max-w-[280px] transition-all duration-300">
      <button 
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between w-full px-4 py-3 text-sm font-medium text-gray-700 hover:bg-gray-50 rounded-t-lg"
      >
        <div className="flex items-center gap-2">
          <Info size={16} className="text-[#722F37]" />
          <span>Graph Legend</span>
        </div>
        {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </button>

      {isExpanded && (
        <div className="px-4 pb-4 space-y-4 border-t border-gray-100 pt-3">
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Node Types</h4>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-[#722F37]"></div>
                <span className="text-xs text-gray-600">Start / End</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-[#DAA520]"></div>
                <span className="text-xs text-gray-600">Synthesis</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-[#F7E7CE] border border-gray-300"></div>
                <span className="text-xs text-gray-600">Technique / Process</span>
              </div>
            </div>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
              {isGrandTasting ? 'Evaluation Categories' : 'Sommeliers'}
            </h4>
            <div className="grid grid-cols-2 gap-2">
              {isGrandTasting ? (
                Object.entries(FULL_TECHNIQUES_COLORS).map(([category, { hex }]) => (
                  <div key={category} className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: hex }}></div>
                    <span className="text-xs text-gray-600 truncate" title={category}>{category}</span>
                  </div>
                ))
              ) : (
                Object.entries(SOMMELIER_THEMES).map(([id, theme]) => (
                  <div key={id} className="flex items-center gap-2">
                    <div 
                      className="w-5 h-5 rounded-full overflow-hidden border flex-shrink-0"
                      style={{ borderColor: theme.color }}
                    >
                      <Image
                        src={theme.image}
                        alt={theme.name}
                        width={20}
                        height={20}
                        className="object-cover object-top w-full h-full"
                      />
                    </div>
                    <span className="text-xs text-gray-600 truncate" title={theme.name}>{theme.name}</span>
                  </div>
                ))
              )}
            </div>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Connections</h4>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <div className="h-0.5 w-8 bg-[#722F37]"></div>
                <span className="text-xs text-gray-600">Flow</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-0.5 w-8 bg-[#722F37] border-t border-dashed border-[#722F37]"></div>
                <span className="text-xs text-gray-600">Data / Reference</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
