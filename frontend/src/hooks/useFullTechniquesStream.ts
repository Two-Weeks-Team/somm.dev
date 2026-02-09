import { useReducer, useEffect, useRef } from 'react';
import { SSEEvent } from '../types';

interface TechniqueStatus {
  id: string;
  name: string;
  category: string;
  status: 'queued' | 'running' | 'complete' | 'error';
  score?: number;
  maxScore?: number;
  confidence?: string;
  durationMs?: number;
  errorMessage?: string;
}

interface CategoryStatus {
  id: string;
  name: string;
  completed: number;
  total: number;
  status: 'pending' | 'running' | 'complete';
}

interface FullTechniquesStreamState {
  connectionStatus: 'connecting' | 'open' | 'retrying' | 'failed' | 'closed';
  retryCount: number;
  
  totalTechniques: number;
  completedTechniques: number;
  failedTechniques: number;
  progressPercent: number;
  
  currentStage: 'categories' | 'deep_synthesis' | 'quality_gate' | 'complete' | 'error';
  
  categories: Record<string, CategoryStatus>;
  
  techniques: Record<string, TechniqueStatus>;
  
  ledgerEvents: Array<{timestamp: string; message: string; type: string}>;
  
  isComplete: boolean;
  totalScore?: number;
  qualityGate?: string;
  error?: string;
  
  tokensUsed: number;
  costUsd: number;
  
  startedAt?: string;
  etaSeconds?: number;
}

const CATEGORIES: Record<string, { name: string; total: number }> = {
  aroma: { name: 'Problem Analysis', total: 11 },
  palate: { name: 'Innovation', total: 13 },
  body: { name: 'Risk Analysis', total: 7 },
  finish: { name: 'User-Centricity', total: 7 },
  balance: { name: 'Feasibility', total: 8 },
  vintage: { name: 'Opportunity', total: 8 },
  terroir: { name: 'Presentation', total: 6 },
  cellar: { name: 'Synthesis', total: 15 },
};

const INITIAL_CATEGORIES: Record<string, CategoryStatus> = Object.entries(CATEGORIES).reduce(
  (acc, [id, info]) => ({
    ...acc,
    [id]: {
      id,
      name: info.name,
      completed: 0,
      total: info.total,
      status: 'pending',
    },
  }),
  {}
);

const initialState: FullTechniquesStreamState = {
  connectionStatus: 'connecting',
  retryCount: 0,
  totalTechniques: Object.values(CATEGORIES).reduce((sum, cat) => sum + cat.total, 0),
  completedTechniques: 0,
  failedTechniques: 0,
  progressPercent: 0,
  currentStage: 'categories',
  categories: INITIAL_CATEGORIES,
  techniques: {},
  ledgerEvents: [],
  isComplete: false,
  tokensUsed: 0,
  costUsd: 0,
};

type Action =
  | { type: 'CONNECTION_CHANGE'; status: FullTechniquesStreamState['connectionStatus']; retryCount?: number }
  | { type: 'EVENT_RECEIVED'; event: SSEEvent }
  | { type: 'ERROR'; error: string };

