import React, { memo } from 'react';
import { Handle, Position, NodeProps, Node } from '@xyflow/react';
import { ReactFlowNodeData } from '@/types/graph';
import { Cog } from 'lucide-react';
import { cn } from '@/lib/utils';

const ProcessNode = ({ data }: NodeProps<Node<ReactFlowNodeData>>) => {
  const isFuture = data.isFuture;
  const stepNumber = data.step as number | undefined;

  return (
    <div
      className={cn(
        'w-44 bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden transition-all duration-300',
        isFuture && 'opacity-40 grayscale'
      )}
    >
      <Handle type="target" position={Position.Top} className="w-3 h-3 !bg-gray-400" />

      <div className="p-3 border-l-4 border-[#722F37]">
        <div className="flex items-start space-x-2">
          <div className="w-8 h-8 rounded bg-[#722F37]/10 flex items-center justify-center flex-shrink-0">
            <Cog size={16} className="text-[#722F37]" />
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="font-medium text-gray-900 text-sm leading-tight truncate" title={data.label as string}>
              {data.label}
            </h4>
            {stepNumber !== undefined && (
              <span className="text-xs text-gray-500">Step {stepNumber}</span>
            )}
          </div>
        </div>
      </div>

      <Handle type="source" position={Position.Bottom} className="w-3 h-3 !bg-gray-400" />
    </div>
  );
};

export default memo(ProcessNode);
