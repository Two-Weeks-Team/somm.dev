import React from 'react';
import { EvaluationMode } from '../types';
import { Wine, Trophy } from 'lucide-react';

interface EvaluationModeSelectorProps {
  value: EvaluationMode;
  onChange: (value: EvaluationMode) => void;
}

interface ModeOption {
  value: EvaluationMode;
  label: string;
  description: string;
  icon: React.ElementType;
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

export const EvaluationModeSelector: React.FC<EvaluationModeSelectorProps> = ({ value, onChange }) => {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-[#722F37]">Select Tasting Style</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {modeOptions.map((option) => (
          <div
            key={option.value}
            onClick={() => onChange(option.value)}
            className={`cursor-pointer border-2 rounded-lg p-4 transition-all duration-200 flex items-start space-x-3 ${
              value === option.value
                ? 'border-[#722F37] bg-[#F7E7CE] bg-opacity-30'
                : 'border-gray-200 hover:border-[#722F37] hover:bg-gray-50'
            }`}
          >
            <div className={`p-2 rounded-full ${value === option.value ? 'bg-[#722F37] text-white' : 'bg-gray-100 text-gray-500'}`}>
              <option.icon size={20} />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <h4 className={`font-medium ${value === option.value ? 'text-[#722F37]' : 'text-gray-900'}`}>
                  {option.label}
                </h4>
                {option.badge && (
                  <span className="text-xs px-2 py-0.5 bg-[#722F37] text-white rounded-full">
                    {option.badge}
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-600 mt-1">
                {option.description}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
