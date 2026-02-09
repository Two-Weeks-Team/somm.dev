import { renderHook } from '@testing-library/react';
import {
  isWebGLAvailable,
  useWebGLSupport,
  _resetCacheForTesting,
} from '@/lib/webgl';

const originalCreateElement = document.createElement.bind(document);

describe('WebGL Detection', () => {
  beforeEach(() => {
    _resetCacheForTesting();
  });

  afterEach(() => {
    document.createElement = originalCreateElement;
  });

  describe('isWebGLAvailable', () => {
    it('returns true when WebGL2 is available', () => {
      const mockCanvas = {
        getContext: jest.fn((type: string) => {
          if (type === 'webgl2') return {};
          return null;
        }),
      };
      document.createElement = jest.fn((tag: string) => {
        if (tag === 'canvas') return mockCanvas as unknown as HTMLCanvasElement;
        return originalCreateElement(tag);
      });

      expect(isWebGLAvailable()).toBe(true);
      expect(mockCanvas.getContext).toHaveBeenCalledWith('webgl2');
    });

    it('returns true when only WebGL1 is available', () => {
      const mockCanvas = {
        getContext: jest.fn((type: string) => {
          if (type === 'webgl') return {};
          return null;
        }),
      };
      document.createElement = jest.fn((tag: string) => {
        if (tag === 'canvas') return mockCanvas as unknown as HTMLCanvasElement;
        return originalCreateElement(tag);
      });

      expect(isWebGLAvailable()).toBe(true);
    });

    it('returns false when neither WebGL2 nor WebGL1 is available', () => {
      const mockCanvas = {
        getContext: jest.fn(() => null),
      };
      document.createElement = jest.fn((tag: string) => {
        if (tag === 'canvas') return mockCanvas as unknown as HTMLCanvasElement;
        return originalCreateElement(tag);
      });

      expect(isWebGLAvailable()).toBe(false);
    });

    it('returns false when getContext throws an error', () => {
      const mockCanvas = {
        getContext: jest.fn(() => {
          throw new Error('WebGL not supported');
        }),
      };
      document.createElement = jest.fn((tag: string) => {
        if (tag === 'canvas') return mockCanvas as unknown as HTMLCanvasElement;
        return originalCreateElement(tag);
      });

      expect(isWebGLAvailable()).toBe(false);
    });
  });

  describe('useWebGLSupport', () => {
    it('returns true when WebGL is available', () => {
      const mockCanvas = {
        getContext: jest.fn(() => ({})),
      };
      document.createElement = jest.fn((tag: string) => {
        if (tag === 'canvas') return mockCanvas as unknown as HTMLCanvasElement;
        return originalCreateElement(tag);
      });

      const { result } = renderHook(() => useWebGLSupport());
      expect(result.current).toBe(true);
    });

    it('returns false when WebGL is not available', () => {
      const mockCanvas = {
        getContext: jest.fn(() => null),
      };
      document.createElement = jest.fn((tag: string) => {
        if (tag === 'canvas') return mockCanvas as unknown as HTMLCanvasElement;
        return originalCreateElement(tag);
      });

      const { result } = renderHook(() => useWebGLSupport());
      expect(result.current).toBe(false);
    });
  });
});
