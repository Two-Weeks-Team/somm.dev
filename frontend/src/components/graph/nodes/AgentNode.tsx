import React, { memo } from 'react';
import { Handle, Position, NodeProps, Node } from '@xyflow/react';
import { ReactFlowNodeData } from '@/types/graph';
import { User, CheckCircle, XCircle, Clock, Loader2 } from 'lucide-react';
import Image from 'next/image';
import { getSommelierTheme } from '@/lib/sommeliers';
import { cn } from '@/lib/utils';

const AgentNode = ({ data }: NodeProps<Node<ReactFlowNodeData>>) => {
  const statusColor = {
    pending: 'bg-gray-100 text-gray-500',
    running: 'bg-blue-100 text-blue-600',
    completed: 'bg-green-100 text-green-600',
    failed: 'bg-red-100 text-red-600',
  };

  const StatusIcon = {
    pending: Clock,
    running: Loader2,
    completed: CheckCircle,
    failed: XCircle,
  };

  const status = data.status || 'pending';
  const Icon = StatusIcon[status];
  
  // Get sommelier theme for avatar
  const label = (data.label as string) || '';
  const sommelierTheme = getSommelierTheme(label.toLowerCase());
  const themeColor = sommelierTheme.color || data.color || '#722F37';
  const isActive = status === 'running';
  const isFuture = data.isFuture;

  return (
    <div 
      className={cn(
        'w-48 bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden transition-all duration-300',
        isActive && !isFuture && 'animate-pulse-glow-blue border-blue-400',
        isFuture && 'opacity-40 grayscale'
      )}
    >
      <Handle type="target" position={Position.Top} className="w-3 h-3 !bg-gray-400" />
      
      <div className="h-2 w-full" style={{ backgroundColor: themeColor }} />
      
      <div className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            <div 
              className="w-10 h-10 rounded-full overflow-hidden border-2 flex-shrink-0"
              style={{ borderColor: themeColor }}
            >
              <Image
                src={sommelierTheme.image}
                alt={label}
                width={40}
                height={40}
                className="object-cover object-top w-full h-full"
              />
            </div>
            <div>
              <h3 className="font-bold text-sm" style={{ color: themeColor }}>{sommelierTheme.name || data.label}</h3>
              <p className="text-xs text-gray-500">{sommelierTheme.description || data.hatType || 'Sommelier'}</p>
            </div>
          </div>
          
          <div className={`p-1 rounded-full ${status === 'running' ? 'animate-spin' : ''}`}>
            <Icon size={16} className={status === 'completed' ? 'text-green-500' : status === 'failed' ? 'text-red-500' : 'text-gray-400'} />
          </div>
        </div>
        
        {data.status && (
          <div className={`mt-3 px-2 py-1 rounded text-xs font-medium inline-block ${statusColor[status]}`}>
            {status.toUpperCase()}
          </div>
        )}
      </div>
      
      <Handle type="source" position={Position.Bottom} className="w-3 h-3 !bg-gray-400" />
    </div>
  );
};

export default memo(AgentNode);