function reducer(state: FullTechniquesStreamState, action: Action): FullTechniquesStreamState {
  switch (action.type) {
    case 'CONNECTION_CHANGE':
      return {
        ...state,
        connectionStatus: action.status,
        retryCount: action.retryCount ?? state.retryCount,
      };

    case 'ERROR':
      return {
        ...state,
        error: action.error,
        isComplete: true,
        currentStage: 'error',
      };

    case 'EVENT_RECEIVED': {
      const { event } = action;
      const newState = { ...state };
      
      if (event.tokens_used) newState.tokensUsed = event.tokens_used;
      if (event.cost_usd) newState.costUsd = event.cost_usd;

      if (event.message) {
        newState.ledgerEvents = [
          {
            timestamp: event.timestamp || new Date().toISOString(),
            message: event.message,
            type: event.event_type,
          },
          ...state.ledgerEvents,
        ].slice(0, 20);
      }

      switch (event.event_type) {
        case 'technique_start':
          if (event.technique_id && event.technique_name && event.category_id) {
            newState.techniques = {
              ...state.techniques,
              [event.technique_id]: {
                id: event.technique_id,
                name: event.technique_name,
                category: event.category_id,
                status: 'running',
              },
            };
          }
          break;

        case 'technique_complete':
          if (event.technique_id) {
            const technique = state.techniques[event.technique_id];
            if (technique) {
              newState.techniques = {
                ...state.techniques,
                [event.technique_id]: {
                  ...technique,
                  status: 'complete',
                  score: event.score,
                  maxScore: event.max_score,
                  confidence: event.confidence,
                  durationMs: event.duration_ms,
                },
              };
              
              newState.completedTechniques = state.completedTechniques + 1;
              newState.progressPercent = Math.round(
                (newState.completedTechniques / state.totalTechniques) * 100
              );

              if (technique.category && newState.categories[technique.category]) {
                const cat = newState.categories[technique.category];
                newState.categories = {
                  ...newState.categories,
                  [technique.category]: {
                    ...cat,
                    completed: cat.completed + 1,
                  },
                };
              }
            }
          }
          break;

        case 'technique_error':
          if (event.technique_id) {
            const technique = state.techniques[event.technique_id];
            if (technique) {
              newState.techniques = {
                ...state.techniques,
                [event.technique_id]: {
                  ...technique,
                  status: 'error',
                  errorMessage: event.error,
                },
              };
              newState.failedTechniques = state.failedTechniques + 1;
            }
          }
          break;

        case 'category_start':
          if (event.category_id && newState.categories[event.category_id]) {
            newState.categories = {
              ...newState.categories,
              [event.category_id]: {
                ...newState.categories[event.category_id],
                status: 'running',
              },
            };
          }
          break;

        case 'category_complete':
          if (event.category_id && newState.categories[event.category_id]) {
            newState.categories = {
              ...newState.categories,
              [event.category_id]: {
                ...newState.categories[event.category_id],
                status: 'complete',
              },
            };
          }
          break;

        case 'deep_synthesis_start':
          newState.currentStage = 'deep_synthesis';
          break;

        case 'deep_synthesis_complete':
          break;

        case 'quality_gate_complete':
          newState.currentStage = 'quality_gate';
          if (event.total_score) newState.totalScore = event.total_score;
          if (event.quality_gate) newState.qualityGate = event.quality_gate;
          break;

        case 'evaluation_complete':
          newState.isComplete = true;
          newState.currentStage = 'complete';
          newState.progressPercent = 100;
          break;

        case 'evaluation_error':
          newState.isComplete = true;
          newState.currentStage = 'error';
          newState.error = event.error || event.message || 'Unknown error';
          break;
      }

      return newState;
    }

    default:
      return state;
  }
}

export function useFullTechniquesStream(evaluationId: string | null) {
  const [state, dispatch] = useReducer(reducer, initialState);
  const eventSourceRef = useRef<EventSource | null>(null);
  const retryTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const retryCountRef = useRef(0);

  useEffect(() => {
    if (!evaluationId || state.isComplete) return;

    retryCountRef.current = 0;

    const connect = () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || '';
      const url = `${apiUrl}/api/evaluate/${evaluationId}/stream`;
      
      dispatch({ type: 'CONNECTION_CHANGE', status: 'connecting' });
      
      const eventSource = new EventSource(url, { withCredentials: true });
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        dispatch({ type: 'CONNECTION_CHANGE', status: 'open', retryCount: 0 });
        retryCountRef.current = 0;
      };

      eventSource.onmessage = (event) => {
        try {
          const parsedData: SSEEvent = JSON.parse(event.data);
          dispatch({ type: 'EVENT_RECEIVED', event: parsedData });
        } catch (err) {
          console.error('Error parsing SSE data:', err);
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
        
        if (state.isComplete) return;

        const maxRetries = 5;
        if (retryCountRef.current < maxRetries) {
          const nextRetryCount = retryCountRef.current + 1;
          retryCountRef.current = nextRetryCount;
          
          const timeout = Math.min(Math.pow(2, nextRetryCount) * 1000, 30000);
          
          dispatch({ 
            type: 'CONNECTION_CHANGE', 
            status: 'retrying', 
            retryCount: nextRetryCount 
          });

          retryTimeoutRef.current = setTimeout(connect, timeout);
        } else {
          dispatch({ type: 'CONNECTION_CHANGE', status: 'failed' });
          dispatch({ type: 'ERROR', error: 'Connection lost. Please refresh the page.' });
        }
      };
    };

    connect();

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
      }
    };
  }, [evaluationId, state.isComplete]);

  return state;
}
