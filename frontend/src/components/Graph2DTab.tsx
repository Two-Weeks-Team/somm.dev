'use client';

import React, { useEffect, useCallback, useState } from 'react';
import { 
  ReactFlow, 
  MiniMap, 
  Controls, 
  Background, 
  useNodesState, 
  useEdgesState,
  Node,
  Edge,
  Connection,
  addEdge,
  BackgroundVariant
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { api } from '@/lib/api';
import { nodeTypes } from './graph/nodes';
import { getLayoutedElements } from '@/lib/graphLayout';
import { Loader2, AlertCircle, RefreshCw } from 'lucide-react';

interface Graph2DTabProps {
  evaluationId: string;
}

export function Graph2DTab({ evaluationId }: Graph2DTabProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const graphData = await api.getGraph(evaluationId);
      
      // Transform API nodes to ReactFlow nodes
      const initialNodes: Node[] = graphData.nodes.map(node => ({
        id: node.id,
        type: node.type,
        position: node.position || { x: 0, y: 0 },
        data: node.data,
      }));

      // Transform API edges to ReactFlow edges
      const initialEdges: Edge[] = graphData.edges.map(edge => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        animated: true,
        style: { stroke: '#722F37', strokeWidth: 2 },
      }));

      // Apply layout
      const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
        initialNodes,
        initialEdges
      );

      setNodes(layoutedNodes);
      setEdges(layoutedEdges);
    } catch (err) {
      console.error('Failed to fetch graph data:', err);
      setError('Failed to load graph data. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [evaluationId, setNodes, setEdges]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  );

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-[600px] bg-white rounded-2xl shadow-sm border border-gray-100">
        <Loader2 className="w-10 h-10 text-[#722F37] animate-spin mb-4" />
        <p className="text-gray-500 font-medium">Loading graph visualization...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-[600px] bg-white rounded-2xl shadow-sm border border-gray-100">
        <AlertCircle className="w-10 h-10 text-red-500 mb-4" />
        <p className="text-gray-800 font-medium mb-2">{error}</p>
        <button 
          onClick={fetchData}
          className="flex items-center px-4 py-2 bg-[#722F37] text-white rounded-lg hover:bg-[#5D262D] transition-colors"
        >
          <RefreshCw size={16} className="mr-2" />
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="h-[800px] bg-[#FAFAFA] rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-left"
        minZoom={0.1}
        maxZoom={1.5}
      >
        <Controls className="!bg-white !border-gray-200 !shadow-sm" />
        <MiniMap 
          className="!bg-white !border-gray-200 !shadow-sm"
          nodeColor={(node) => {
            switch (node.type) {
              case 'start':
              case 'end':
                return '#722F37';
              case 'agent':
                return '#2E4A3F';
              case 'technique':
                return '#F7E7CE';
              case 'synthesis':
                return '#DAA520';
              default:
                return '#eee';
            }
          }}
        />
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} color="#E5E7EB" />
      </ReactFlow>
    </div>
  );
}
