import { useState, useEffect, useRef } from 'react';
import { api } from '../lib/api';
import { SommelierResult, EvaluationStatus, SSEEvent } from '../types';

interface UseEvaluationStreamResult {
  status: EvaluationStatus;
  completedSommeliers: SommelierResult[];
  errors: string[];
  isComplete: boolean;
  progress: number;
}

export const useEvaluationStream = (evaluationId: string): UseEvaluationStreamResult => {
  const [status, setStatus] = useState<EvaluationStatus>('pending');
  const [completedSommeliers, setCompletedSommeliers] = useState<SommelierResult[]>([]);
  const [errors, setErrors] = useState<string[]>([]);
  const [isComplete, setIsComplete] = useState(false);
  
  const progress = Math.min(100, Math.round((completedSommeliers.length / 6) * 100));

  const isCompleteRef = useRef(isComplete);
  useEffect(() => {
    isCompleteRef.current = isComplete;
  }, [isComplete]);

  useEffect(() => {
    if (!evaluationId || isCompleteRef.current) return;

    let eventSource: EventSource | null = null;
    let retryTimeout: NodeJS.Timeout | null = null;
    let retryCount = 0;
    const MAX_RETRIES = 3;

    const connect = () => {
      if (eventSource) {
        eventSource.close();
      }

      eventSource = api.getEvaluationStream(
        evaluationId,
        (event) => {
          try {
            const parsedData = JSON.parse(event.data);
            const { type, data } = parsedData as SSEEvent;

            switch (type) {
              case 'status':
                setStatus(data.status as EvaluationStatus);
                break;
              case 'sommelier':
                setCompletedSommeliers((prev) => {
                  const newResult = data as SommelierResult;
                  if (prev.find(s => s.id === newResult.id)) return prev;
                  return [...prev, newResult];
                });
                break;
              case 'error':
                setErrors((prev) => [...prev, (data as { message: string }).message]);
                break;
              case 'complete':
                setIsComplete(true);
                setStatus('completed');
                if (eventSource) eventSource.close();
                break;
              default:
                console.warn('Unknown event type:', type);
            }
            
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
            const timeout = Math.pow(2, retryCount) * 1000;
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
  }, [evaluationId]);

  return {
    status,
    completedSommeliers,
    errors,
    isComplete,
    progress,
  };
};
