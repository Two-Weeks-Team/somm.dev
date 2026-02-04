/**
 * @jest-environment jsdom
 */

import { api } from '../src/lib/api';
import { EvaluationResult, EvaluationHistoryItem, CriteriaType } from '../types';

// Mock the global fetch and EventSource
global.fetch = jest.fn();
global.EventSource = jest.fn();

describe('API Client Tests', () => {
  const mockApiUrl = 'http://localhost:8080';

  beforeEach(() => {
    jest.clearAllMocks();
    // Reset environment variable
    delete process.env.NEXT_PUBLIC_API_URL;
  });

  describe('startEvaluation', () => {
    it('should successfully start an evaluation', async () => {
      const mockResponse = {
        evaluation_id: 'eval_123',
        status: 'pending',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await api.startEvaluation(
        'https://github.com/owner/repo',
        'basic'
      );

      expect(global.fetch).toHaveBeenCalledWith(
        `${mockApiUrl}/api/evaluate`,
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
          body: JSON.stringify({
            repoUrl: 'https://github.com/owner/repo',
            criteria: 'basic',
          }),
        })
      );

      expect(result).toEqual(mockResponse);
    });

    it('should throw error on failed evaluation', async () => {
      const mockError = { message: 'Invalid repository URL' };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => mockError,
      });

      await expect(
        api.startEvaluation('invalid-url', 'basic')
      ).rejects.toThrow('Invalid repository URL');
    });

    it('should include custom criteria when specified', async () => {
      const mockResponse = {
        evaluation_id: 'eval_custom',
        status: 'pending',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      await api.startEvaluation(
        'https://github.com/owner/repo',
        'custom',
        ['readability', 'performance']
      );

      expect(global.fetch).toHaveBeenCalledWith(
        `${mockApiUrl}/api/evaluate`,
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            repoUrl: 'https://github.com/owner/repo',
            criteria: 'custom',
            custom_criteria: ['readability', 'performance'],
          }),
        })
      );
    });
  });

  describe('getEvaluationResult', () => {
    it('should successfully get evaluation result', async () => {
      const mockResult: EvaluationResult = {
        id: 'eval_123',
        repoUrl: 'https://github.com/owner/repo',
        status: 'completed',
        createdAt: '2024-01-01T00:00:00Z',
        results: [],
        finalVerdict: 'Great project!',
        totalScore: 85,
        tier: 'Premier Cru',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResult,
      });

      const result = await api.getEvaluationResult('eval_123');

      expect(global.fetch).toHaveBeenCalledWith(
        `${mockApiUrl}/api/evaluate/eval_123`,
        expect.objectContaining({ method: 'GET' })
      );

      expect(result).toEqual(mockResult);
    });
  });

  describe('getHistory', () => {
    it('should successfully get evaluation history', async () => {
      const mockHistory = {
        items: [
          {
            id: 'eval_1',
            repoUrl: 'https://github.com/owner/repo1',
            createdAt: '2024-01-01T00:00:00Z',
            status: 'completed',
            totalScore: 85,
          },
        ],
        total: 1,
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockHistory,
      });

      const result = await api.getHistory(1, 10);

      expect(global.fetch).toHaveBeenCalledWith(
        `${mockApiUrl}/api/history?page=1&limit=10`,
        expect.objectContaining({ method: 'GET' })
      );

      expect(result).toEqual(mockHistory);
    });

    it('should use default pagination values', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ items: [], total: 0 }),
      });

      await api.getHistory();

      expect(global.fetch).toHaveBeenCalledWith(
        `${mockApiUrl}/api/history?page=1&limit=10`,
        expect.any(Object)
      );
    });
  });

  describe('getEvaluationStream', () => {
    it('should create EventSource with correct URL', () => {
      const mockOnMessage = jest.fn();
      const mockOnError = jest.fn();

      // Clear the mock and set up the constructor mock properly
      const mockEventSourceInstance = {
        onmessage: null,
        onerror: null,
        close: jest.fn(),
      };

      (global.EventSource as jest.Mock).mockImplementation(() => mockEventSourceInstance);

      const eventSource = api.getEvaluationStream(
        'eval_123',
        mockOnMessage,
        mockOnError
      );

      expect(global.EventSource).toHaveBeenCalledWith(
        `${mockApiUrl}/api/evaluate/eval_123/stream`
      );

      expect(mockEventSourceInstance.onmessage).toBe(mockOnMessage);
      expect(mockEventSourceInstance.onerror).toBe(mockOnError);
    });
  });

  describe('Custom API URL', () => {
    beforeEach(() => {
      process.env.NEXT_PUBLIC_API_URL = 'https://api.somm.dev';
    });

    afterEach(() => {
      delete process.env.NEXT_PUBLIC_API_URL;
    });

    it('should use custom API URL from environment', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ evaluation_id: 'eval_test', status: 'pending' }),
      });

      await api.startEvaluation(
        'https://github.com/owner/repo',
        'basic'
      );

      expect(global.fetch).toHaveBeenCalledWith(
        'https://api.somm.dev/api/evaluate',
        expect.any(Object)
      );
    });
  });
});
