import React, { useRef, useState } from 'react';
import { useFrame, ThreeEvent } from '@react-three/fiber';
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

  const handlePointerOver = (e: ThreeEvent<PointerEvent>) => {
    e.stopPropagation();
    setHovered(true);
    document.body.style.cursor = 'pointer';
  };

  const handlePointerOut = () => {
    setHovered(false);
    document.body.style.cursor = 'auto';
  };

  const renderGeometry = () => {
    switch (node.node_type) {
      case 'start':
      case 'end':
        return <sphereGeometry args={[10, 32, 32]} />;
      case 'agent':
        return <boxGeometry args={[18, 18, 18]} />;
      case 'technique':
        return <octahedronGeometry args={[8, 0]} />;
      case 'synthesis':
        return <cylinderGeometry args={[10, 10, 16, 32]} />;
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
      
      <Html distanceFactor={200} position={[0, 20, 0]} center zIndexRange={[0, 0]}>
        <div className="pointer-events-none select-none whitespace-nowrap rounded bg-black/70 px-2 py-1 text-xs text-white backdrop-blur-sm">
          {node.node_type === 'synthesis' ? 'Jean-Pierre' : node.label}
        </div>
      </Html>
    </group>
  );
};
