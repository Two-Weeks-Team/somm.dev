import { 
  EvaluationResult, 
  EvaluationHistoryItem, 
  CriteriaType, 
  EvaluationMode,
  ReactFlowGraph,
  Graph3DPayload,
  TraceEvent,
  ModeResponse
} from '../types';

export interface KeyStatusResponse {
  provider: string;
  key_hint: string;
  registered_at: string | null;
  expires_at: string | null;
  last_used_at: string | null;
  usage_count: number;
}

export interface RegisterKeyResponse {
  valid: boolean;
  key_hint: string;
  provider: string;
  expires_at: string | null;
}

export interface ValidateKeyResponse {
  valid: boolean;
  error: string | null;
  models_available: string[];
}

const BASE_API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.somm.dev';
const TOKEN_STORAGE_KEY = 'somm_auth_token';

interface BackendSommelierOutput {
  sommelier_name?: string;
  score?: number;
  summary?: string;
  recommendations?: string[];
}

interface BackendHistoryItem {
  id: string;
  repo_context?: { repo_url?: string };
  created_at: string;
  status: string;
  score?: number;
}

export class AuthError extends Error {
  constructor(message: string = 'Authentication required') {
    super(message);
    this.name = 'AuthError';
  }
}

async function fetchWithConfig(endpoint: string, options: RequestInit = {}, token?: string) {
  const url = `${BASE_API_URL}${endpoint}`;
  const storedToken = typeof window !== 'undefined' ? localStorage.getItem(TOKEN_STORAGE_KEY) : null;
  const authToken = token || storedToken || undefined;
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...options.headers as Record<string, string>,
  };

  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      throw new AuthError('Authentication required. Please login again.');
    }
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || `API Error: ${response.statusText}`);
  }

  return response.json();
}

export interface RepositoryOwner {
  login: string;
  type: 'User' | 'Organization';
  avatar_url: string | null;
}

export interface Repository {
  id: number;
  name: string;
  full_name: string;
  description: string | null;
  private: boolean;
  html_url: string;
  default_branch: string;
  stars: number;
  forks: number;
  language: string | null;
  updated_at: string | null;
  pushed_at: string | null;
  owner: RepositoryOwner | null;
}

export interface RepositoryListResponse {
  repositories: Repository[];
  total: number;
  cached_at: string | null;
}

export interface User {
  id: string;
  github_id: string;
  username: string;
  email?: string;
  avatar_url?: string;
  created_at?: string;
}

