/**
 * @jest-environment jsdom
 */

import { renderHook, waitFor } from '@testing-library/react';
import { useEvaluationStream } from '../src/hooks/useEvaluationStream';
import { EvaluationStatus, SSEEvent, SommelierResult } from '../src/types';

// Mock the api module
jest.mock('../src/lib/api', () => ({
  api: {
    getEvaluationStream: jest.fn(),
  },
}));

describe('useEvaluationStream Hook Tests', () => {
  const mockApi = require('../src/lib/api/api');

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should return initial state', () => {
    const mockEventSource = {
      close: jest.fn(),
    };
    (mockApi.getEvaluationStream as jest.Mock).mockReturnValue(mockEventSource);

    const { result } = renderHook(() => useEvaluationStream('eval_123'));

    expect(result.current.status).toBe('pending');
    expect(result.current.completedSommeliers).toEqual([]);
    expect(result.current.errors).toEqual([]);
    expect(result.current.isComplete).toBe(false);
    expect(result.current.progress).toBe(0);
  });

  it('should update status when status event is received', () => {
    const mockEventSource = {
      close: jest.fn(),
    };
    const mockSubscribe = (onMessage: (event: MessageEvent) => void) => {
      // Simulate status change
      setTimeout(() => {
        onMessage({
          data: JSON.stringify({
            type: 'status',
            data: { status: 'processing' },
          }),
        });
      }, 10);
    };

    (mockApi.getEvaluationStream as jest.Mock).mockReturnValue({
      ...mockEventSource,
      onmessage: null,
    });

    // We need to handle the subscription differently
    let callback: ((event: MessageEvent) => void) | null = null;
    (mockApi.getEvaluationStream as jest.Mock).mockImplementation((id, onMessage) => {
      callback = onMessage;
      return mockEventSource;
    });

    const { result } = renderHook(() => useEvaluationStream('eval_123'));

    // Simulate status event
    if (callback) {
      callback({
        data: JSON.stringify({
          type: 'status',
          data: { status: 'processing' },
        }),
      } as MessageEvent);
    }

    expect(result.current.status).toBe('processing');
  });

  it('should add sommelier result when sommelier event is received', () => {
    const mockEventSource = {
      close: jest.fn(),
    };

    let callback: ((event: MessageEvent) => void) | null = null;
    (mockApi.getEvaluationStream as jest.Mock).mockImplementation((id, onMessage) => {
      callback = onMessage;
      return mockEventSource;
    });

    const { result } = renderHook(() => useEvaluationStream('eval_123'));

    const sommelierResult: SommelierResult = {
      id: 'marcel',
      name: 'Marcel',
      role: 'Cellar Master',
      score: 85,
      feedback: 'Good structure',
    };

    // Simulate sommelier event
    if (callback) {
      callback({
        data: JSON.stringify({
          type: 'sommelier',
          data: sommelierResult,
        }),
      } as MessageEvent);
    }

    expect(result.current.completedSommeliers).toHaveLength(1);
    expect(result.current.completedSommeliers[0].id).toBe('marcel');
    expect(result.current.progress).toBe(17); // 1/6 * 100
  });

  it('should add error when error event is received', () => {
    const mockEventSource = {
      close: jest.fn(),
    };

    let callback: ((event: MessageEvent) => void) | null = null;
    (mockApi.getEvaluationStream as jest.Mock).mockImplementation((id, onMessage) => {
      callback = onMessage;
      return mockEventSource;
    });

    const { result } = renderHook(() => useEvaluationStream('eval_123'));

    // Simulate error event
    if (callback) {
      callback({
        data: JSON.stringify({
          type: 'error',
          data: { message: 'GitHub API rate limit exceeded' },
        }),
      } as MessageEvent);
    }

    expect(result.current.errors).toHaveLength(1);
    expect(result.current.errors[0]).toBe('GitHub API rate limit exceeded');
  });

  it('should mark as complete when complete event is received', () => {
    const mockEventSource = {
      close: jest.fn(),
    };

    let callback: ((event: MessageEvent) => void) | null = null;
    (mockApi.getEvaluationStream as jest.Mock).mockImplementation((id, onMessage) => {
      callback = onMessage;
      return mockEventSource;
    });

    const { result } = renderHook(() => useEvaluationStream('eval_123'));

    // Simulate complete event
    if (callback) {
      callback({
        data: JSON.stringify({
          type: 'complete',
          data: {},
        }),
      } as MessageEvent);
    }

    expect(result.current.isComplete).toBe(true);
    expect(result.current.status).toBe('completed');
    expect(mockEventSource.close).toHaveBeenCalled();
  });

  it('should not fetch when evaluationId is empty', () => {
    const { result } = renderHook(() => useEvaluationStream(''));

    expect(mockApi.getEvaluationStream).not.toHaveBeenCalled();
    expect(result.current.status).toBe('pending');
  });

  it('should close event source on cleanup', () => {
    const mockEventSource = {
      close: jest.fn(),
    };

    (mockApi.getEvaluationStream as jest.Mock).mockReturnValue(mockEventSource);

    const { unmount } = renderHook(() => useEvaluationStream('eval_123'));

    unmount();

    expect(mockEventSource.close).toHaveBeenCalled();
  });

  it('should not add duplicate sommelier results', () => {
    const mockEventSource = {
      close: jest.fn(),
    };

    let callback: ((event: MessageEvent) => void) | null = null;
    (mockApi.getEvaluationStream as jest.Mock).mockImplementation((id, onMessage) => {
      callback = onMessage;
      return mockEventSource;
    });

    const { result } = renderHook(() => useEvaluationStream('eval_123'));

    const sommelierResult: SommelierResult = {
      id: 'marcel',
      name: 'Marcel',
      role: 'Cellar Master',
      score: 85,
      feedback: 'Good structure',
    };

    // Send same sommelier twice
    if (callback) {
      callback({
        data: JSON.stringify({
          type: 'sommelier',
          data: sommelierResult,
        }),
      } as MessageEvent);

      callback({
        data: JSON.stringify({
          type: 'sommelier',
          data: sommelierResult,
        }),
      } as MessageEvent);
    }

    expect(result.current.completedSommeliers).toHaveLength(1);
  });

  it('should calculate progress correctly', () => {
    const mockEventSource = {
      close: jest.fn(),
    };

    let callback: ((event: MessageEvent) => void) | null = null;
    (mockApi.getEvaluationStream as jest.Mock).mockImplementation((id, onMessage) => {
      callback = onMessage;
      return mockEventSource;
    });

    const { result } = renderHook(() => useEvaluationStream('eval_123'));

    // Add 3 sommelier results (50% progress)
    const sommelierIds = ['marcel', 'isabella', 'heinrich'];

    sommelierIds.forEach((id) => {
      if (callback) {
        callback({
          data: JSON.stringify({
            type: 'sommelier',
            data: {
              id,
              name: id.charAt(0).toUpperCase() + id.slice(1),
              role: 'Test',
              score: 85,
              feedback: 'Good',
            },
          }),
        } as MessageEvent);
      }
    });

    expect(result.current.progress).toBe(50);
  });
});
