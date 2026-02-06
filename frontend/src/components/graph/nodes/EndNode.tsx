import React, { memo } from 'react';
import { Handle, Position, NodeProps, Node } from '@xyflow/react';
import { ReactFlowNodeData } from '@/types/graph';

const EndNode = ({ data }: NodeProps<Node<ReactFlowNodeData>>) => {
  return (
    <div className="flex flex-col items-center justify-center">
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 !bg-[#722F37]"
      />
      <div className="w-16 h-16 rounded-full bg-[#722F37] flex items-center justify-center shadow-lg border-2 border-[#F7E7CE]">
        <span className="text-white font-bold text-xs">END</span>
      </div>
      <div className="mt-2 text-sm font-medium text-gray-700">{data.label}</div>
    </div>
  );
};

export default memo(EndNode);
