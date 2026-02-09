import React, { memo } from 'react';
import { Handle, Position, NodeProps, Node } from '@xyflow/react';
import { ReactFlowNodeData } from '@/types/graph';
import { Trophy } from 'lucide-react';

const EndNode = ({ data: _data }: NodeProps<Node<ReactFlowNodeData>>) => {
  return (
    <div className="flex flex-col items-center justify-center">
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 !bg-[#722F37]"
      />
      <div className="w-16 h-16 rounded-full bg-gradient-to-br from-[#DAA520] to-[#B8860B] flex items-center justify-center shadow-lg border-2 border-[#F7E7CE]">
        <Trophy className="text-white" size={28} />
      </div>
      <div className="mt-2 text-sm font-bold text-[#DAA520]">Vintage Rated</div>
    </div>
  );
};

export default memo(EndNode);
