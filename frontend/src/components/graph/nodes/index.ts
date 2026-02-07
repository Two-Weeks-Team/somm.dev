import StartNode from './StartNode';
import EndNode from './EndNode';
import AgentNode from './AgentNode';
import TechniqueNode from './TechniqueNode';
import SynthesisNode from './SynthesisNode';
import RagNode from './RagNode';
import HatNode from './HatNode';
import ItemNode from './ItemNode';
import ProcessNode from './ProcessNode';

export const nodeTypes = {
  start: StartNode,
  end: EndNode,
  agent: AgentNode,
  technique: TechniqueNode,
  synthesis: SynthesisNode,
  rag: RagNode,
  hat: HatNode,
  item: ItemNode,
  process: ProcessNode,
};
