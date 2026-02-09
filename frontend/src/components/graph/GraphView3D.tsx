'use client';

import React, {
  useRef,
  useEffect,
  useState,
  useMemo,
  useCallback,
  MutableRefObject,
} from 'react';
import dynamic from 'next/dynamic';
import * as THREE from 'three';
import type { ForceGraphMethods, NodeObject, LinkObject } from 'react-force-graph-3d';
import {
  Graph3DPayload,
  Graph3DNode,
  Graph3DEdge,
  Graph3DViewMode,
} from '@/types/graph';
import { useWebGLSupport } from '@/lib/webgl';
import { getAgentColor, getCategoryColor } from '@/lib/graphColors';

interface GraphView3DProps {
  data: Graph3DPayload;
  evaluationId?: string;
  currentStep?: number;
  isPlaying?: boolean;
  playbackSpeed?: number;
  onNodeClick?: (node: Graph3DNode) => void;
  className?: string;
}

type GraphNode = NodeObject & Graph3DNode & { id: string };
type GraphLink = LinkObject & Omit<Graph3DEdge, 'source' | 'target'>;

interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

const WINE_COLOR = '#722F37';
const GOLD_COLOR = '#DAA520';
const DEFAULT_NODE_COLOR = '#888888';
const BACKGROUND_COLOR = '#111111';

const NODE_SIZE_MAP: Record<string, number> = {
  start: 10,
  end: 10,
  agent: 14,
  technique: 10,
  synthesis: 12,
  rag: 10,
  process: 8,
};

const DEFAULT_NODE_SIZE = 8;

const OPACITY_FOCUSED = 1.0;
const OPACITY_CONNECTED = 0.8;
const OPACITY_DIMMED = 0.15;

const glowTextureCache = new Map<string, THREE.Texture>();
const spriteMaterialCache = new Map<string, THREE.SpriteMaterial>();
const lineMaterialCache = new Map<string, THREE.Material>();

function createGlowTexture(color: string, size: number = 64): THREE.Texture {
  const cacheKey = `${color}-${size}`;
  const cached = glowTextureCache.get(cacheKey);
  if (cached) return cached;

  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d')!;

  const gradient = ctx.createRadialGradient(
    size / 2, size / 2, 0,
    size / 2, size / 2, size / 2
  );

  const tempColor = new THREE.Color(color);
  const r = Math.floor(tempColor.r * 255);
  const g = Math.floor(tempColor.g * 255);
  const b = Math.floor(tempColor.b * 255);

  gradient.addColorStop(0, `rgba(${r}, ${g}, ${b}, 1)`);
  gradient.addColorStop(0.3, `rgba(${r}, ${g}, ${b}, 0.8)`);
  gradient.addColorStop(0.6, `rgba(${r}, ${g}, ${b}, 0.3)`);
  gradient.addColorStop(1, `rgba(${r}, ${g}, ${b}, 0)`);

  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, size, size);

  const texture = new THREE.CanvasTexture(canvas);
  texture.needsUpdate = true;
  glowTextureCache.set(cacheKey, texture);
  return texture;
}

function createSpriteMaterial(color: string, opacity: number = 1): THREE.SpriteMaterial {
  const cacheKey = `${color}-${opacity.toFixed(2)}`;
  const cached = spriteMaterialCache.get(cacheKey);
  if (cached) return cached.clone();

  const texture = createGlowTexture(color);
  const material = new THREE.SpriteMaterial({
    map: texture,
    transparent: true,
    opacity,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
  });

  spriteMaterialCache.set(cacheKey, material);
  return material.clone();
}

function createLineMaterial(color: string, dashed: boolean, opacity: number = 0.6): THREE.Material {
  const cacheKey = `${color}-${dashed}-${opacity.toFixed(2)}`;
  const cached = lineMaterialCache.get(cacheKey);
  if (cached) return cached.clone();

  const material = dashed
    ? new THREE.LineDashedMaterial({
        color,
        transparent: true,
        opacity,
        dashSize: 3,
        gapSize: 2,
        linewidth: 1,
      })
    : new THREE.LineBasicMaterial({
        color,
        transparent: true,
        opacity,
        linewidth: 1,
      });

  lineMaterialCache.set(cacheKey, material);
  return material.clone();
}

function getNodeColor(node: GraphNode): string {
  if (node.color) return node.color;
  if (node.hat_type) return getAgentColor(node.hat_type);
  if (node.category) return getCategoryColor(node.category);

  switch (node.node_type) {
    case 'start':
    case 'end':
      return WINE_COLOR;
    case 'synthesis':
      return GOLD_COLOR;
    default:
      return DEFAULT_NODE_COLOR;
  }
}

