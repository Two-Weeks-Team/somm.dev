import { EvaluationResult, EvaluationHistoryItem, CriteriaType } from '../types';

const BASE_API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.somm.dev';

export class AuthError extends Error {
  constructor(message: string = 'Authentication required') {
    super(message);
    this.name = 'AuthError';
  }
}

async function fetchWithConfig(endpoint: string, options: RequestInit = {}, token?: string) {
  const url = `${BASE_API_URL}${endpoint}`;
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...options.headers as Record<string, string>,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
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
  startEvaluation: async (repoUrl: string, criteria: CriteriaType): Promise<{ id: string }> => {
    const response = await fetchWithConfig('/api/evaluate', {
      method: 'POST',
      body: JSON.stringify({ repo_url: repoUrl, criteria }),
    });
    // Backend returns { evaluation_id, status, estimated_time }
    // Frontend expects { id }
    return { id: response.evaluation_id };
  },

  getEvaluationStream: (evaluationId: string, onMessage: (event: MessageEvent) => void, onError?: (error: Event) => void): EventSource => {
    const url = `${BASE_API_URL}/api/evaluate/${evaluationId}/stream`;
    const eventSource = new EventSource(url);

    eventSource.onmessage = onMessage;
    
    if (onError) {
      eventSource.onerror = onError;
    }

    return eventSource;
  },

  getEvaluationResult: async (evaluationId: string): Promise<EvaluationResult> => {
    const response = await fetchWithConfig(`/api/evaluate/${evaluationId}/result`);
    // Transform backend response to frontend format
    return {
      id: response.evaluation_id,
      repoUrl: '', // Will be populated from evaluation data
      status: 'completed',
      createdAt: response.created_at,
      finalVerdict: response.final_evaluation?.summary || '',
      totalScore: response.final_evaluation?.overall_score || 0,
      tier: response.final_evaluation?.rating_tier || '',
      results: response.final_evaluation?.sommelier_outputs || [],
    };
  },

  getHistory: async (page: number = 1, limit: number = 10): Promise<{ items: EvaluationHistoryItem[], total: number }> => {
    const skip = (page - 1) * limit;
    const queryParams = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    const response = await fetchWithConfig(`/api/history?${queryParams.toString()}`);

    // Transform backend response to frontend format
    const items = response.items.map((item: any) => ({
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
};
