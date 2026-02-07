import React, { memo } from 'react';
import { Handle, Position, NodeProps, Node } from '@xyflow/react';
import { ReactFlowNodeData } from '@/types/graph';
import { Star, Award } from 'lucide-react';
import Image from 'next/image';
import { cn } from '@/lib/utils';

const SynthesisNode = ({ data }: NodeProps<Node<ReactFlowNodeData>>) => {
  const isActive = data.status === 'running';
  const isFuture = data.isFuture;

  return (
    <div className={cn(
      'w-72 bg-gradient-to-br from-[#722F37] to-[#5D262D] rounded-lg shadow-xl border border-[#F7E7CE] text-white overflow-hidden transition-all duration-300',
      isActive && 'animate-pulse-glow',
      isFuture && 'opacity-40 grayscale'
    )}>
      <Handle type="target" position={Position.Top} className="w-3 h-3 !bg-[#F7E7CE]" />
      
      <div className="p-4">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 rounded-full overflow-hidden border-2 border-[#F7E7CE] flex-shrink-0">
            <Image
              src="/sommeliers/jeanpierre.png"
              alt="Jean-Pierre"
              width={48}
              height={48}
              className="object-cover object-top w-full h-full"
            />
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <h3 className="font-serif text-lg font-bold">Jean-Pierre</h3>
              <Star className="text-[#F7E7CE] fill-[#F7E7CE]" size={16} />
            </div>
            <p className="text-[#F7E7CE] text-xs font-medium">Grand Sommelier</p>
            <p className="text-white/60 text-xs">Final Synthesis</p>
          </div>
        </div>
        
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
