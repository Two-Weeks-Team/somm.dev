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
    return fetchWithConfig('/api/evaluate', {
      method: 'POST',
      body: JSON.stringify({ repoUrl, criteria }),
    });
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
    return fetchWithConfig(`/api/evaluate/${evaluationId}`);
  },

  getHistory: async (page: number = 1, limit: number = 10): Promise<{ items: EvaluationHistoryItem[], total: number }> => {
    const queryParams = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
    });
    return fetchWithConfig(`/api/history?${queryParams.toString()}`);
  },
};
