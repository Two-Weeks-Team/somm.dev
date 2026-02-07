'use client';

import { useState, useEffect } from 'react';

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

export function useWebGLSupport(): boolean {
  const [supported, setSupported] = useState(false);
  
  useEffect(() => {
    setSupported(isWebGLAvailable());
  }, []);
  
  return supported;
}
