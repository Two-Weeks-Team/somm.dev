'use client';

import { useSyncExternalStore } from 'react';

export function isWebGLAvailable(): boolean {
  if (typeof window === 'undefined') return false;
  
  try {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
    return gl !== null;
  } catch {
    return false;
  }
}

let cachedSupport: boolean | null = null;

export function _resetCacheForTesting(): void {
  cachedSupport = null;
}

function getWebGLSnapshot(): boolean {
  if (cachedSupport === null) {
    cachedSupport = isWebGLAvailable();
  }
  return cachedSupport;
}

function getServerSnapshot(): boolean {
  return false; // SSR fallback
}

function subscribe(): () => void {
  // WebGL support doesn't change, so no-op subscription
  return () => {};
}

export function useWebGLSupport(): boolean {
  return useSyncExternalStore(subscribe, getWebGLSnapshot, getServerSnapshot);
}
