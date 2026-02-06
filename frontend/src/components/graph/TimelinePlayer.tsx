import React, { useEffect, useMemo, useCallback } from 'react';
import { Play, Pause, ChevronLeft, ChevronRight, SkipBack, SkipForward } from 'lucide-react';
import { cn } from '@/lib/utils';

interface TimelinePlayerProps {
  currentStep: number;
  maxStep: number;
  isPlaying: boolean;
  onStepChange: (step: number) => void;
  onPlayPause: () => void;
  playbackSpeed?: number;
  onSpeedChange?: (speed: number) => void;
  /** Optional labels for step tooltips */
  stepLabels?: string[];
  /** Callback when step changes for auto-pan/zoom */
  onAutoFocus?: (step: number) => void;
}

export function TimelinePlayer({
  currentStep,
  maxStep,
  isPlaying,
  onStepChange,
  onPlayPause,
  playbackSpeed = 1,
  onSpeedChange,
  stepLabels,
  onAutoFocus,
}: TimelinePlayerProps) {
  const handleStepClick = useCallback((step: number) => {
    onStepChange(step);
    onAutoFocus?.(step);
    window.dispatchEvent(new CustomEvent('timeline-step-change', { detail: { step } }));
  }, [onStepChange, onAutoFocus]);

  const displayedSteps = useMemo(() => {
    if (maxStep <= 15) {
      return Array.from({ length: maxStep + 1 }, (_, i) => i);
    }
    const stepInterval = Math.ceil(maxStep / 10);
    const steps: number[] = [0];
    for (let i = stepInterval; i < maxStep; i += stepInterval) {
      steps.push(i);
    }
    if (steps[steps.length - 1] !== maxStep) {
      steps.push(maxStep);
    }
    return steps;
  }, [maxStep]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      switch (e.key) {
        case ' ':
          e.preventDefault();
          onPlayPause();
          break;
        case 'ArrowLeft':
          e.preventDefault();
          handleStepClick(Math.max(0, currentStep - 1));
          break;
        case 'ArrowRight':
          e.preventDefault();
          handleStepClick(Math.min(maxStep, currentStep + 1));
          break;
        case '1':
          onSpeedChange?.(0.5);
          break;
        case '2':
          onSpeedChange?.(1);
          break;
        case '3':
          onSpeedChange?.(2);
          break;
        case 'Home':
          e.preventDefault();
          handleStepClick(0);
          break;
        case 'End':
          e.preventDefault();
          handleStepClick(maxStep);
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentStep, maxStep, onPlayPause, handleStepClick, onSpeedChange]);

  useEffect(() => {
    if (isPlaying) {
      window.dispatchEvent(new CustomEvent('timeline-step-change', { detail: { step: currentStep } }));
    }
  }, [currentStep, isPlaying]);

  return (
    <div className="flex flex-col gap-3 p-4 bg-white border border-[#F7E7CE] rounded-lg shadow-sm w-full max-w-4xl mx-auto">
      <div className="flex items-center justify-between gap-2 md:gap-4">
        <div className="flex items-center gap-1 md:gap-2">
          <button
            onClick={() => handleStepClick(0)}
            disabled={currentStep <= 0}
            className="p-1.5 md:p-2 text-[#722F37] hover:bg-[#F7E7CE]/20 rounded-full disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            aria-label="First step"
          >
            <SkipBack size={16} className="md:w-5 md:h-5" />
          </button>

          <button
            onClick={() => handleStepClick(Math.max(0, currentStep - 1))}
            disabled={currentStep <= 0}
            className="p-1.5 md:p-2 text-[#722F37] hover:bg-[#F7E7CE]/20 rounded-full disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            aria-label="Previous step"
          >
            <ChevronLeft size={18} className="md:w-5 md:h-5" />
          </button>

          <button
            onClick={onPlayPause}
            className="p-2.5 md:p-3 bg-[#722F37] text-white rounded-full hover:bg-[#5a252c] transition-colors shadow-md"
            aria-label={isPlaying ? "Pause" : "Play"}
          >
            {isPlaying ? <Pause size={18} fill="currentColor" className="md:w-5 md:h-5" /> : <Play size={18} fill="currentColor" className="ml-0.5 md:w-5 md:h-5" />}
          </button>

          <button
            onClick={() => handleStepClick(Math.min(maxStep, currentStep + 1))}
            disabled={currentStep >= maxStep}
            className="p-1.5 md:p-2 text-[#722F37] hover:bg-[#F7E7CE]/20 rounded-full disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            aria-label="Next step"
          >
            <ChevronRight size={18} className="md:w-5 md:h-5" />
          </button>

          <button
            onClick={() => handleStepClick(maxStep)}
            disabled={currentStep >= maxStep}
            className="p-1.5 md:p-2 text-[#722F37] hover:bg-[#F7E7CE]/20 rounded-full disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            aria-label="Last step"
          >
            <SkipForward size={16} className="md:w-5 md:h-5" />
          </button>
        </div>

        <div className="font-mono text-xs md:text-sm font-medium text-[#722F37] min-w-[60px] md:min-w-[80px] text-center">
          {currentStep}/{maxStep}
        </div>

        {onSpeedChange && (
          <div className="flex items-center bg-[#F7E7CE]/30 rounded-lg p-0.5 md:p-1">
            {[0.5, 1, 2].map((speed) => (
              <button
                key={speed}
                onClick={() => onSpeedChange(speed)}
                className={cn(
                  'px-1.5 md:px-2 py-0.5 md:py-1 text-[10px] md:text-xs font-medium rounded transition-colors',
                  playbackSpeed === speed
                    ? 'bg-[#722F37] text-white shadow-sm'
                    : 'text-[#722F37] hover:bg-[#F7E7CE]/50'
                )}
              >
                {speed}x
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="relative px-2">
        <div className="absolute top-1/2 left-2 right-2 h-0.5 bg-[#F7E7CE] -translate-y-1/2" />
        <div 
          className="absolute top-1/2 left-2 h-0.5 bg-[#722F37] -translate-y-1/2 transition-all duration-300"
          style={{ width: `${maxStep > 0 ? (currentStep / maxStep) * 100 : 0}%` }}
        />
        
        <div className="relative flex justify-between items-center">
          {displayedSteps.map((step, index) => {
            const isCompleted = step < currentStep;
            const isActive = step === currentStep;
            const isPending = step > currentStep;
            const label = stepLabels?.[step];
            
            return (
              <button
                key={step}
                onClick={() => handleStepClick(step)}
                title={label || `Step ${step}`}
                className="group relative flex flex-col items-center"
                aria-label={label || `Go to step ${step}`}
              >
                <div
                  className={cn(
                    'w-3 h-3 md:w-4 md:h-4 rounded-full border-2 transition-all duration-200 cursor-pointer',
                    isCompleted && 'bg-[#722F37] border-[#722F37]',
                    isActive && 'bg-[#722F37] border-[#722F37] ring-4 ring-[#722F37]/20 animate-pulse',
                    isPending && 'bg-white border-[#F7E7CE] hover:border-[#722F37]/50'
                  )}
                />
                {(index === 0 || index === displayedSteps.length - 1 || isActive) && (
                  <span className={cn(
                    'absolute -bottom-5 text-[10px] md:text-xs font-mono transition-colors',
                    isActive ? 'text-[#722F37] font-medium' : 'text-gray-400'
                  )}>
                    {step}
                  </span>
                )}
                {label && (
                  <span className="absolute -top-8 left-1/2 -translate-x-1/2 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-10">
                    {label}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
