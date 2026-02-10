import { useState, useEffect, useRef, useCallback } from 'react';
import { api } from '../lib/api';
import { SommelierResult, EvaluationStatus, SSEEvent } from '../types';

type ConnectionStatus = 'connecting' | 'open' | 'retrying' | 'failed';

interface RetryInfo {
  attempt: number;
  maxAttempts: number;
  nextRetryAt: Date | null;
}

interface UseEvaluationStreamResult {
  status: EvaluationStatus;
  completedSommeliers: SommelierResult[];
  errors: string[];
  isComplete: boolean;
  progress: number;
  currentSommelier: string | null;
  connectionStatus: ConnectionStatus;
  retryInfo: RetryInfo | null;
}

const SOMMELIER_NAMES: Record<string, { name: string; role: string }> = {
  marcel: { name: 'Marcel', role: 'Cellar Master' },
  isabella: { name: 'Isabella', role: 'Wine Critic' },
  heinrich: { name: 'Heinrich', role: 'Quality Inspector' },
  sofia: { name: 'Sofia', role: 'Vineyard Scout' },
  laurent: { name: 'Laurent', role: 'Winemaker' },
  jeanpierre: { name: 'Jean-Pierre', role: 'Master Sommelier' },
};

const TASTING_NOTE_NAMES: Record<string, { name: string; role: string }> = {
  aroma: { name: 'Aroma', role: 'Problem Analysis' },
  palate: { name: 'Palate', role: 'Innovation & Creativity' },
  body: { name: 'Body', role: 'Technical Depth' },
  finish: { name: 'Finish', role: 'User Experience' },
  balance: { name: 'Balance', role: 'Architecture & Design' },
  vintage: { name: 'Vintage', role: 'Market Opportunity' },
  terroir: { name: 'Terroir', role: 'Presentation Quality' },
  cellar: { name: 'Cellar', role: 'Final Synthesis' },
};

const TOTAL_SOMMELIERS = 6;
const TOTAL_TASTING_NOTES = 8;

