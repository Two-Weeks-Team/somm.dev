import StartNode from './StartNode';
import EndNode from './EndNode';
import AgentNode from './AgentNode';
import TechniqueNode from './TechniqueNode';
import SynthesisNode from './SynthesisNode';
import RagNode from './RagNode';

export const nodeTypes = {
  start: StartNode,
  end: EndNode,
  agent: AgentNode,
  technique: TechniqueNode,
  synthesis: SynthesisNode,
  rag: RagNode,
  process: TechniqueNode, // Fallback for process nodes
};
