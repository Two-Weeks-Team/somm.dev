import React from 'react';
import { TechniquePill } from './TechniquePill';

interface TechniqueStatus {
  id: string;
  name: string;
  category: string;
  status: 'queued' | 'running' | 'complete' | 'error';
  score?: number;
}

interface CategoryGlassCardProps {
  category: {
    id: string;
    name: string;
    completed: number;
    total: number;
    status: 'pending' | 'running' | 'complete';
  };
  techniques: TechniqueStatus[];
}

const CATEGORY_COLORS: Record<string, string> = {
  aroma: '#C41E3A',
  palate: '#DAA520',
  body: '#2F4F4F',
  finish: '#F7E7CE',
  balance: '#228B22',
  vintage: '#8B7355',
  terroir: '#722F37',
  cellar: '#2E4A3F',
};

export const CategoryGlassCard: React.FC<CategoryGlassCardProps> = ({ category, techniques }) => {
  const color = CATEGORY_COLORS[category.id] || '#722F37';
  const progress = (category.completed / category.total) * 100;
  const isComplete = category.completed === category.total;
  const isRunning = category.status === 'running';

  return (
    <div className={`
      relative overflow-hidden rounded-xl border transition-all duration-500
      ${isRunning ? 'shadow-lg ring-1 ring-offset-2' : 'shadow-sm'}
      ${isComplete ? 'bg-white/90 border-emerald-100' : 'bg-white/60 border-white/40'}
    `}
    style={{
      borderColor: isRunning ? color : undefined,
      boxShadow: isRunning ? `0 4px 20px -2px ${color}20` : undefined,
    }}
    >
      <div 
        className="absolute bottom-0 left-0 right-0 transition-all duration-1000 ease-in-out opacity-10 pointer-events-none"
        style={{ 
          height: `${progress}%`,
          backgroundColor: color,
        }}
      />

      <div className="relative p-3 border-b border-gray-100/50 flex justify-between items-center bg-white/40 backdrop-blur-sm">
        <h3 className="font-serif font-bold text-gray-800 flex items-center gap-2">
          <span 
            className="w-2 h-2 rounded-full"
            style={{ backgroundColor: color }}
          />
          {category.name}
        </h3>
        <span className="text-xs font-mono text-gray-500 bg-white/50 px-1.5 py-0.5 rounded">
          {category.completed}/{category.total}
        </span>
      </div>

      <div className="relative p-3 grid grid-cols-1 gap-1.5 max-h-[240px] overflow-y-auto scrollbar-thin scrollbar-thumb-gray-200">
        {techniques.map((tech) => (
          <TechniquePill 
            key={tech.id}
            name={tech.name}
            status={tech.status}
            score={tech.score}
          />
        ))}
        
        {Array.from({ length: Math.max(0, category.total - techniques.length) }).map((_, i) => (
          <div 
            key={`placeholder-${i}`} 
            className="h-6 rounded-md border border-dashed border-gray-200 bg-gray-50/30"
          />
        ))}
      </div>
    </div>
  );
};
