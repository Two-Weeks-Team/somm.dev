import React, { useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import { Graph3DPayload, Graph3DNode } from '@/types/graph';
import { Node3D } from './nodes3d/Node3D';
import { Edge3D } from './edges3d/Edge3D';
import { BundledEdge3D } from './edges3d/BundledEdge3D';

interface GraphView3DProps {
  data: Graph3DPayload;
}

const GraphView3D: React.FC<GraphView3DProps> = ({ data }) => {
  const nodeMap = useMemo(() => {
    const map = new Map<string, Graph3DNode>();
    data.nodes.forEach(node => map.set(node.node_id, node));
    return map;
  }, [data.nodes]);

  return (
    <div className="h-full w-full bg-neutral-900">
      <Canvas camera={{ position: [0, 200, 600], fov: 60 }}>
        <color attach="background" args={['#111111']} />
        <ambientLight intensity={0.5} />
        <pointLight position={[100, 100, 100]} intensity={1} />
        <directionalLight position={[-100, 200, 100]} intensity={0.8} />
        
        <Stars radius={300} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
        
        <OrbitControls makeDefault />

        <group>
          {data.nodes.map((node) => (
            <Node3D key={node.node_id} node={node} />
          ))}

          {data.edges.map((edge) => {
            if (edge.bundled_path && edge.bundled_path.length > 0) {
              return <BundledEdge3D key={edge.edge_id} edge={edge} />;
            }

            const sourceNode = nodeMap.get(edge.source);
            const targetNode = nodeMap.get(edge.target);

            if (sourceNode && targetNode) {
              return (
                <Edge3D
                  key={edge.edge_id}
                  edge={edge}
                  start={sourceNode.position}
                  end={targetNode.position}
                />
              );
            }
            return null;
          })}
        </group>
      </Canvas>
    </div>
  );
};

export default GraphView3D;
