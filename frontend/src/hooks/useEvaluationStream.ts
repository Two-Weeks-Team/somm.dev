import { useState, useEffect, useRef, useCallback } from 'react';
import { api } from '../lib/api';
import { SommelierResult, EvaluationStatus, SSEEvent } from '../types';

interface UseEvaluationStreamResult {
  status: EvaluationStatus;
  completedSommeliers: SommelierResult[];
  errors: string[];
  isComplete: boolean;
  progress: number;
  currentSommelier: string | null;
}

const SOMMELIER_NAMES: Record<string, { name: string; role: string }> = {
  marcel: { name: 'Marcel', role: 'Cellar Master' },
  isabella: { name: 'Isabella', role: 'Wine Critic' },
  heinrich: { name: 'Heinrich', role: 'Quality Inspector' },
  sofia: { name: 'Sofia', role: 'Vineyard Scout' },
  laurent: { name: 'Laurent', role: 'Winemaker' },
  jeanpierre: { name: 'Jean-Pierre', role: 'Master Sommelier' },
};

export const useEvaluationStream = (evaluationId: string): UseEvaluationStreamResult => {
  const [status, setStatus] = useState<EvaluationStatus>('pending');
  const [completedSommeliers, setCompletedSommeliers] = useState<SommelierResult[]>([]);
  const [errors, setErrors] = useState<string[]>([]);
  const [isComplete, setIsComplete] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentSommelier, setCurrentSommelier] = useState<string | null>(null);

  const isCompleteRef = useRef(isComplete);
  useEffect(() => {
    isCompleteRef.current = isComplete;
  }, [isComplete]);

  const handleSSEEvent = useCallback((event: SSEEvent) => {
    const eventType = event.event_type;

    switch (eventType) {
      case 'sommelier_start':
        if (event.progress_percent !== undefined && event.progress_percent >= 0) {
          setProgress(event.progress_percent);
        }
        if (event.sommelier) {
          setCurrentSommelier(event.sommelier);
        }
        setStatus('processing');
        break;

      case 'sommelier_complete':
        if (event.progress_percent !== undefined && event.progress_percent >= 0) {
          setProgress(event.progress_percent);
        }
        if (event.sommelier) {
          const sommelierInfo = SOMMELIER_NAMES[event.sommelier] || {
            name: event.sommelier,
            role: 'Sommelier',
          };
          setCompletedSommeliers((prev) => {
            if (prev.find((s) => s.id === event.sommelier)) return prev;
            return [
              ...prev,
              {
                id: event.sommelier!,
                name: sommelierInfo.name,
                role: sommelierInfo.role,
                score: 0,
                feedback: event.message || `${sommelierInfo.name} analysis complete`,
              },
            ];
          });
          setCurrentSommelier(null);
        }
        break;

      case 'sommelier_error':
        if (event.progress_percent !== undefined && event.progress_percent >= 0) {
          setProgress(event.progress_percent);
        }
        if (event.message) {
          setErrors((prev) => [...prev, event.message!]);
        }
        if (event.sommelier) {
          setCurrentSommelier(null);
        }
        break;

      case 'evaluation_complete':
        setIsComplete(true);
        setStatus('completed');
        setProgress(100);
        setCurrentSommelier(null);
        break;

      case 'heartbeat':
        break;

      case 'status':
        break;

      case 'sommelier':
      case 'complete':
      case 'error':
        break;

      default:
        console.warn('Unknown event type:', eventType);
    }
  }, []);

  useEffect(() => {
    if (!evaluationId || isCompleteRef.current) return;

    let eventSource: EventSource | null = null;
    let retryTimeout: NodeJS.Timeout | null = null;
    let retryCount = 0;
    const MAX_RETRIES = 5;

    const connect = () => {
      if (eventSource) {
        eventSource.close();
      }

      eventSource = api.getEvaluationStream(
        evaluationId,
        (event) => {
          try {
            const parsedData: SSEEvent = JSON.parse(event.data);
            handleSSEEvent(parsedData);
            retryCount = 0;
          } catch (err) {
            console.error('Error parsing SSE data:', err);
          }
        },
        (error) => {
          console.error('SSE Error:', error);
          if (eventSource) eventSource.close();

          if (!isCompleteRef.current && retryCount < MAX_RETRIES) {
            retryCount += 1;
            const timeout = Math.min(Math.pow(2, retryCount) * 1000, 30000);
            retryTimeout = setTimeout(() => {
              console.log(`Retrying connection... (${retryCount}/${MAX_RETRIES})`);
              connect();
            }, timeout);
          } else if (retryCount >= MAX_RETRIES) {
            setErrors((prev) => [...prev, 'Connection lost. Please refresh the page.']);
          }
        }
      );
    };

    connect();

    return () => {
      if (eventSource) {
        eventSource.close();
      }
      if (retryTimeout) {
        clearTimeout(retryTimeout);
      }
    };
  }, [evaluationId, handleSSEEvent]);

  return {
    status,
    completedSommeliers,
    errors,
    isComplete,
    progress,
    currentSommelier,
  };
};
