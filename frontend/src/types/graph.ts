export const GRAPH_SCHEMA_VERSION = 2;

export type GraphEvaluationMode = 'six_hats' | 'full_techniques';

export type Graph3DViewMode = '3d' | 'topdown' | 'timeline' | '2d';

export type ReactFlowNodeType = 
  | 'start' 
  | 'end' 
  | 'agent' 
  | 'technique' 
  | 'synthesis' 
  | 'process' 
  | 'rag';

export type NodeStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface ReactFlowNodeData {
  label: string;
  status?: NodeStatus;
  progress?: number;
  color?: string;
  hatType?: string;
  category?: string;
  tokenUsage?: number;
  costUsd?: number;
  isFuture?: boolean;
  [key: string]: unknown;
}

export interface ReactFlowNode {
  id: string;
  type: ReactFlowNodeType | string;
  position: { x: number; y: number };
  data: ReactFlowNodeData;
}

export interface ReactFlowEdge {
  id: string;
  source: string;
  target: string;
  animated?: boolean;
  style?: Record<string, unknown>;
  data?: {
    edge_type?: 'primary' | 'secondary' | 'excluded';
    weight?: number;
  };
}

export interface ReactFlowGraph {
  graph_schema_version: number;
  mode: GraphEvaluationMode | string;
  nodes: ReactFlowNode[];
  edges: ReactFlowEdge[];
  description?: string;
  meta?: Record<string, unknown>;
}

export interface Position3D {
  x: number;
  y: number;
  z: number;
}

export type Graph3DEdgeType = 'flow' | 'parallel' | 'data' | 'excluded';

export interface Graph3DNode {
  node_id: string;
  node_type: string;
  label: string;
  position: Position3D;
  color?: string;
  step_number: number;
  hat_type?: string;
  technique_id?: string;
  category?: string;
  item_count?: number;
  node_meta?: Record<string, unknown>;
}

export interface Graph3DEdge {
  edge_id: string;
  source: string;
  target: string;
  edge_type: Graph3DEdgeType | string;
  color?: string;
  width: number;
  step_number: number;
  bundle_id?: string;
  bundled_path?: Position3D[];
  control_points?: Position3D[];
  dasharray?: string;
}

export interface ExcludedTechnique {
  technique_id: string;
  reason: string;
}

export interface Graph3DMetadata {
  x_range: [number, number];
  y_range: [number, number];
  z_range: [number, number];
  total_nodes: number;
  total_edges: number;
  total_steps: number;
  max_step_number: number;
  graph_schema_version: number;
  generated_at: string;
}

export interface Graph3DPayload {
  graph_schema_version: number;
  evaluation_id: string;
  mode: GraphEvaluationMode | string;
  nodes: Graph3DNode[];
  edges: Graph3DEdge[];
  edges_raw?: Graph3DEdge[];
  excluded_techniques?: ExcludedTechnique[];
  metadata: Graph3DMetadata;
}

export interface TraceEvent {
  step: number;
  timestamp: string;
  agent: string;
  technique_id: string;
  item_id?: string;
  action: string;
  score_delta?: number;
  evidence_ref?: string;
}

export interface ModeResponse {
  mode: GraphEvaluationMode | string;
  evaluation_id: string;
}

export function isReactFlowNode(value: unknown): value is ReactFlowNode {
  if (typeof value !== 'object' || value === null) return false;
  const node = value as Record<string, unknown>;
  return (
    typeof node.id === 'string' &&
    typeof node.type === 'string' &&
    typeof node.position === 'object' &&
    node.position !== null &&
    typeof (node.position as Record<string, unknown>).x === 'number' &&
    typeof (node.position as Record<string, unknown>).y === 'number' &&
    typeof node.data === 'object' &&
    node.data !== null
  );
}

export function isReactFlowGraph(value: unknown): value is ReactFlowGraph {
  if (typeof value !== 'object' || value === null) return false;
  const graph = value as Record<string, unknown>;
  return (
    typeof graph.graph_schema_version === 'number' &&
    typeof graph.mode === 'string' &&
    Array.isArray(graph.nodes) &&
    Array.isArray(graph.edges)
  );
}

export function isGraph3DPayload(value: unknown): value is Graph3DPayload {
  if (typeof value !== 'object' || value === null) return false;
  const payload = value as Record<string, unknown>;
  return (
    typeof payload.graph_schema_version === 'number' &&
    typeof payload.evaluation_id === 'string' &&
    typeof payload.mode === 'string' &&
    Array.isArray(payload.nodes) &&
    Array.isArray(payload.edges) &&
    typeof payload.metadata === 'object' &&
    payload.metadata !== null
  );
}

export function isTraceEvent(value: unknown): value is TraceEvent {
  if (typeof value !== 'object' || value === null) return false;
  const event = value as Record<string, unknown>;
  return (
    typeof event.step === 'number' &&
    typeof event.timestamp === 'string' &&
    typeof event.agent === 'string' &&
    typeof event.technique_id === 'string' &&
    typeof event.action === 'string'
  );
}
