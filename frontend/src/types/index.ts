export type EvaluationStatus = 'pending' | 'processing' | 'completed' | 'failed';

export type CriteriaType = 'basic' | 'hackathon' | 'academic' | 'custom';

export interface EvaluationRequest {
  repoUrl: string;
  criteria: CriteriaType;
}

export interface SommelierResult {
  id: string;
  name: string;
  role: string;
  score: number;
  feedback: string;
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

export interface SSEEvent {
  type: 'status' | 'sommelier' | 'error' | 'complete';
  data: unknown;
}

export interface SommelierProgress {
  name: string;
  status: 'pending' | 'analyzing' | 'completed' | 'failed';
  result?: SommelierResult;
}
