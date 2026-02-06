import dagre from 'dagre';
import { Node, Edge, Position } from '@xyflow/react';

const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

const nodeWidth = 250;
const nodeHeight = 100;

export const getLayoutedElements = (nodes: Node[], edges: Edge[], direction = 'TB') => {
  const isHorizontal = direction === 'LR';
  dagreGraph.setGraph({ rankdir: direction, nodesep: 80, ranksep: 120 });

  nodes.forEach((node) => {
    // Adjust dimensions based on node type if needed
    let width = nodeWidth;
    let height = nodeHeight;
    
    if (node.type === 'start' || node.type === 'end') {
      width = 80;
      height = 80;
    } else if (node.type === 'synthesis') {
      width = 300;
      height = 150;
    }

    dagreGraph.setNode(node.id, { width, height });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    
    // We are shifting the dagre node position (anchor=center center) to the top left
    // so it matches the React Flow node anchor point (top left).
    const width = node.measured?.width ?? (node.type === 'start' || node.type === 'end' ? 80 : nodeWidth);
    const height = node.measured?.height ?? (node.type === 'start' || node.type === 'end' ? 80 : nodeHeight);

    return {
      ...node,
      targetPosition: isHorizontal ? Position.Left : Position.Top,
      sourcePosition: isHorizontal ? Position.Right : Position.Bottom,
      position: {
        x: nodeWithPosition.x - width / 2,
        y: nodeWithPosition.y - height / 2,
      },
    };
  });

  return { nodes: layoutedNodes, edges };
};
