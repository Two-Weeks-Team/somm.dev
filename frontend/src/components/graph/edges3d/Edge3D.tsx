import React from 'react';
import { Line } from '@react-three/drei';
import { Graph3DEdge, Position3D } from '@/types/graph';

interface Edge3DProps {
  edge: Graph3DEdge;
  start: Position3D;
  end: Position3D;
}

export const Edge3D: React.FC<Edge3DProps> = ({ edge, start, end }) => {
  return (
    <Line
      points={[
        [start.x, start.y, start.z],
        [end.x, end.y, end.z]
      ]}
      color={edge.color || '#999999'}
      opacity={0.6}
      transparent
      lineWidth={1}
    />
  );
};
