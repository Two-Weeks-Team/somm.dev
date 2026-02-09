'use client';

import React, { useEffect, useCallback, useState } from 'react';
import {
  ReactFlow,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  Node,
  Edge,
  BackgroundVariant,
  NodeMouseHandler,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { api } from '@/lib/api';
import { nodeTypes } from './nodes';
import { getLayoutedElements } from '@/lib/graphLayout';
import { AlertCircle, RefreshCw, Loader2 } from 'lucide-react';
import { getAgentColor, getCategoryColor } from '@/lib/graphColors';
import { GraphEvaluationMode, ReactFlowNodeData } from '@/types/graph';
import { cn } from '@/lib/utils';

type GraphViewType = 'structure' | 'execution';

interface InteractiveGraphViewProps {
  evaluationId: string;
  view: GraphViewType;
  currentStep?: number;
  className?: string;
  onNodeClick?: (nodeId: string, nodeData: ReactFlowNodeData) => void;
}

interface _SelectedNode {
  id: string;
  type: string;
  data: ReactFlowNodeData;
}

export function InteractiveGraphView({
  evaluationId,
  view,
  currentStep,
  className,
  onNodeClick: onNodeClickProp,
}: InteractiveGraphViewProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [_mode, setMode] = useState<GraphEvaluationMode | string>('six_hats');
  const [_maxStep, setMaxStep] = useState(0);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const graphData =
        view === 'structure'
          ? await api.getGraphStructure(evaluationId)
          : await api.getGraphExecution(evaluationId);

      setMode(graphData.mode);

      const maxNodeStep = Math.max(
        ...graphData.nodes.map((n) => (n.data.step as number) || 0),
        0
      );
      setMaxStep(maxNodeStep);

      const initialNodes: Node[] = graphData.nodes.map((node) => {
        let nodeColor = node.data.color as string;

        if (node.type === 'agent') {
          if (graphData.mode === 'full_techniques') {
            nodeColor = getCategoryColor(node.data.category as string);
          } else {
            nodeColor = getAgentColor(node.data.label as string);
          }
        }

        return {
          id: node.id,
          type: node.type,
          position: node.position || { x: 0, y: 0 },
          data: {
            ...node.data,
            color: nodeColor,
            mode: graphData.mode,
          },
        };
      });

      const initialEdges: Edge[] = graphData.edges.map((edge) => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        animated: view === 'execution',
        style: {
          stroke: '#722F37',
          strokeWidth: 2,
          strokeDasharray: edge.data?.edge_type === 'secondary' ? '5,5' : undefined,
        },
      }));

      const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
        initialNodes,
        initialEdges
      );

      setNodes(layoutedNodes);
      setEdges(layoutedEdges);
    } catch (err) {
      console.error(`Failed to fetch ${view} graph data:`, err);
      setError(`Failed to load ${view} graph data. Please try again.`);
    } finally {
      setLoading(false);
    }
  }, [evaluationId, view, setNodes, setEdges]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Step-based visibility: opacity/blur for nodes beyond currentStep
  useEffect(() => {
    if (currentStep === undefined) return;

    setNodes((nds) =>
      nds.map((node) => {
        const nodeStep = (node.data.step as number) || 0;
        const isFuture = nodeStep > currentStep;
        return {
          ...node,
          style: {
            ...node.style,
            opacity: isFuture ? 0.15 : 1,
            filter: isFuture ? 'grayscale(100%) blur(1px)' : 'none',
            transition: 'opacity 0.3s ease, filter 0.3s ease',
          },
          data: {
            ...node.data,
            isFuture,
          },
        };
      })
    );
  }, [currentStep, setNodes]);

  const handleNodeClick: NodeMouseHandler = useCallback(
    (_event, node) => {
      if (onNodeClickProp) {
        onNodeClickProp(node.id, node.data as ReactFlowNodeData);
      }
    },
    [onNodeClickProp]
  );

  if (loading) {
    return (
      <div
        className={cn(
          'flex items-center justify-center bg-gray-50 rounded-lg',
          className
        )}
      >
        <Loader2 className="w-8 h-8 animate-spin text-[#722F37]" />
      </div>
    );
  }

  if (error) {
    return (
      <div
        className={cn(
          'flex flex-col items-center justify-center bg-white rounded-lg border border-gray-100',
          className
        )}
      >
        <AlertCircle className="w-8 h-8 text-red-500 mb-3" />
        <p className="text-gray-800 font-medium text-sm mb-2">{error}</p>
        <button
          onClick={fetchData}
          className="flex items-center px-3 py-1.5 text-sm bg-[#722F37] text-white rounded-lg hover:bg-[#5D262D] transition-colors"
        >
          <RefreshCw size={14} className="mr-1.5" />
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className={cn('bg-[#FAFAFA] rounded-lg overflow-hidden', className)}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-left"
        minZoom={0.1}
        maxZoom={1.5}
        proOptions={{ hideAttribution: true }}
      >
        <Controls className="!bg-white !border-gray-200 !shadow-sm" />
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} color="#E5E7EB" />
      </ReactFlow>
    </div>
  );
}
