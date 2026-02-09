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
  | 'complete';

export interface SSEEvent {
  event_type: SSEEventType;
  evaluation_id: string;
  sommelier?: string;
  message?: string;
  progress_percent?: number;
  tokens_used?: number;
  cost_usd?: number;
  timestamp?: string;
}

export interface SommelierProgress {
  name: string;
  status: 'pending' | 'analyzing' | 'completed' | 'failed';
  result?: SommelierResult;
}

export * from './graph';