export const useEvaluationStream = (evaluationId: string): UseEvaluationStreamResult => {
  const [status, setStatus] = useState<EvaluationStatus>('pending');
  const [completedSommeliers, setCompletedSommeliers] = useState<SommelierResult[]>([]);
  const [errors, setErrors] = useState<string[]>([]);
  const [isComplete, setIsComplete] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentSommelier, setCurrentSommelier] = useState<string | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('connecting');
  const [retryInfo, setRetryInfo] = useState<RetryInfo | null>(null);
  
  const progressRef = useRef(0);

  const isCompleteRef = useRef(isComplete);
  useEffect(() => {
    isCompleteRef.current = isComplete;
  }, [isComplete]);
  
  const updateProgressFromCompleted = useCallback((completedCount: number, hasActiveTask: boolean) => {
    const isTastingMode = completedSommeliers.some(s => s.id in TASTING_NOTE_NAMES);
    const total = isTastingMode ? TOTAL_TASTING_NOTES : TOTAL_SOMMELIERS;
    const baseProgress = Math.round((completedCount / total) * 100);
    const activeBonus = hasActiveTask ? 5 : 0;
    const newProgress = Math.min(99, baseProgress + activeBonus);
    
    if (newProgress > progressRef.current) {
      progressRef.current = newProgress;
      setProgress(newProgress);
    }
  }, [completedSommeliers]);

  const handleSSEEvent = useCallback((event: SSEEvent) => {
    const eventType = event.event_type;

    switch (eventType) {
      case 'sommelier_start':
        if (event.sommelier) {
          setCurrentSommelier(event.sommelier);
        }
        setStatus('processing');
        if (event.progress_percent != null && event.progress_percent >= 0) {
          const newProgress = event.progress_percent;
          if (newProgress > progressRef.current) {
            progressRef.current = newProgress;
            setProgress(newProgress);
          }
        } else {
          setCompletedSommeliers((prev) => {
            updateProgressFromCompleted(prev.length, true);
            return prev;
          });
        }
        break;

      case 'sommelier_complete':
        if (event.sommelier) {
          const sommelierInfo = SOMMELIER_NAMES[event.sommelier] || 
            TASTING_NOTE_NAMES[event.sommelier] || {
              name: event.sommelier,
              role: 'Evaluator',
            };
          setCompletedSommeliers((prev) => {
            if (prev.find((s) => s.id === event.sommelier)) return prev;
            const newList = [
              ...prev,
              {
                id: event.sommelier!,
                name: sommelierInfo.name,
                role: sommelierInfo.role,
                score: 0,
                feedback: event.message || `${sommelierInfo.name} analysis complete`,
              },
            ];
            if (event.progress_percent != null && event.progress_percent >= 0) {
              const newProgress = event.progress_percent;
              if (newProgress > progressRef.current) {
                progressRef.current = newProgress;
                setProgress(newProgress);
              }
            } else {
              updateProgressFromCompleted(newList.length, false);
            }
            return newList;
          });
          setCurrentSommelier(null);
        }
        break;

      case 'sommelier_error':
        if (event.message) {
          setErrors((prev) => [...prev, event.message!]);
        }
        if (event.sommelier) {
          setCurrentSommelier(null);
        }
        break;

      case 'sommelier_retry':
        break;

      case 'evaluation_complete':
        isCompleteRef.current = true;
        setIsComplete(true);
        setStatus('completed');
        progressRef.current = 100;
        setProgress(100);
        setCurrentSommelier(null);
        break;

      case 'evaluation_error':
        isCompleteRef.current = true;
        setIsComplete(true);
        setStatus('failed');
        setCurrentSommelier(null);
        if (event.message) {
          setErrors((prev) => [...prev, event.message!]);
        }
        break;

      case 'heartbeat':
        break;

      case 'status':
        break;

      case 'sommelier':
      case 'complete':
      case 'error':
        break;

      // Full techniques mode events - handled by useFullTechniquesStream
      // Silently ignore here to prevent console warnings
      case 'technique_start':
      case 'technique_complete':
      case 'technique_error':
      case 'category_start':
      case 'category_complete':
      case 'deep_synthesis_start':
      case 'deep_synthesis_complete':
      case 'quality_gate_complete':
      case 'enrichment_start':
      case 'enrichment_complete':
      case 'enrichment_error':
      case 'metrics_update':
        break;

      default:
        console.warn('Unknown event type:', eventType);
    }
  }, [updateProgressFromCompleted]);

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

      setConnectionStatus('connecting');

      eventSource = api.getEvaluationStream(
        evaluationId,
        (event) => {
          try {
            const parsedData: SSEEvent = JSON.parse(event.data);
            handleSSEEvent(parsedData);
            retryCount = 0;
            setConnectionStatus('open');
            setRetryInfo(null);
          } catch (err) {
            console.error('Error parsing SSE data:', err);
          }
        },
        () => {
          const readyState = eventSource?.readyState;
          const readyStateLabel = readyState === 0 ? 'CONNECTING' : readyState === 1 ? 'OPEN' : 'CLOSED';
          const isOnline = typeof navigator !== 'undefined' ? navigator.onLine : true;
          
          // Only log warning for expected disconnections, error for unexpected ones
          if (readyState === 2 && isOnline) {
            // Connection closed while online - might be server-side close
            console.warn('SSE connection closed:', {
              readyState: `${readyState} (${readyStateLabel})`,
              retryCount: retryCount + 1,
              maxRetries: MAX_RETRIES,
            });
          } else if (!isOnline) {
            console.warn('SSE offline - waiting for network');
          } else {
            console.warn('SSE connection issue:', {
              readyState: `${readyState} (${readyStateLabel})`,
              retryCount: retryCount + 1,
              isOnline,
            });
          }
          
          if (eventSource) eventSource.close();

          if (!isCompleteRef.current && retryCount < MAX_RETRIES) {
            retryCount += 1;
            const timeout = Math.min(Math.pow(2, retryCount) * 1000, 30000);
            const nextRetryAt = new Date(Date.now() + timeout);
            
            setConnectionStatus('retrying');
            setRetryInfo({ attempt: retryCount, maxAttempts: MAX_RETRIES, nextRetryAt });
            
            retryTimeout = setTimeout(() => {
              connect();
            }, timeout);
          } else if (retryCount >= MAX_RETRIES) {
            setConnectionStatus('failed');
            setRetryInfo(null);
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
    connectionStatus,
    retryInfo,
  };
};
