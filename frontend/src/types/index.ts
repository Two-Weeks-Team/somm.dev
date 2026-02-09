export type EvaluationStatus = 'pending' | 'processing' | 'completed' | 'failed';

export type CriteriaType = 'basic' | 'hackathon' | 'academic' | 'custom';

export type EvaluationMode = 'six_sommeliers' | 'grand_tasting' | 'full_techniques';

export interface EvaluationRequest {
  repoUrl: string;
  criteria: CriteriaType;
  evaluationMode: EvaluationMode;
}

export interface SommelierResult {
  id: string;
  name: string;
  role: string;
  score: number;
  feedback: string;
  recommendations?: string[];
  pairingSuggestion?: string;
}

export interface EvaluationResult {
  id: string;
  repoUrl: string;
  status: EvaluationStatus;
  createdAt: string;
  completedAt?: string;
  results: SommelierResult[];
  finalVerdict?: string;
  totalScore?: number;
  tier?: string;
}

export interface EvaluationHistoryItem {
  id: string;
  repoUrl: string;
  createdAt: string;
  status: EvaluationStatus;
  totalScore?: number;
}

export type SSEEventType =
  | 'sommelier_start'
  | 'sommelier_complete'
  | 'sommelier_error'
  | 'sommelier_retry'
  | 'evaluation_complete'
  | 'evaluation_error'
  | 'heartbeat'
  | 'status'
  | 'sommelier'
  | 'error'
  | 'complete'
  | 'technique_start'
  | 'technique_complete'
  | 'technique_error'
  | 'category_start'
  | 'category_complete'
  | 'deep_synthesis_start'
  | 'deep_synthesis_complete'
  | 'quality_gate_complete'
  | 'metrics_update';

export interface SSEEvent {
  event_type: SSEEventType;
  evaluation_id: string;
  sommelier?: string;
  message?: string;
  progress_percent?: number;
  tokens_used?: number;
  cost_usd?: number;
  timestamp?: string;
  // Full Techniques specific fields
  technique_id?: string;
  technique_name?: string;
  category_id?: string;
  category_name?: string;
  score?: number;
  max_score?: number;
  confidence?: string;
  duration_ms?: number;
  quality_gate?: string;
  total_score?: number;
  error?: string;
}

export interface ItemData {
  id: string;
  name: string;
  score: number;
  maxScore: number;
  confidence: string;
  evidence?: string[];
  rationale?: string;
}

export interface DimensionData {
  id: string;
  name: string;
  score: number;
  maxScore: number;
  items: ItemData[];
}

export interface FullTechniqueResultData {
  evaluationId: string;
  evaluationMode: 'full_techniques';
  totalScore: number;
  normalizedScore: number;
  qualityGate: string;
  coverage: number;
  itemScores: Record<string, ItemData>;
  dimensionScores: Record<string, DimensionData>;
  techniquesUsed: string[];
  failedTechniques: {id: string; error: string}[];
  costSummary: {totalTokens: number; estimatedCost: number};
  durationMs: number;
}

export interface SommelierProgress {
  name: string;
  status: 'pending' | 'analyzing' | 'completed' | 'failed';
  result?: SommelierResult;
}

export * from './graph';
