import React, { useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';
import { Graph3DNode } from '@/types/graph';

interface Node3DProps {
  node: Graph3DNode;
  onClick?: (node: Graph3DNode) => void;
}

const WINE_COLOR = '#722F37';
const GOLD_COLOR = '#DAA520';
const DEFAULT_COLOR = '#cccccc';

export const Node3D: React.FC<Node3DProps> = ({ node, onClick }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  useFrame((state, delta) => {
    if (hovered && meshRef.current) {
      meshRef.current.rotation.y += delta;
    }
  });

  const position: [number, number, number] = [
    node.position.x,
    node.position.y,
    node.position.z
  ];

  const handlePointerOver = (e: any) => {
    e.stopPropagation();
    setHovered(true);
    document.body.style.cursor = 'pointer';
  };

  const handlePointerOut = (e: any) => {
    setHovered(false);
    document.body.style.cursor = 'auto';
  };

  const renderGeometry = () => {
    switch (node.node_type) {
      case 'start':
      case 'end':
        return <sphereGeometry args={[8, 32, 32]} />;
      case 'agent':
        return <boxGeometry args={[12, 12, 12]} />;
      case 'technique':
        return <octahedronGeometry args={[8, 0]} />;
      case 'synthesis':
        return <cylinderGeometry args={[6, 6, 12, 32]} />;
      case 'rag':
        return <dodecahedronGeometry args={[8, 0]} />;
      default:
        return <sphereGeometry args={[6, 16, 16]} />;
    }
  };

  const getColor = () => {
    if (node.color) return node.color;
    
    switch (node.node_type) {
      case 'start':
      case 'end':
        return WINE_COLOR;
      case 'synthesis':
        return GOLD_COLOR;
      default:
        return DEFAULT_COLOR;
    }
  };

  return (
    <group position={position}>
      <mesh
        ref={meshRef}
        onClick={() => onClick?.(node)}
        onPointerOver={handlePointerOver}
        onPointerOut={handlePointerOut}
      >
        {renderGeometry()}
        <meshStandardMaterial 
          color={getColor()} 
          emissive={hovered ? '#444444' : '#000000'}
          roughness={0.3}
          metalness={0.2}
        />
      </mesh>
      
      <Html distanceFactor={200} position={[0, 15, 0]} center>
        <div className="pointer-events-none select-none whitespace-nowrap rounded bg-black/70 px-2 py-1 text-xs text-white backdrop-blur-sm">
          {node.label}
        </div>
      </Html>
    </group>
  );
};
