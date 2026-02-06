import React, { useEffect } from 'react';
import { Play, Pause, ChevronLeft, ChevronRight } from 'lucide-react';

interface TimelinePlayerProps {
  currentStep: number;
  maxStep: number;
  isPlaying: boolean;
  onStepChange: (step: number) => void;
  onPlayPause: () => void;
  playbackSpeed?: number;
  onSpeedChange?: (speed: number) => void;
}

export function TimelinePlayer({
  currentStep,
  maxStep,
  isPlaying,
  onStepChange,
  onPlayPause,
  playbackSpeed = 1,
  onSpeedChange,
}: TimelinePlayerProps) {
  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Only trigger if not typing in an input
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
          onStepChange(Math.max(0, currentStep - 1));
          break;
        case 'ArrowRight':
          e.preventDefault();
          onStepChange(Math.min(maxStep, currentStep + 1));
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
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentStep, maxStep, onPlayPause, onStepChange, onSpeedChange]);

  return (
    <div className="flex flex-col gap-2 p-4 bg-white border border-[#F7E7CE] rounded-lg shadow-sm w-full max-w-3xl mx-auto">
      <div className="flex items-center justify-between gap-4">
        {/* Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => onStepChange(Math.max(0, currentStep - 1))}
            disabled={currentStep <= 0}
            className="p-2 text-[#722F37] hover:bg-[#F7E7CE]/20 rounded-full disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            aria-label="Previous step"
          >
            <ChevronLeft size={20} />
          </button>

          <button
            onClick={onPlayPause}
            className="p-3 bg-[#722F37] text-white rounded-full hover:bg-[#5a252c] transition-colors shadow-md"
            aria-label={isPlaying ? "Pause" : "Play"}
          >
            {isPlaying ? <Pause size={20} fill="currentColor" /> : <Play size={20} fill="currentColor" className="ml-0.5" />}
          </button>

          <button
            onClick={() => onStepChange(Math.min(maxStep, currentStep + 1))}
            disabled={currentStep >= maxStep}
            className="p-2 text-[#722F37] hover:bg-[#F7E7CE]/20 rounded-full disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            aria-label="Next step"
          >
            <ChevronRight size={20} />
          </button>
        </div>

        {/* Step Counter */}
        <div className="font-mono text-sm font-medium text-[#722F37] min-w-[80px] text-center">
          Step {currentStep}/{maxStep}
        </div>

        {/* Slider */}
        <div className="flex-1 px-2">
          <input
            type="range"
            min={0}
            max={maxStep}
            value={currentStep}
            onChange={(e) => onStepChange(parseInt(e.target.value))}
            className="w-full h-2 bg-[#F7E7CE] rounded-lg appearance-none cursor-pointer accent-[#722F37]"
          />
        </div>

        {/* Speed Selector */}
        {onSpeedChange && (
          <div className="flex items-center bg-[#F7E7CE]/30 rounded-lg p-1">
            {[0.5, 1, 2].map((speed) => (
              <button
                key={speed}
                onClick={() => onSpeedChange(speed)}
                className={`px-2 py-1 text-xs font-medium rounded transition-colors ${
                  playbackSpeed === speed
                    ? 'bg-[#722F37] text-white shadow-sm'
                    : 'text-[#722F37] hover:bg-[#F7E7CE]/50'
                }`}
              >
                {speed}x
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
