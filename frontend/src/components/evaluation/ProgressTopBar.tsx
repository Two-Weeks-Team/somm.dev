import React from 'react';
import { Wifi, WifiOff, Clock, GitBranch, Loader2 } from 'lucide-react';

interface ProgressTopBarProps {
  repoName: string;
  connectionStatus: 'connecting' | 'open' | 'retrying' | 'failed' | 'closed';
  elapsedSeconds: number;
  etaSeconds?: number;
  totalTechniques: number;
  completedTechniques: number;
  enrichmentMessage?: string | null;
}

export const ProgressTopBar: React.FC<ProgressTopBarProps> = ({
  repoName,
  connectionStatus,
  elapsedSeconds,
  etaSeconds,
  totalTechniques,
  completedTechniques,
  enrichmentMessage,
}) => {
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getConnectionColor = () => {
    switch (connectionStatus) {
      case 'open': return 'bg-emerald-500/20 text-emerald-700 border-emerald-500/30';
      case 'connecting': return 'bg-blue-500/20 text-blue-700 border-blue-500/30';
      case 'retrying': return 'bg-amber-500/20 text-amber-700 border-amber-500/30';
      case 'failed': return 'bg-red-500/20 text-red-700 border-red-500/30';
      default: return 'bg-gray-500/20 text-gray-700 border-gray-500/30';
    }
  };

  const getConnectionText = () => {
    switch (connectionStatus) {
      case 'open': return 'Live';
      case 'connecting': return 'Connecting...';
      case 'retrying': return 'Reconnecting...';
      case 'failed': return 'Offline';
      default: return 'Unknown';
    }
  };

  return (
    <div className="w-full bg-white/80 backdrop-blur-md border-b border-[#722F37]/10 sticky top-0 z-50 px-4 py-3 shadow-sm">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
        
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-[#722F37] font-serif font-bold text-lg">
            <GitBranch size={18} />
            <span className="truncate max-w-[200px]">{repoName}</span>
          </div>
          <div className="hidden sm:flex items-center px-2.5 py-0.5 rounded-full bg-[#722F37]/5 border border-[#722F37]/10 text-xs font-medium text-[#722F37]">
            Full Techniques · {totalTechniques}
          </div>
        </div>

        <div className="flex items-center gap-4 text-sm">
          <div 
            className={`flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-700 text-xs font-medium transition-opacity duration-300 ${enrichmentMessage ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
            style={{ visibility: enrichmentMessage ? 'visible' : 'hidden' }}
          >
            <Loader2 size={12} className="animate-spin" />
            <span className="truncate max-w-[150px]">{enrichmentMessage || 'Loading...'}</span>
          </div>
          <div className="hidden md:block text-gray-600 font-medium">
            <span className="text-[#722F37] font-bold">{completedTechniques}</span>
            <span className="text-gray-400 mx-1">/</span>
            <span>{totalTechniques} techniques</span>
          </div>

          <div className="flex items-center gap-1.5 text-gray-600 bg-gray-100/50 px-3 py-1 rounded-full border border-gray-200">
            <Clock size={14} />
            <span className="font-mono font-medium">{formatTime(elapsedSeconds)}</span>
            {etaSeconds && (
              <span className="text-gray-400 text-xs ml-1">
                / ~{formatTime(etaSeconds)}
              </span>
            )}
          </div>

          <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full border text-xs font-semibold transition-colors ${getConnectionColor()}`}>
            {connectionStatus === 'open' ? (
              <Wifi size={14} className="animate-pulse" />
            ) : (
              <WifiOff size={14} />
            )}
            <span>{getConnectionText()}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
