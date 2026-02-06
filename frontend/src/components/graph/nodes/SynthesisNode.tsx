import React, { memo } from 'react';
import { Handle, Position, NodeProps, Node } from '@xyflow/react';
import { ReactFlowNodeData } from '@/types/graph';
import { Star, Award } from 'lucide-react';

const SynthesisNode = ({ data }: NodeProps<Node<ReactFlowNodeData>>) => {
  return (
    <div className="w-72 bg-gradient-to-br from-[#722F37] to-[#5D262D] rounded-lg shadow-xl border border-[#F7E7CE] text-white overflow-hidden">
      <Handle type="target" position={Position.Top} className="w-3 h-3 !bg-[#F7E7CE]" />
      
      <div className="p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <Award className="text-[#F7E7CE]" size={20} />
            <span className="font-bold text-[#F7E7CE] text-xs tracking-wider uppercase">Final Verdict</span>
          </div>
          <Star className="text-[#F7E7CE] fill-[#F7E7CE]" size={16} />
        </div>
        
        <h3 className="font-serif text-xl font-bold mb-1">{data.label}</h3>
        <p className="text-white/80 text-xs">Synthesis & Scoring</p>
        
        {data.status === 'completed' && (
          <div className="mt-3 pt-3 border-t border-white/20 flex justify-between items-center">
            <span className="text-xs text-white/70">Evaluation Complete</span>
            <span className="bg-[#F7E7CE] text-[#722F37] text-xs font-bold px-2 py-0.5 rounded">
              DONE
            </span>
          </div>
        )}
      </div>
      
      <Handle type="source" position={Position.Bottom} className="w-3 h-3 !bg-[#F7E7CE]" />
    </div>
  );
};

export default memo(SynthesisNode);
