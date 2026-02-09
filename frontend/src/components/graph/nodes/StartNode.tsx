import React, { memo } from 'react';
import { Handle, Position, NodeProps, Node } from '@xyflow/react';
import { ReactFlowNodeData } from '@/types/graph';
import { Wine } from 'lucide-react';

const StartNode = ({ data: _data }: NodeProps<Node<ReactFlowNodeData>>) => {
  return (
    <div className="flex flex-col items-center justify-center">
      <div className="w-16 h-16 rounded-full bg-gradient-to-br from-[#722F37] to-[#5D262D] flex items-center justify-center shadow-lg border-2 border-[#F7E7CE]">
        <Wine className="text-[#F7E7CE]" size={28} />
      </div>
      <div className="mt-2 text-sm font-bold text-[#722F37]">Begin Tasting</div>
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 !bg-[#722F37]"
      />
    </div>
  );
};

export default memo(StartNode);