function getNodeSize(node: GraphNode): number {
  return NODE_SIZE_MAP[node.node_type] || DEFAULT_NODE_SIZE;
}

function isEdgeDashed(link: GraphLink): boolean {
  if (link.dasharray) return true;
  return link.edge_type === 'parallel' || link.edge_type === 'data';
}

function getNodeId(nodeOrId: string | number | NodeObject | undefined): string {
  if (nodeOrId === undefined) return '';
  if (typeof nodeOrId === 'string') return nodeOrId;
  if (typeof nodeOrId === 'number') return String(nodeOrId);
  return String(nodeOrId.id ?? '');
}

const ForceGraph3DComponent = dynamic(
  () => import('react-force-graph-3d'),
  { ssr: false }
);

const GraphView3D: React.FC<GraphView3DProps> = ({
  data,
  currentStep = Infinity,
  isPlaying = false,
  playbackSpeed = 1,
  onNodeClick,
  className,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const fgRef = useRef<ForceGraphMethods>(null);
  const initialFitDone = useRef(false);

  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [focusedNodeId, setFocusedNodeId] = useState<string | null>(null);
  const [userViewMode, setUserViewMode] = useState<Graph3DViewMode>('3d');

  const webglSupported = useWebGLSupport();
  const viewMode: Graph3DViewMode = webglSupported ? userViewMode : '2d';
  const setViewMode = setUserViewMode;

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const updateDimensions = () => {
      const rect = container.getBoundingClientRect();
      setDimensions({
        width: rect.width || 800,
        height: rect.height || 600,
      });
    };

    updateDimensions();

    const resizeObserver = new ResizeObserver(updateDimensions);
    resizeObserver.observe(container);

    return () => resizeObserver.disconnect();
  }, []);

  const nodeMap = useMemo(() => {
    const map = new Map<string, Graph3DNode>();
    data.nodes.forEach((node) => map.set(node.node_id, node));
    return map;
  }, [data.nodes]);

  const connectedNodeIds = useMemo(() => {
    if (!focusedNodeId) return new Set<string>();

    const connected = new Set<string>([focusedNodeId]);

    data.edges.forEach((edge) => {
      if (edge.source === focusedNodeId) connected.add(edge.target);
      if (edge.target === focusedNodeId) connected.add(edge.source);
    });

    return connected;
  }, [focusedNodeId, data.edges]);

  const graphData: GraphData = useMemo(() => {
    const visibleNodes = data.nodes.filter((node) => node.step_number <= currentStep);
    const visibleNodeIds = new Set(visibleNodes.map((n) => n.node_id));

    const visibleEdges = data.edges.filter((edge) => {
      if (edge.step_number > currentStep) return false;
      return visibleNodeIds.has(edge.source) && visibleNodeIds.has(edge.target);
    });

    const nodes: GraphNode[] = visibleNodes.map((node) => ({
      ...node,
      id: node.node_id,
      x: node.position.x,
      y: node.position.z,
      z: node.position.y,
    }));

    const links: GraphLink[] = visibleEdges.map((edge) => ({
      ...edge,
      source: edge.source,
      target: edge.target,
    }));

    return { nodes, links };
  }, [data.nodes, data.edges, currentStep]);

  useEffect(() => {
    const fg = fgRef.current;
    if (!fg) return;

    switch (viewMode) {
      case '2d':
        graphData.nodes.forEach((node) => {
          node.fz = 0;
        });
        break;

      case 'topdown':
        graphData.nodes.forEach((node) => {
          node.fy = 0;
        });
        fg.cameraPosition({ x: 0, y: 500, z: 0 }, { x: 0, y: 0, z: 0 }, 1000);
        break;

      case 'timeline':
        graphData.nodes.forEach((node) => {
          node.fx = node.step_number * 50;
          node.fy = undefined;
          node.fz = undefined;
        });
        break;

      case '3d':
      default:
        graphData.nodes.forEach((node) => {
          node.fx = undefined;
          node.fy = undefined;
          node.fz = undefined;
        });
        break;
    }

    fg.refresh();
  }, [viewMode, graphData.nodes]);

  useEffect(() => {
    const fg = fgRef.current;
    if (!fg || initialFitDone.current) return;

    const timer = setTimeout(() => {
      fg.zoomToFit(400, 50);
      initialFitDone.current = true;
    }, 500);

    return () => clearTimeout(timer);
  }, [graphData.nodes.length]);

  const handleNodeClick = useCallback(
    (node: NodeObject) => {
      const graphNode = node as GraphNode;
      setFocusedNodeId((prev) =>
        prev === graphNode.node_id ? null : graphNode.node_id
      );

      const fg = fgRef.current;
      if (fg && node.x !== undefined && node.y !== undefined) {
        const distance = 150;
        const distRatio = 1 + distance / Math.hypot(node.x || 0, node.y || 0, node.z || 0);

        fg.cameraPosition(
          {
            x: (node.x || 0) * distRatio,
            y: (node.y || 0) * distRatio,
            z: (node.z || 0) * distRatio,
          },
          { x: node.x || 0, y: node.y || 0, z: node.z || 0 },
          1000
        );
      }

      if (onNodeClick) {
        const originalNode = nodeMap.get(graphNode.node_id);
        if (originalNode) onNodeClick(originalNode);
      }
    },
    [onNodeClick, nodeMap]
  );

  const nodeThreeObject = useCallback(
    (node: NodeObject) => {
      const graphNode = node as GraphNode;
      const color = getNodeColor(graphNode);
      const size = getNodeSize(graphNode);

      let opacity = OPACITY_FOCUSED;
      if (focusedNodeId) {
        if (graphNode.node_id === focusedNodeId) {
          opacity = OPACITY_FOCUSED;
        } else if (connectedNodeIds.has(graphNode.node_id)) {
          opacity = OPACITY_CONNECTED;
        } else {
          opacity = OPACITY_DIMMED;
        }
      }

      const material = createSpriteMaterial(color, opacity);
      const sprite = new THREE.Sprite(material);
      sprite.scale.set(size * 2, size * 2, 1);

      const labelCanvas = document.createElement('canvas');
      const ctx = labelCanvas.getContext('2d')!;
      const fontSize = 12;
      const label = graphNode.label || graphNode.node_id;

      ctx.font = `${fontSize}px Inter, sans-serif`;
      const textWidth = ctx.measureText(label).width;

      labelCanvas.width = textWidth + 20;
      labelCanvas.height = fontSize + 10;

      ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
      ctx.roundRect(0, 0, labelCanvas.width, labelCanvas.height, 4);
      ctx.fill();

      ctx.font = `${fontSize}px Inter, sans-serif`;
      ctx.fillStyle = 'white';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(label, labelCanvas.width / 2, labelCanvas.height / 2);

      const labelTexture = new THREE.CanvasTexture(labelCanvas);
      labelTexture.needsUpdate = true;

      const labelMaterial = new THREE.SpriteMaterial({
        map: labelTexture,
        transparent: true,
        opacity,
        depthWrite: false,
      });

      const labelSprite = new THREE.Sprite(labelMaterial);
      const labelScale = textWidth / 15;
      labelSprite.scale.set(labelScale, labelScale * 0.4, 1);
      labelSprite.position.set(0, size * 1.5, 0);

      const group = new THREE.Group();
      group.add(sprite);
      group.add(labelSprite);

      return group;
    },
    [focusedNodeId, connectedNodeIds]
  );

  const linkThreeObject = useCallback(
    (link: LinkObject) => {
      const graphLink = link as GraphLink;
      const color = graphLink.color || '#666666';
      const dashed = isEdgeDashed(graphLink);

      let opacity = 0.6;
      if (focusedNodeId) {
        const sourceId = getNodeId(link.source);
        const targetId = getNodeId(link.target);

        if (sourceId === focusedNodeId || targetId === focusedNodeId) {
          opacity = 0.9;
        } else if (connectedNodeIds.has(sourceId) && connectedNodeIds.has(targetId)) {
          opacity = 0.5;
        } else {
          opacity = OPACITY_DIMMED;
        }
      }

      const material = createLineMaterial(color, dashed, opacity);

      const geometry = new THREE.BufferGeometry();
      const positions = new Float32Array(6);
      geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

      const line = new THREE.Line(geometry, material);

      if (dashed && material instanceof THREE.LineDashedMaterial) {
        line.computeLineDistances();
      }

      return line;
    },
    [focusedNodeId, connectedNodeIds]
  );

  const linkPositionUpdate = useCallback(
    (
      obj: THREE.Object3D,
      coords: { start: { x: number; y: number; z: number }; end: { x: number; y: number; z: number } }
    ) => {
      const line = obj as THREE.Line;
      const positions = line.geometry?.attributes?.position;
      if (!positions) return false;

      const array = positions.array as Float32Array;
      array[0] = coords.start.x;
      array[1] = coords.start.y;
      array[2] = coords.start.z;
      array[3] = coords.end.x;
      array[4] = coords.end.y;
      array[5] = coords.end.z;

      positions.needsUpdate = true;
      line.geometry.computeBoundingSphere();

      if (line.material instanceof THREE.LineDashedMaterial) {
        line.computeLineDistances();
      }

      return true;
    },
    []
  );

  const linkDirectionalParticles = useCallback(
    (link: LinkObject) => {
      if (!isPlaying) return 0;
      const graphLink = link as GraphLink;
      return graphLink.edge_type === 'flow' ? 3 : 0;
    },
    [isPlaying]
  );

  const linkDirectionalParticleSpeed = useCallback(() => 0.005 * playbackSpeed, [playbackSpeed]);

  const linkDirectionalParticleWidth = useCallback(() => 2, []);

  const linkDirectionalParticleColor = useCallback((link: LinkObject) => {
    const graphLink = link as GraphLink;
    return graphLink.color || WINE_COLOR;
  }, []);

  const handleViewModeChange = useCallback((mode: Graph3DViewMode) => {
    setViewMode(mode);
    initialFitDone.current = false;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!webglSupported && viewMode !== '2d') {
    return (
      <div
        ref={containerRef}
        className={`h-full w-full bg-neutral-900 flex items-center justify-center ${className || ''}`}
      >
        <div className="text-center text-white p-4">
          <p className="text-lg font-medium mb-2">WebGL Not Available</p>
          <p className="text-sm text-gray-400">
            3D visualization requires WebGL support.
          </p>
          <button
            onClick={() => setViewMode('2d')}
            className="mt-4 px-4 py-2 bg-[#722F37] text-white rounded-lg hover:bg-[#5D262D] transition-colors"
          >
            Switch to 2D View
          </button>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={`h-full w-full bg-neutral-900 relative ${className || ''}`}
    >
      <div className="absolute top-4 right-4 z-10 flex gap-1 bg-black/50 rounded-lg p-1 backdrop-blur-sm">
        {(['3d', 'topdown', 'timeline', '2d'] as const).map((mode) => (
          <button
            key={mode}
            onClick={() => handleViewModeChange(mode)}
            className={`px-3 py-1.5 text-xs font-medium rounded transition-colors ${
              viewMode === mode
                ? 'bg-[#722F37] text-white'
                : 'text-gray-300 hover:bg-white/10'
            }`}
            disabled={mode !== '2d' && !webglSupported}
          >
            {mode === '3d'
              ? '3D'
              : mode === 'topdown'
                ? 'Top-Down'
                : mode === 'timeline'
                  ? 'Timeline'
                  : '2D'}
          </button>
        ))}
      </div>

      {focusedNodeId && (
        <div className="absolute top-4 left-4 z-10 bg-black/50 rounded-lg px-3 py-2 backdrop-blur-sm">
          <p className="text-xs text-gray-400">Focused on:</p>
          <p className="text-sm text-white font-medium">
            {nodeMap.get(focusedNodeId)?.label || focusedNodeId}
          </p>
          <button
            onClick={() => setFocusedNodeId(null)}
            className="text-xs text-[#C06C84] hover:text-[#C06C84]/80 mt-1"
          >
            Clear focus
          </button>
        </div>
      )}

      <ForceGraph3DComponent
        ref={fgRef as MutableRefObject<ForceGraphMethods | undefined>}
        width={dimensions.width}
        height={dimensions.height}
        graphData={graphData}
        backgroundColor={BACKGROUND_COLOR}
        nodeThreeObject={nodeThreeObject}
        nodeThreeObjectExtend={false}
        linkThreeObject={linkThreeObject}
        linkThreeObjectExtend={false}
        linkPositionUpdate={linkPositionUpdate}
        linkDirectionalParticles={linkDirectionalParticles}
        linkDirectionalParticleSpeed={linkDirectionalParticleSpeed}
        linkDirectionalParticleWidth={linkDirectionalParticleWidth}
        linkDirectionalParticleColor={linkDirectionalParticleColor}
        onNodeClick={handleNodeClick}
        enableNodeDrag={true}
        enableNavigationControls={true}
        showNavInfo={false}
        warmupTicks={50}
        cooldownTicks={100}
        d3AlphaDecay={0.02}
        d3VelocityDecay={0.3}
      />
    </div>
  );
};

export default GraphView3D;
