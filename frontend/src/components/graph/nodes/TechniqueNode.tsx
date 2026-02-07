import React, { memo } from 'react';
import { Handle, Position, NodeProps, Node } from '@xyflow/react';
import { ReactFlowNodeData } from '@/types/graph';
import { FileText } from 'lucide-react';
import { cn } from '@/lib/utils';

const TechniqueNode = ({ data }: NodeProps<Node<ReactFlowNodeData>>) => {
  const isFuture = data.isFuture;
  
  return (
    <div className={cn(
      'w-56 bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-all duration-300',
      isFuture && 'opacity-40 grayscale'
    )}>
      <Handle type="target" position={Position.Top} className="w-3 h-3 !bg-gray-400" />
      
      <div className="p-3 border-l-4" style={{ borderLeftColor: data.color || '#F7E7CE' }}>
        <div className="flex items-start space-x-2">
          <FileText size={16} className="text-gray-400 mt-1 flex-shrink-0" />
          <div>
            <h4 className="font-medium text-gray-900 text-sm leading-tight">{data.label}</h4>
            {data.category && (
              <span className="text-xs text-gray-500 mt-1 block">{data.category}</span>
            )}
          </div>
        </div>
      </div>
      
      <Handle type="source" position={Position.Bottom} className="w-3 h-3 !bg-gray-400" />
    </div>
  );
};

export default memo(TechniqueNode);
