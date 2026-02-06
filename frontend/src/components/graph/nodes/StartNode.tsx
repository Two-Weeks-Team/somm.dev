import React, { memo } from 'react';
import { Handle, Position, NodeProps, Node } from '@xyflow/react';
import { ReactFlowNodeData } from '@/types/graph';

const StartNode = ({ data }: NodeProps<Node<ReactFlowNodeData>>) => {
  return (
    <div className="flex flex-col items-center justify-center">
      <div className="w-16 h-16 rounded-full bg-[#722F37] flex items-center justify-center shadow-lg border-2 border-[#F7E7CE]">
        <span className="text-white font-bold text-xs">START</span>
      </div>
      <div className="mt-2 text-sm font-medium text-gray-700">{data.label}</div>
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 !bg-[#722F37]"
      />
    </div>
  );
};

export default memo(StartNode);
