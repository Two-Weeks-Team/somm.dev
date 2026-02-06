import { useReducer, useEffect, useCallback } from 'react';

interface TimelineState {
  currentStep: number;
  isPlaying: boolean;
  playbackSpeed: number;
}

type TimelineAction =
  | { type: 'TICK'; maxStep: number }
  | { type: 'TOGGLE_PLAY'; maxStep: number }
  | { type: 'NEXT_STEP'; maxStep: number }
  | { type: 'PREV_STEP' }
  | { type: 'SET_STEP'; step: number; maxStep: number }
  | { type: 'SET_SPEED'; speed: number }
  | { type: 'SET_PLAYING'; isPlaying: boolean };

function timelineReducer(state: TimelineState, action: TimelineAction): TimelineState {
  switch (action.type) {
    case 'TICK': {
      const nextStep = Math.min(state.currentStep + 1, action.maxStep);
      const shouldStop = nextStep >= action.maxStep;
      return {
        ...state,
        currentStep: nextStep,
        isPlaying: shouldStop ? false : state.isPlaying,
      };
    }
    case 'TOGGLE_PLAY':
      if (state.currentStep >= action.maxStep) {
        return { ...state, currentStep: 0, isPlaying: true };
      }
      return { ...state, isPlaying: !state.isPlaying };
    case 'NEXT_STEP':
      return { ...state, currentStep: Math.min(state.currentStep + 1, action.maxStep), isPlaying: false };
    case 'PREV_STEP':
      return { ...state, currentStep: Math.max(state.currentStep - 1, 0), isPlaying: false };
    case 'SET_STEP':
      return { ...state, currentStep: Math.max(0, Math.min(action.step, action.maxStep)), isPlaying: false };
    case 'SET_SPEED':
      return { ...state, playbackSpeed: action.speed };
    case 'SET_PLAYING':
      return { ...state, isPlaying: action.isPlaying };
    default: {
      const _exhaustiveCheck: never = action;
      return _exhaustiveCheck;
    }
  }
}

export function useTimelinePlayer(maxStep: number) {
  const [state, dispatch] = useReducer(timelineReducer, {
    currentStep: 0,
    isPlaying: false,
    playbackSpeed: 1,
  });

  useEffect(() => {
    if (!state.isPlaying || state.currentStep >= maxStep) return;

    const timer = setTimeout(() => {
      dispatch({ type: 'TICK', maxStep });
    }, 1000 / state.playbackSpeed);

    return () => clearTimeout(timer);
  }, [state.isPlaying, state.currentStep, state.playbackSpeed, maxStep]);

  const togglePlay = useCallback(() => dispatch({ type: 'TOGGLE_PLAY', maxStep }), [maxStep]);
  const nextStep = useCallback(() => dispatch({ type: 'NEXT_STEP', maxStep }), [maxStep]);
  const prevStep = useCallback(() => dispatch({ type: 'PREV_STEP' }), []);
  const setStep = useCallback((step: number) => dispatch({ type: 'SET_STEP', step, maxStep }), [maxStep]);
  const setPlaybackSpeed = useCallback((speed: number) => dispatch({ type: 'SET_SPEED', speed }), []);
  const setIsPlaying = useCallback((isPlaying: boolean) => dispatch({ type: 'SET_PLAYING', isPlaying }), []);

  return {
    currentStep: state.currentStep,
    setCurrentStep: setStep,
    isPlaying: state.isPlaying,
    setIsPlaying,
    togglePlay,
    nextStep,
    prevStep,
    playbackSpeed: state.playbackSpeed,
    setPlaybackSpeed,
  };
}
