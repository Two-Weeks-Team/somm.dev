import React, { memo } from 'react';
import { Handle, Position, NodeProps, Node } from '@xyflow/react';
import { ReactFlowNodeData } from '@/types/graph';
import { Package } from 'lucide-react';
import { cn } from '@/lib/utils';

const BMAD_COLORS: Record<string, { bg: string; border: string }> = {
  A: { bg: '#DBEAFE', border: '#3B82F6' },
  B: { bg: '#DCFCE7', border: '#22C55E' },
  C: { bg: '#FEF9C3', border: '#EAB308' },
  D: { bg: '#FEE2E2', border: '#EF4444' },
};

const ItemNode = ({ data }: NodeProps<Node<ReactFlowNodeData>>) => {
  const category = ((data.category as string) || 'A').toUpperCase().charAt(0);
  const colors = BMAD_COLORS[category] || BMAD_COLORS.A;
  const isFuture = data.isFuture;

  return (
    <div
      className={cn(
        'w-48 rounded-lg shadow-sm border overflow-hidden transition-all duration-300',
        isFuture && 'opacity-40 grayscale'
      )}
      style={{
        backgroundColor: colors.bg,
        borderColor: colors.border,
      }}
    >
      <Handle type="target" position={Position.Top} className="w-3 h-3 !bg-gray-400" />

      <div className="p-3 flex items-start space-x-2">
        <div
          className="w-8 h-8 rounded flex items-center justify-center flex-shrink-0"
          style={{ backgroundColor: colors.border }}
        >
          <Package size={16} className="text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="font-medium text-gray-900 text-sm truncate" title={data.label as string}>
            {data.label}
          </h4>
          <span className="text-xs text-gray-600">Category {category}</span>
        </div>
      </div>

      <Handle type="source" position={Position.Bottom} className="w-3 h-3 !bg-gray-400" />
    </div>
  );
};

export default memo(ItemNode);