export const api = {
  startEvaluation: async (repoUrl: string, criteria: CriteriaType, evaluationMode: EvaluationMode = 'six_sommeliers'): Promise<{ id: string }> => {
    const response = await fetchWithConfig('/api/evaluate', {
      method: 'POST',
      body: JSON.stringify({ repo_url: repoUrl, criteria, evaluation_mode: evaluationMode }),
    });
    return { id: response.evaluation_id };
  },

  getEvaluationStream: (evaluationId: string, onMessage: (event: MessageEvent) => void, onError?: (error: Event) => void): EventSource => {
    const token = typeof window !== 'undefined' ? localStorage.getItem(TOKEN_STORAGE_KEY) : null;
    const url = token 
      ? `${BASE_API_URL}/api/evaluate/${evaluationId}/stream?token=${encodeURIComponent(token)}`
      : `${BASE_API_URL}/api/evaluate/${evaluationId}/stream`;
    const eventSource = new EventSource(url);

    eventSource.onmessage = onMessage;
    
    if (onError) {
      eventSource.onerror = onError;
    }

    return eventSource;
  },

  getEvaluationResult: async (evaluationId: string): Promise<EvaluationResult> => {
    const response = await fetchWithConfig(`/api/evaluate/${evaluationId}/result`);

    const SOMMELIER_ROLES: Record<string, string> = {
      'Marcel': 'Cellar Master',
      'Isabella': 'Wine Critic',
      'Heinrich': 'Quality Inspector',
      'Sofia': 'Vineyard Scout',
      'Laurent': 'Winemaker',
      'Aroma Notes': 'Problem Analysis',
      'Palate Notes': 'Innovation',
      'Body Notes': 'Risk Analysis',
      'Finish Notes': 'User-Centricity',
      'Balance Notes': 'Feasibility',
      'Vintage Notes': 'Opportunity',
      'Terroir Notes': 'Presentation',
    };

    const sommelierOutputs = response.final_evaluation?.sommelier_outputs || [];
    const results = sommelierOutputs.map((output: BackendSommelierOutput) => ({
      id: output.sommelier_name?.toLowerCase().replace(/[^a-z]/g, '') || '',
      name: output.sommelier_name || '',
      role: SOMMELIER_ROLES[output.sommelier_name || ''] || 'Sommelier',
      score: output.score || 0,
      feedback: output.summary || '',
      recommendations: output.recommendations || [],
      pairingSuggestion: output.recommendations?.[0] || undefined,
    }));

    return {
      id: response.evaluation_id,
      repoUrl: '',
      status: 'completed',
      createdAt: response.created_at,
      finalVerdict: response.final_evaluation?.summary || '',
      totalScore: response.final_evaluation?.overall_score || 0,
      tier: response.final_evaluation?.rating_tier || '',
      results,
    };
  },

  getHistory: async (page: number = 1, limit: number = 10): Promise<{ items: EvaluationHistoryItem[], total: number }> => {
    const skip = (page - 1) * limit;
    const queryParams = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    const response = await fetchWithConfig(`/api/history?${queryParams.toString()}`);

    const items = response.items.map((item: BackendHistoryItem) => ({
      id: item.id,
      repoUrl: item.repo_context?.repo_url || '',
      createdAt: item.created_at,
      status: item.status,
      totalScore: item.score,
    }));

    return { items, total: response.total };
  },

  // Authenticated API methods
  getRepositories: async (token: string): Promise<RepositoryListResponse> => {
    return fetchWithConfig('/repositories', {}, token);
  },

  refreshRepositories: async (token: string): Promise<RepositoryListResponse> => {
    return fetchWithConfig('/repositories/refresh', {
      method: 'POST',
    }, token);
  },

  getCurrentUser: async (token: string): Promise<User> => {
    return fetchWithConfig('/auth/me', {}, token);
  },

  getGraph: async (evaluationId: string, refresh?: boolean): Promise<ReactFlowGraph> => {
    const queryParams = refresh ? '?refresh=true' : '';
    return fetchWithConfig(`/api/evaluate/${evaluationId}/graph${queryParams}`);
  },

  getGraphStructure: async (evaluationId: string): Promise<ReactFlowGraph> => {
    return fetchWithConfig(`/api/evaluate/${evaluationId}/graph/structure`);
  },

  getGraphExecution: async (evaluationId: string): Promise<ReactFlowGraph> => {
    return fetchWithConfig(`/api/evaluate/${evaluationId}/graph/execution`);
  },

  getGraph3D: async (evaluationId: string, refresh?: boolean): Promise<Graph3DPayload> => {
    const queryParams = refresh ? '?refresh=true' : '';
    return fetchWithConfig(`/api/evaluate/${evaluationId}/graph-3d${queryParams}`);
  },

  getTimeline: async (evaluationId: string): Promise<TraceEvent[]> => {
    return fetchWithConfig(`/api/evaluate/${evaluationId}/graph/timeline`);
  },

  getGraphMode: async (evaluationId: string): Promise<ModeResponse> => {
    return fetchWithConfig(`/api/evaluate/${evaluationId}/graph/mode`);
  },

  // API Key methods
  registerKey: async (provider: string, apiKey: string): Promise<RegisterKeyResponse> => {
    return fetchWithConfig('/api/keys/register', {
      method: 'POST',
      body: JSON.stringify({ provider, api_key: apiKey }),
    });
  },

  getKeyStatus: async (): Promise<KeyStatusResponse[]> => {
    return fetchWithConfig('/api/keys/status');
  },

  deleteKey: async (provider: string): Promise<{ deleted: boolean; provider: string }> => {
    return fetchWithConfig(`/api/keys/${provider}`, {
      method: 'DELETE',
    });
  },

  validateKey: async (provider: string, apiKey: string): Promise<ValidateKeyResponse> => {
    return fetchWithConfig('/api/keys/validate', {
      method: 'POST',
      body: JSON.stringify({ provider, api_key: apiKey }),
    });
  },
};
