import React, { useMemo } from 'react';
import * as THREE from 'three';
import { Graph3DEdge } from '@/types/graph';

interface BundledEdge3DProps {
  edge: Graph3DEdge;
}

export const BundledEdge3D: React.FC<BundledEdge3DProps> = ({ edge }) => {
  const curve = useMemo(() => {
    if (!edge.bundled_path || edge.bundled_path.length < 2) return null;

    const points = edge.bundled_path.map(
      p => new THREE.Vector3(p.x, p.y, p.z)
    );
    
    return new THREE.CatmullRomCurve3(points);
  }, [edge.bundled_path]);

  if (!curve) return null;

  return (
    <mesh>
      <tubeGeometry args={[curve, 64, 0.5, 8, false]} />
      <meshStandardMaterial 
        color={edge.color || '#999999'} 
        opacity={0.6} 
        transparent 
        roughness={0.4}
        metalness={0.1}
      />
    </mesh>
  );
};
