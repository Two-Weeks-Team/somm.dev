'use client';

import React from 'react';
import { X, Clock, Zap, User, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { ReactFlowNodeData, NodeStatus } from '@/types/graph';
import { cn } from '@/lib/utils';

interface GraphNodeDetailsProps {
  nodeId: string;
  nodeType: string;
  data: ReactFlowNodeData;
  onClose: () => void;
}

function formatTokens(tokens: number): string {
  if (tokens < 1000) return `${tokens}`;
  return `${(tokens / 1000).toFixed(1)}K`;
}

function formatCost(cost: number): string {
  if (cost < 0.01) return `$${cost.toFixed(4)}`;
  return `$${cost.toFixed(2)}`;
}

const statusConfig: Record<NodeStatus, { icon: typeof CheckCircle; color: string; label: string }> = {
  pending: { icon: Clock, color: 'text-gray-400', label: 'Pending' },
  running: { icon: Loader2, color: 'text-blue-500', label: 'Running' },
  completed: { icon: CheckCircle, color: 'text-green-500', label: 'Completed' },
  failed: { icon: XCircle, color: 'text-red-500', label: 'Failed' },
};

function getNodeTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    agent: 'Sommelier Agent',
    technique: 'Analysis Technique',
    start: 'Start',
    end: 'End',
    synthesis: 'Synthesis',
    rag: 'RAG Enhancement',
    process: 'Process Step',
  };
  return labels[type] || type.charAt(0).toUpperCase() + type.slice(1);
}

function getNodeTypeColor(type: string): string {
  const colors: Record<string, string> = {
    agent: 'text-[#722F37]',
    technique: 'text-blue-500',
    start: 'text-green-500',
    end: 'text-green-500',
    synthesis: 'text-amber-500',
    rag: 'text-purple-500',
  };
  return colors[type] || 'text-gray-500';
}

export function GraphNodeDetails({ nodeId, nodeType, data, onClose }: GraphNodeDetailsProps) {
  const status = data.status || 'pending';
  const statusInfo = statusConfig[status];
  const StatusIcon = statusInfo.icon;

  return (
    <div className="absolute top-4 right-4 w-80 max-h-[calc(100%-2rem)] bg-white rounded-xl shadow-xl border border-gray-200 z-20 animate-in slide-in-from-right-4 duration-300 overflow-hidden flex flex-col">
      <div className="flex items-start justify-between p-4 border-b border-gray-100 shrink-0">
        <div className="space-y-1 pr-4">
          <div className={cn('text-xs font-semibold uppercase tracking-wider', getNodeTypeColor(nodeType))}>
            {getNodeTypeLabel(nodeType)}
          </div>
          <h3 className="text-lg font-bold text-gray-900 break-words leading-tight">
            {data.label}
          </h3>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors shrink-0"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
      
      <div className="p-4 space-y-4 text-sm overflow-y-auto flex-1">
        <div className="flex items-center justify-between pt-2 border-t border-gray-100">
          <div>
            <span className="text-xs text-gray-500 block">Status</span>
            <div className="flex items-center gap-1.5 mt-0.5">
              <StatusIcon 
                size={14} 
                className={cn(statusInfo.color, status === 'running' && 'animate-spin')} 
              />
              <span className="font-medium text-gray-700">{statusInfo.label}</span>
            </div>
          </div>
          <div>
            <span className="text-xs text-gray-500 block">Node ID</span>
            <span className="font-mono text-xs text-gray-600">{nodeId.slice(0, 12)}...</span>
          </div>
        </div>

        {nodeType === 'agent' && (
          <div className="space-y-3">
            {data.hatType && (
              <div>
                <span className="text-xs text-gray-500 block">Role</span>
                <span className="text-gray-700">{data.hatType}</span>
              </div>
            )}
            
            <div className="p-3 bg-[#722F37]/5 rounded-lg border border-[#722F37]/10">
              <div className="flex items-center gap-2 mb-2">
                <User size={14} className="text-[#722F37]" />
                <span className="text-xs font-medium text-[#722F37]">Sommelier Details</span>
              </div>
              <p className="text-xs text-gray-600">
                This sommelier agent analyzes specific aspects of your codebase 
                using specialized evaluation techniques.
              </p>
            </div>
          </div>
        )}

        {nodeType === 'technique' && data.category && (
          <div className="space-y-3">
            <div>
              <span className="text-xs text-gray-500 block">Category</span>
              <span className="text-gray-700 capitalize">{data.category}</span>
            </div>
          </div>
        )}

        {(data.tokenUsage !== undefined || data.costUsd !== undefined) && (
          <div className="flex gap-4 pt-3 border-t border-gray-100">
            {data.tokenUsage !== undefined && data.tokenUsage > 0 && (
              <div>
                <span className="text-xs text-gray-500 flex items-center gap-1">
                  <Zap size={12} />
                  Tokens
                </span>
                <p className="text-sm font-medium text-gray-700">{formatTokens(data.tokenUsage)}</p>
              </div>
            )}
            {data.costUsd !== undefined && data.costUsd > 0 && (
              <div>
                <span className="text-xs text-gray-500 flex items-center gap-1">
                  <Clock size={12} />
                  Cost
                </span>
                <p className="text-sm font-medium text-gray-700">{formatCost(data.costUsd)}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
