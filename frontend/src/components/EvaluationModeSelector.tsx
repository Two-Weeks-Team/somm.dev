import React, { useEffect } from 'react';
import { EvaluationMode } from '../types';
import { Wine, Trophy, LucideIcon } from 'lucide-react';

interface EvaluationModeSelectorProps {
  value: EvaluationMode;
  onChange: (value: EvaluationMode) => void;
  isAuthenticated?: boolean;
}

interface ModeOption {
  value: EvaluationMode;
  label: string;
  description: string;
  icon: LucideIcon;
  badge?: string;
}

const modeOptions: ModeOption[] = [
  {
    value: 'six_sommeliers',
    label: 'Six Sommeliers',
    description: 'Classic evaluation by 6 expert AI sommeliers. Quick and comprehensive.',
    icon: Wine,
  },
  {
    value: 'grand_tasting',
    label: 'Grand Tasting',
    description: 'Deep analysis using 75 evaluation techniques across 8 tasting notes. Thorough and detailed.',
    icon: Trophy,
    badge: '75 Techniques',
  },
];

export const EvaluationModeSelector: React.FC<EvaluationModeSelectorProps> = ({ value, onChange, isAuthenticated = false }) => {
  useEffect(() => {
    if (!isAuthenticated && value === 'grand_tasting') {
      onChange('six_sommeliers');
    }
  }, [isAuthenticated, value, onChange]);

  const handleKeyDown = (e: React.KeyboardEvent, optionValue: EvaluationMode, disabled: boolean) => {
    if (disabled) return;
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onChange(optionValue);
    }
  };

  return (
    <div className="space-y-4">
      <h3 id="tasting-style-label" className="text-lg font-semibold text-[#722F37]">Select Tasting Style</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4" role="radiogroup" aria-labelledby="tasting-style-label">
        {modeOptions.map((option) => {
          const isDisabled = !isAuthenticated && option.value === 'grand_tasting';
          
          return (
            <div
              key={option.value}
              role="radio"
              aria-checked={value === option.value}
              aria-disabled={isDisabled}
              tabIndex={isDisabled ? -1 : 0}
              onClick={() => !isDisabled && onChange(option.value)}
              onKeyDown={(e) => handleKeyDown(e, option.value, isDisabled)}
              className={`border-2 rounded-lg p-4 transition-all duration-200 flex items-start space-x-3 focus:outline-none focus:ring-2 focus:ring-[#722F37] focus:ring-offset-2 ${
                isDisabled 
                  ? 'opacity-50 cursor-not-allowed border-gray-200 bg-gray-50'
                  : value === option.value
                    ? 'cursor-pointer border-[#722F37] bg-[#F7E7CE] bg-opacity-30'
                    : 'cursor-pointer border-gray-200 hover:border-[#722F37] hover:bg-gray-50'
              }`}
            >
              <div className={`p-2 rounded-full ${
                isDisabled 
                  ? 'bg-gray-200 text-gray-400'
                  : value === option.value 
                    ? 'bg-[#722F37] text-white' 
                    : 'bg-gray-100 text-gray-500'
              }`}>
                <option.icon size={20} />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h4 className={`font-medium ${
                    isDisabled 
                      ? 'text-gray-400'
                      : value === option.value 
                        ? 'text-[#722F37]' 
                        : 'text-gray-900'
                  }`}>
                    {option.label}
                  </h4>
                  {option.badge && (
                    <span className={`text-xs px-2 py-0.5 text-white rounded-full ${isDisabled ? 'bg-gray-400' : 'bg-[#722F37]'}`}>
                      {option.badge}
                    </span>
                  )}
                  {isDisabled && (
                    <span className="text-xs px-2 py-0.5 bg-amber-100 text-amber-700 border border-amber-200 rounded-full">
                      Login Required
                    </span>
                  )}
                </div>
                <p className={`text-sm mt-1 ${isDisabled ? 'text-gray-400' : 'text-gray-600'}`}>
                  {option.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
