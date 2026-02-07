import React, { memo } from 'react';
import { Handle, Position, NodeProps, Node } from '@xyflow/react';
import { ReactFlowNodeData } from '@/types/graph';
import { cn } from '@/lib/utils';

const HAT_COLORS: Record<string, { bg: string; border: string; text: string }> = {
  white: { bg: '#FFFFFF', border: '#E5E7EB', text: '#374151' },
  red: { bg: '#DC2626', border: '#B91C1C', text: '#FFFFFF' },
  black: { bg: '#1F2937', border: '#111827', text: '#FFFFFF' },
  yellow: { bg: '#FBBF24', border: '#D97706', text: '#1F2937' },
  green: { bg: '#16A34A', border: '#15803D', text: '#FFFFFF' },
  blue: { bg: '#2563EB', border: '#1D4ED8', text: '#FFFFFF' },
};

const HatNode = ({ data }: NodeProps<Node<ReactFlowNodeData>>) => {
  const hatType = (data.hatType as string)?.toLowerCase() || 'white';
  const colors = HAT_COLORS[hatType] || HAT_COLORS.white;
  const isFuture = data.isFuture;

  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center transition-all duration-300',
        isFuture && 'opacity-40 grayscale'
      )}
    >
      <Handle type="target" position={Position.Top} className="w-3 h-3 !bg-gray-400" />

      <div
        className="w-16 h-16 rounded-full flex items-center justify-center shadow-md border-2 font-bold text-xs uppercase tracking-wider"
        style={{
          backgroundColor: colors.bg,
          borderColor: colors.border,
          color: colors.text,
        }}
      >
        {hatType.slice(0, 3)}
      </div>

      <div className="mt-2 text-sm font-medium text-gray-700 max-w-[120px] text-center truncate">
        {data.label}
      </div>

      <Handle type="source" position={Position.Bottom} className="w-3 h-3 !bg-gray-400" />
    </div>
  );
};

export default memo(HatNode);
