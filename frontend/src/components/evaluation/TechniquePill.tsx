import React from 'react';
import { Check, X, Loader2, Circle } from 'lucide-react';

interface TechniquePillProps {
  name: string;
  status: 'queued' | 'running' | 'complete' | 'error';
  score?: number;
  className?: string;
}

export const TechniquePill: React.FC<TechniquePillProps> = ({ name, status, score, className = '' }) => {
  const getStatusStyles = () => {
    switch (status) {
      case 'running':
        return 'bg-blue-50 text-blue-700 border-blue-200 shadow-sm shadow-blue-100';
      case 'complete':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'error':
        return 'bg-red-50 text-red-700 border-red-200';
      case 'queued':
      default:
        return 'bg-gray-50 text-gray-400 border-gray-100';
    }
  };

  const getIcon = () => {
    switch (status) {
      case 'running':
        return <Loader2 size={10} className="animate-spin" />;
      case 'complete':
        return <Check size={10} strokeWidth={3} />;
      case 'error':
        return <X size={10} strokeWidth={3} />;
      case 'queued':
      default:
        return <Circle size={6} className="fill-current opacity-50" />;
    }
  };

  return (
    <div 
      className={`
        group relative flex items-center gap-1.5 px-2 py-1 rounded-md border text-[10px] font-medium transition-all duration-300
        ${getStatusStyles()}
        ${status === 'running' ? 'scale-105 ring-2 ring-blue-100 ring-offset-1 z-10' : ''}
        ${className}
      `}
    >
      <span className="flex-shrink-0">{getIcon()}</span>
      <span className="truncate max-w-[120px]">{name}</span>
      
      {status === 'complete' && score !== undefined && (
        <span className={`
          ml-auto px-1 rounded text-[9px] font-bold
          ${score >= 90 ? 'bg-emerald-200 text-emerald-800' : 
            score >= 70 ? 'bg-emerald-100 text-emerald-700' : 
            'bg-yellow-100 text-yellow-700'}
        `}>
          {score}
        </span>
      )}
    </div>
  );
};
