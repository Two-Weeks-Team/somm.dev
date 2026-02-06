import { useState, useEffect, useCallback } from 'react';

export function useTimelinePlayer(maxStep: number) {
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);

  // Auto-advance when playing
  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (isPlaying && currentStep < maxStep) {
      timer = setTimeout(() => {
        setCurrentStep((s) => {
          if (s >= maxStep) {
            setIsPlaying(false);
            return s;
          }
          return s + 1;
        });
      }, 1000 / playbackSpeed);
    } else if (currentStep >= maxStep) {
      setIsPlaying(false);
    }
    return () => clearTimeout(timer);
  }, [isPlaying, currentStep, maxStep, playbackSpeed]);

  const togglePlay = useCallback(() => {
    if (currentStep >= maxStep) {
      setCurrentStep(0);
      setIsPlaying(true);
    } else {
      setIsPlaying((p) => !p);
    }
  }, [currentStep, maxStep]);

  const nextStep = useCallback(() => {
    setCurrentStep((s) => Math.min(s + 1, maxStep));
    setIsPlaying(false);
  }, [maxStep]);

  const prevStep = useCallback(() => {
    setCurrentStep((s) => Math.max(s - 1, 0));
    setIsPlaying(false);
  }, []);

  const setStep = useCallback((step: number) => {
    setCurrentStep(Math.max(0, Math.min(step, maxStep)));
    setIsPlaying(false); // Pause when manually setting step
  }, [maxStep]);

  return {
    currentStep,
    setCurrentStep: setStep,
    isPlaying,
    setIsPlaying,
    togglePlay,
    nextStep,
    prevStep,
    playbackSpeed,
    setPlaybackSpeed,
  };
}
