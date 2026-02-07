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
  BackgroundVariant,
  NodeMouseHandler
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { api } from '@/lib/api';
import { nodeTypes } from './graph/nodes';
import { getLayoutedElements } from '@/lib/graphLayout';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { ModeIndicatorBadge } from './ModeIndicatorBadge';
import { GraphLegend } from './graph/GraphLegend';
import { GraphNodeDetails } from './graph/GraphNodeDetails';
import { getAgentColor, getCategoryColor } from '@/lib/graphColors';
import { GraphEvaluationMode, ReactFlowNodeData } from '@/types/graph';

import { TimelinePlayer } from './graph/TimelinePlayer';
import { useTimelinePlayer } from '@/hooks/useTimelinePlayer';
import { useMediaQuery } from '@/hooks/useMediaQuery';
import { GraphSkeleton } from './graph/GraphSkeleton';

interface SelectedNode {
  id: string;
  type: string;
  data: ReactFlowNodeData;
}

interface Graph2DTabProps {
  evaluationId: string;
}

export function Graph2DTab({ evaluationId }: Graph2DTabProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [maxStep, setMaxStep] = useState(0);
  const [mode, setMode] = useState<GraphEvaluationMode | string>('six_hats');
  const [selectedNode, setSelectedNode] = useState<SelectedNode | null>(null);
  const isMobile = useMediaQuery('(max-width: 768px)');

  const {
    currentStep,
    setCurrentStep,
    isPlaying,
    togglePlay,
    playbackSpeed,
    setPlaybackSpeed,
  } = useTimelinePlayer(maxStep);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const graphData = await api.getGraph(evaluationId);
      setMode(graphData.mode);
      
      const maxNodeStep = Math.max(...graphData.nodes.map(n => (n.data.step as number) || 0), 0);
      setMaxStep(maxNodeStep);
      setCurrentStep(maxNodeStep);
      
      const initialNodes: Node[] = graphData.nodes.map(node => {
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
            mode: graphData.mode
          },
        };
      });

      const initialEdges: Edge[] = graphData.edges.map(edge => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        animated: true,
        style: { stroke: '#722F37', strokeWidth: 2 },
      }));

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
  }, [evaluationId, setNodes, setEdges, setCurrentStep]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    setNodes((nds) =>
      nds.map((node) => {
        const nodeStep = (node.data.step as number) || 0;
        const isFuture = nodeStep > currentStep;
        return {
          ...node,
          style: {
            ...node.style,
            opacity: isFuture ? 0.1 : 1,
            filter: isFuture ? 'grayscale(100%)' : 'none',
            transition: 'opacity 0.3s ease, filter 0.3s ease',
          },
          data: {
            ...node.data,
            isFuture,
          }
        };
      })
    );
  }, [currentStep, setNodes]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  );

  const onNodeClick: NodeMouseHandler = useCallback((_event, node) => {
    setSelectedNode({
      id: node.id,
      type: node.type || 'unknown',
      data: node.data as ReactFlowNodeData,
    });
  }, []);

  const handleCloseDetails = useCallback(() => {
    setSelectedNode(null);
  }, []);

  if (loading) {
    return (
      <div className="md:h-[600px] h-[400px]">
        <GraphSkeleton />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center md:h-[600px] h-[400px] bg-white rounded-2xl shadow-sm border border-gray-100">
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
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <ModeIndicatorBadge mode={mode} />
      </div>

      <div className="md:h-[600px] h-[400px] bg-[#FAFAFA] rounded-2xl shadow-sm border border-gray-200 overflow-hidden relative">
        <GraphLegend mode={mode} />
        {selectedNode && (
          <GraphNodeDetails
            nodeId={selectedNode.id}
            nodeType={selectedNode.type}
            data={selectedNode.data}
            onClose={handleCloseDetails}
          />
        )}
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          onPaneClick={handleCloseDetails}
          nodeTypes={nodeTypes}
          fitView
          attributionPosition="bottom-left"
          minZoom={0.1}
          maxZoom={1.5}
        >
          <Controls className="!bg-white !border-gray-200 !shadow-sm" />
          {!isMobile && (
            <MiniMap 
              className="!bg-white !border-gray-200 !shadow-sm"
              nodeColor={(node) => {
                if (node.data.color && typeof node.data.color === 'string') {
                  return node.data.color;
                }
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
          )}
          <Background variant={BackgroundVariant.Dots} gap={12} size={1} color="#E5E7EB" />
        </ReactFlow>
      </div>

      <TimelinePlayer
        currentStep={currentStep}
        maxStep={maxStep}
        isPlaying={isPlaying}
        onStepChange={setCurrentStep}
        onPlayPause={togglePlay}
        playbackSpeed={playbackSpeed}
        onSpeedChange={setPlaybackSpeed}
      />
    </div>
  );
}
