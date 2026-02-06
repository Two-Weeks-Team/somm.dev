import React, { memo } from 'react';
import { Handle, Position, NodeProps, Node } from '@xyflow/react';
import { ReactFlowNodeData } from '@/types/graph';
import { Database, Search } from 'lucide-react';

const RagNode = ({ data }: NodeProps<Node<ReactFlowNodeData>>) => {
  return (
    <div className="w-48 bg-slate-50 rounded-lg shadow-sm border border-slate-200 p-3 flex items-center space-x-3">
      <Handle type="target" position={Position.Top} className="w-3 h-3 !bg-slate-400" />
      
      <div className="w-10 h-10 rounded bg-slate-200 flex items-center justify-center text-slate-600 flex-shrink-0">
        <Database size={18} />
      </div>
      
      <div className="flex-1 min-w-0">
        <h4 className="font-medium text-slate-800 text-sm truncate" title={data.label}>
          {data.label}
        </h4>
        <div className="flex items-center text-xs text-slate-500 mt-0.5">
          <Search size={10} className="mr-1" />
          <span>Retrieval</span>
        </div>
      </div>
      
      <Handle type="source" position={Position.Bottom} className="w-3 h-3 !bg-slate-400" />
    </div>
  );
};

export default memo(RagNode);
