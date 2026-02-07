import {
  isReactFlowNode,
  isReactFlowGraph,
  isGraph3DPayload,
  isTraceEvent,
  ReactFlowNode,
  ReactFlowGraph,
  Graph3DPayload,
  TraceEvent,
  Graph3DEdge,
  ExcludedTechnique,
} from '@/types/graph';

describe('Type Guards', () => {
  describe('isReactFlowNode', () => {
    it('returns true for a valid ReactFlowNode', () => {
      const validNode: ReactFlowNode = {
        id: 'node-1',
        type: 'agent',
        position: { x: 100, y: 200 },
        data: { label: 'Test Node' },
      };
      expect(isReactFlowNode(validNode)).toBe(true);
    });

    it('returns false for null', () => {
      expect(isReactFlowNode(null)).toBe(false);
    });

    it('returns false for undefined', () => {
      expect(isReactFlowNode(undefined)).toBe(false);
    });

    it('returns false for a string', () => {
      expect(isReactFlowNode('not a node')).toBe(false);
    });

    it('returns false for a number', () => {
      expect(isReactFlowNode(123)).toBe(false);
    });

    it('returns false when id is missing', () => {
      const invalidNode = {
        type: 'agent',
        position: { x: 100, y: 200 },
        data: { label: 'Test Node' },
      };
      expect(isReactFlowNode(invalidNode)).toBe(false);
    });

    it('returns false when type is not a string', () => {
      const invalidNode = {
        id: 'node-1',
        type: 123,
        position: { x: 100, y: 200 },
        data: { label: 'Test Node' },
      };
      expect(isReactFlowNode(invalidNode)).toBe(false);
    });

    it('returns false when position is missing', () => {
      const invalidNode = {
        id: 'node-1',
        type: 'agent',
        data: { label: 'Test Node' },
      };
      expect(isReactFlowNode(invalidNode)).toBe(false);
    });

    it('returns false when position.x is not a number', () => {
      const invalidNode = {
        id: 'node-1',
        type: 'agent',
        position: { x: '100', y: 200 },
        data: { label: 'Test Node' },
      };
      expect(isReactFlowNode(invalidNode)).toBe(false);
    });

    it('returns false when position.y is not a number', () => {
      const invalidNode = {
        id: 'node-1',
        type: 'agent',
        position: { x: 100, y: '200' },
        data: { label: 'Test Node' },
      };
      expect(isReactFlowNode(invalidNode)).toBe(false);
    });

    it('returns false when data is null', () => {
      const invalidNode = {
        id: 'node-1',
        type: 'agent',
        position: { x: 100, y: 200 },
        data: null,
      };
      expect(isReactFlowNode(invalidNode)).toBe(false);
    });

    it('returns false for an empty object', () => {
      expect(isReactFlowNode({})).toBe(false);
    });
  });

  describe('isReactFlowGraph', () => {
    it('returns true for a valid ReactFlowGraph', () => {
      const validGraph: ReactFlowGraph = {
        graph_schema_version: 2,
        mode: 'six_hats',
        nodes: [
          {
            id: 'node-1',
            type: 'agent',
            position: { x: 100, y: 200 },
            data: { label: 'Test Node' },
          },
        ],
        edges: [
          {
            id: 'edge-1',
            source: 'node-1',
            target: 'node-2',
          },
        ],
      };
      expect(isReactFlowGraph(validGraph)).toBe(true);
    });

    it('returns false for null', () => {
      expect(isReactFlowGraph(null)).toBe(false);
    });

    it('returns false for undefined', () => {
      expect(isReactFlowGraph(undefined)).toBe(false);
    });

    it('returns false when graph_schema_version is not a number', () => {
      const invalidGraph = {
        graph_schema_version: '2',
        mode: 'six_hats',
        nodes: [],
        edges: [],
      };
      expect(isReactFlowGraph(invalidGraph)).toBe(false);
    });

    it('returns false when mode is not a string', () => {
      const invalidGraph = {
        graph_schema_version: 2,
        mode: 123,
        nodes: [],
        edges: [],
      };
      expect(isReactFlowGraph(invalidGraph)).toBe(false);
    });

    it('returns false when nodes is not an array', () => {
      const invalidGraph = {
        graph_schema_version: 2,
        mode: 'six_hats',
        nodes: 'not an array',
        edges: [],
      };
      expect(isReactFlowGraph(invalidGraph)).toBe(false);
    });

    it('returns false when edges is not an array', () => {
      const invalidGraph = {
        graph_schema_version: 2,
        mode: 'six_hats',
        nodes: [],
        edges: 'not an array',
      };
      expect(isReactFlowGraph(invalidGraph)).toBe(false);
    });

    it('returns false for an empty object', () => {
      expect(isReactFlowGraph({})).toBe(false);
    });

    it('returns true for graph with empty arrays', () => {
      const graph = {
        graph_schema_version: 2,
        mode: 'six_hats',
        nodes: [],
        edges: [],
      };
      expect(isReactFlowGraph(graph)).toBe(true);
    });
  });

  describe('isGraph3DPayload', () => {
    it('returns true for a valid Graph3DPayload', () => {
      const validPayload: Graph3DPayload = {
        graph_schema_version: 2,
        evaluation_id: 'eval-123',
        mode: 'full_techniques',
        nodes: [
          {
            node_id: 'node-1',
            node_type: 'agent',
            label: 'Test Node',
            position: { x: 0, y: 0, z: 0 },
            step_number: 1,
          },
        ],
        edges: [
          {
            edge_id: 'edge-1',
            source: 'node-1',
            target: 'node-2',
            edge_type: 'flow',
            width: 2,
            step_number: 1,
          },
        ],
        metadata: {
          x_range: [-10, 10],
          y_range: [-10, 10],
          z_range: [0, 5],
          total_nodes: 1,
          total_edges: 1,
          total_steps: 1,
          max_step_number: 1,
          graph_schema_version: 2,
          generated_at: '2024-01-01T00:00:00Z',
        },
      };
      expect(isGraph3DPayload(validPayload)).toBe(true);
    });

    it('returns false for null', () => {
      expect(isGraph3DPayload(null)).toBe(false);
    });

    it('returns false for undefined', () => {
      expect(isGraph3DPayload(undefined)).toBe(false);
    });

    it('returns false when evaluation_id is missing', () => {
      const invalidPayload = {
        graph_schema_version: 2,
        mode: 'full_techniques',
        nodes: [],
        edges: [],
        metadata: {},
      };
      expect(isGraph3DPayload(invalidPayload)).toBe(false);
    });

    it('returns false when evaluation_id is not a string', () => {
      const invalidPayload = {
        graph_schema_version: 2,
        evaluation_id: 123,
        mode: 'full_techniques',
        nodes: [],
        edges: [],
        metadata: {},
      };
      expect(isGraph3DPayload(invalidPayload)).toBe(false);
    });

    it('returns false when nodes is not an array', () => {
      const invalidPayload = {
        graph_schema_version: 2,
        evaluation_id: 'eval-123',
        mode: 'full_techniques',
        nodes: 'not an array',
        edges: [],
        metadata: {},
      };
      expect(isGraph3DPayload(invalidPayload)).toBe(false);
    });

    it('returns false when edges is not an array', () => {
      const invalidPayload = {
        graph_schema_version: 2,
        evaluation_id: 'eval-123',
        mode: 'full_techniques',
        nodes: [],
        edges: 'not an array',
        metadata: {},
      };
      expect(isGraph3DPayload(invalidPayload)).toBe(false);
    });

    it('returns false when metadata is null', () => {
      const invalidPayload = {
        graph_schema_version: 2,
        evaluation_id: 'eval-123',
        mode: 'full_techniques',
        nodes: [],
        edges: [],
        metadata: null,
      };
      expect(isGraph3DPayload(invalidPayload)).toBe(false);
    });

    it('returns false when metadata is missing', () => {
      const invalidPayload = {
        graph_schema_version: 2,
        evaluation_id: 'eval-123',
        mode: 'full_techniques',
        nodes: [],
        edges: [],
      };
      expect(isGraph3DPayload(invalidPayload)).toBe(false);
    });

    it('returns false for an empty object', () => {
      expect(isGraph3DPayload({})).toBe(false);
    });
  });

  describe('isTraceEvent', () => {
    it('returns true for a valid TraceEvent', () => {
      const validEvent: TraceEvent = {
        step: 1,
        timestamp: '2024-01-01T00:00:00Z',
        agent: 'Marcel',
        technique_id: 'tech-1',
        action: 'started',
      };
      expect(isTraceEvent(validEvent)).toBe(true);
    });

    it('returns true for a TraceEvent with optional fields', () => {
      const validEvent: TraceEvent = {
        step: 1,
        timestamp: '2024-01-01T00:00:00Z',
        agent: 'Marcel',
        technique_id: 'tech-1',
        action: 'completed',
        item_id: 'item-123',
        score_delta: 5,
        evidence_ref: 'evidence-456',
      };
      expect(isTraceEvent(validEvent)).toBe(true);
    });

    it('returns false for null', () => {
      expect(isTraceEvent(null)).toBe(false);
    });

    it('returns false for undefined', () => {
      expect(isTraceEvent(undefined)).toBe(false);
    });

    it('returns false when step is not a number', () => {
      const invalidEvent = {
        step: '1',
        timestamp: '2024-01-01T00:00:00Z',
        agent: 'Marcel',
        technique_id: 'tech-1',
        action: 'started',
      };
      expect(isTraceEvent(invalidEvent)).toBe(false);
    });

    it('returns false when timestamp is not a string', () => {
      const invalidEvent = {
        step: 1,
        timestamp: 1234567890,
        agent: 'Marcel',
        technique_id: 'tech-1',
        action: 'started',
      };
      expect(isTraceEvent(invalidEvent)).toBe(false);
    });

    it('returns false when agent is missing', () => {
      const invalidEvent = {
        step: 1,
        timestamp: '2024-01-01T00:00:00Z',
        technique_id: 'tech-1',
        action: 'started',
      };
      expect(isTraceEvent(invalidEvent)).toBe(false);
    });

    it('returns false when technique_id is not a string', () => {
      const invalidEvent = {
        step: 1,
        timestamp: '2024-01-01T00:00:00Z',
        agent: 'Marcel',
        technique_id: 123,
        action: 'started',
      };
      expect(isTraceEvent(invalidEvent)).toBe(false);
    });

    it('returns false when action is not a string', () => {
      const invalidEvent = {
        step: 1,
        timestamp: '2024-01-01T00:00:00Z',
        agent: 'Marcel',
        technique_id: 'tech-1',
        action: 123,
      };
      expect(isTraceEvent(invalidEvent)).toBe(false);
    });

    it('returns false for an empty object', () => {
      expect(isTraceEvent({})).toBe(false);
    });

    it('returns false for an array', () => {
      expect(isTraceEvent([])).toBe(false);
    });
  });

  describe('Graph3DEdge with control_points', () => {
    it('accepts edge with control_points field', () => {
      const edgeWithControlPoints: Graph3DEdge = {
        edge_id: 'edge-1',
        source: 'node-1',
        target: 'node-2',
        edge_type: 'flow',
        width: 2,
        step_number: 1,
        control_points: [
          { x: 0, y: 0, z: 0 },
          { x: 5, y: 2, z: 1 },
          { x: 10, y: 0, z: 0 },
        ],
      };

      expect(edgeWithControlPoints.control_points).toHaveLength(3);
      expect(edgeWithControlPoints.control_points![0]).toEqual({ x: 0, y: 0, z: 0 });
    });

    it('accepts edge without control_points field', () => {
      const edgeWithoutControlPoints: Graph3DEdge = {
        edge_id: 'edge-2',
        source: 'node-1',
        target: 'node-2',
        edge_type: 'parallel',
        width: 1,
        step_number: 2,
      };

      expect(edgeWithoutControlPoints.control_points).toBeUndefined();
    });

    it('accepts edge with bundled_path field', () => {
      const edgeWithBundledPath: Graph3DEdge = {
        edge_id: 'edge-3',
        source: 'node-1',
        target: 'node-3',
        edge_type: 'data',
        width: 1.5,
        step_number: 1,
        bundle_id: 'bundle-1',
        bundled_path: [
          { x: 0, y: 0, z: 0 },
          { x: 2, y: 3, z: 1 },
          { x: 5, y: 5, z: 2 },
        ],
      };

      expect(edgeWithBundledPath.bundled_path).toHaveLength(3);
      expect(edgeWithBundledPath.bundle_id).toBe('bundle-1');
    });
  });

  describe('ExcludedTechnique typing', () => {
    it('accepts valid ExcludedTechnique object', () => {
      const excluded: ExcludedTechnique = {
        technique_id: 'tech-xyz',
        reason: 'Not applicable to this evaluation',
      };

      expect(excluded.technique_id).toBe('tech-xyz');
      expect(excluded.reason).toBe('Not applicable to this evaluation');
    });

    it('validates Graph3DPayload with excluded_techniques array', () => {
      const payloadWithExcluded: Graph3DPayload = {
        graph_schema_version: 2,
        evaluation_id: 'eval-456',
        mode: 'full_techniques',
        nodes: [],
        edges: [],
        excluded_techniques: [
          { technique_id: 'tech-1', reason: 'Reason A' },
          { technique_id: 'tech-2', reason: 'Reason B' },
        ],
        metadata: {
          x_range: [-10, 10],
          y_range: [-10, 10],
          z_range: [0, 5],
          total_nodes: 0,
          total_edges: 0,
          total_steps: 0,
          max_step_number: 0,
          graph_schema_version: 2,
          generated_at: '2024-01-01T00:00:00Z',
        },
      };

      expect(isGraph3DPayload(payloadWithExcluded)).toBe(true);
      expect(payloadWithExcluded.excluded_techniques).toHaveLength(2);
      expect(payloadWithExcluded.excluded_techniques![0].technique_id).toBe('tech-1');
    });

    it('validates Graph3DPayload without excluded_techniques', () => {
      const payloadWithoutExcluded: Graph3DPayload = {
        graph_schema_version: 2,
        evaluation_id: 'eval-789',
        mode: 'six_hats',
        nodes: [],
        edges: [],
        metadata: {
          x_range: [-10, 10],
          y_range: [-10, 10],
          z_range: [0, 5],
          total_nodes: 0,
          total_edges: 0,
          total_steps: 0,
          max_step_number: 0,
          graph_schema_version: 2,
          generated_at: '2024-01-01T00:00:00Z',
        },
      };

      expect(isGraph3DPayload(payloadWithoutExcluded)).toBe(true);
      expect(payloadWithoutExcluded.excluded_techniques).toBeUndefined();
    });
  });

  describe('Type guards remain permissive', () => {
    it('isGraph3DPayload accepts payloads with extra fields', () => {
      const payloadWithExtra = {
        graph_schema_version: 2,
        evaluation_id: 'eval-extra',
        mode: 'six_hats',
        nodes: [],
        edges: [],
        metadata: {
          x_range: [-10, 10],
          y_range: [-10, 10],
          z_range: [0, 5],
          total_nodes: 0,
          total_edges: 0,
          total_steps: 0,
          max_step_number: 0,
          graph_schema_version: 2,
          generated_at: '2024-01-01T00:00:00Z',
        },
        some_future_field: 'extra data',
        another_field: { nested: true },
      };

      expect(isGraph3DPayload(payloadWithExtra)).toBe(true);
    });

    it('isReactFlowGraph accepts graphs with extra fields', () => {
      const graphWithExtra = {
        graph_schema_version: 2,
        mode: 'six_hats',
        nodes: [],
        edges: [],
        description: 'Optional description',
        meta: { custom: 'metadata' },
        future_field: 'some value',
      };

      expect(isReactFlowGraph(graphWithExtra)).toBe(true);
    });

    it('isTraceEvent accepts events with extra fields', () => {
      const eventWithExtra = {
        step: 1,
        timestamp: '2024-01-01T00:00:00Z',
        agent: 'Marcel',
        technique_id: 'tech-1',
        action: 'started',
        custom_field: 'extra',
        metrics: { score: 85 },
      };

      expect(isTraceEvent(eventWithExtra)).toBe(true);
    });
  });
});
