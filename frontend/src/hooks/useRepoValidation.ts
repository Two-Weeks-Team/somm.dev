import { useState, useEffect, useCallback, useRef } from 'react';

export type ValidationStatus = 'idle' | 'checking' | 'valid' | 'invalid' | 'private' | 'error';

interface ValidationState {
  status: ValidationStatus;
  message: string | null;
}

interface UseRepoValidationReturn {
  validation: ValidationState;
  validateRepo: (url: string) => void;
  clearValidation: () => void;
}

const GITHUB_URL_REGEX = /^https:\/\/github\.com\/[\w-]+\/[\w-.]+$/;

function parseGithubUrl(url: string): { owner: string; repo: string } | null {
  const match = url.match(/github\.com\/([\w-]+)\/([\w-.]+)/);
  if (!match) return null;
  return {
    owner: match[1],
    repo: match[2].replace(/\.git$/, ''),
  };
}

export function useRepoValidation(debounceMs: number = 500): UseRepoValidationReturn {
  const [validation, setValidation] = useState<ValidationState>({
    status: 'idle',
    message: null,
  });
  
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const clearValidation = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setValidation({ status: 'idle', message: null });
  }, []);

  const validateRepo = useCallback((url: string) => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    if (!url.trim()) {
      setValidation({ status: 'idle', message: null });
      return;
    }

    if (!GITHUB_URL_REGEX.test(url)) {
      setValidation({
        status: 'invalid',
        message: 'Please enter a valid GitHub URL (e.g., https://github.com/owner/repo)',
      });
      return;
    }

    const parsed = parseGithubUrl(url);
    if (!parsed) {
      setValidation({
        status: 'invalid',
        message: 'Could not parse GitHub URL',
      });
      return;
    }

    setValidation({ status: 'checking', message: 'Checking repository...' });

    timeoutRef.current = setTimeout(async () => {
      abortControllerRef.current = new AbortController();

      try {
        const response = await fetch(
          `https://api.github.com/repos/${parsed.owner}/${parsed.repo}`,
          {
            method: 'HEAD',
            signal: abortControllerRef.current.signal,
          }
        );

        if (response.status === 200) {
          setValidation({
            status: 'valid',
            message: 'Repository found and accessible',
          });
        } else if (response.status === 404) {
          setValidation({
            status: 'invalid',
            message: 'Repository not found',
          });
        } else if (response.status === 403) {
          const rateLimitRemaining = response.headers.get('x-ratelimit-remaining');
          if (rateLimitRemaining === '0') {
            setValidation({
              status: 'error',
              message: 'API rate limit exceeded. Please try again later.',
            });
          } else {
            setValidation({
              status: 'private',
              message: 'Repository exists but is private. Please login to access.',
            });
          }
        } else if (response.status === 401) {
          setValidation({
            status: 'private',
            message: 'Repository exists but requires authentication',
          });
        } else {
          setValidation({
            status: 'error',
            message: `Unexpected error: ${response.status}`,
          });
        }
      } catch (error) {
        if (error instanceof DOMException && error.name === 'AbortError') {
          return;
        }
        setValidation({
          status: 'error',
          message: 'Failed to validate repository. Please check your connection.',
        });
      }
    }, debounceMs);
  }, [debounceMs]);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return { validation, validateRepo, clearValidation };
}
