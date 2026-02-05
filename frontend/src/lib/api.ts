import { EvaluationResult, EvaluationHistoryItem, CriteriaType } from '../types';

const BASE_API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

async function fetchWithConfig(endpoint: string, options: RequestInit = {}) {
  const url = `${BASE_API_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || `API Error: ${response.statusText}`);
  }

  return response.json();
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
};
