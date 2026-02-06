import React from 'react';
import { CriteriaType } from '../types';
import { Wine, Award, BookOpen, Settings, LucideIcon } from 'lucide-react';

interface CriteriaSelectorProps {
  value: CriteriaType;
  onChange: (value: CriteriaType) => void;
}

const criteriaOptions: { value: CriteriaType; label: string; description: string; icon: LucideIcon }[] = [
  {
    value: 'basic',
    label: 'House Blend (Basic)',
    description: 'A balanced evaluation of code quality, structure, and best practices. Good for everyday commits.',
    icon: Wine,
  },
  {
    value: 'hackathon',
    label: 'Beaujolais Nouveau (Hackathon)',
    description: 'Quick, vibrant, and focused on innovation and "wow" factor. Perfect for prototypes and MVPs.',
    icon: Award,
  },
  {
    value: 'academic',
    label: 'Grand Cru (Academic)',
    description: 'Rigorous, structured, and detail-oriented. Focuses on algorithms, complexity, and theoretical soundness.',
    icon: BookOpen,
  },
  {
    value: 'custom',
    label: 'Sommelier\'s Choice (Custom)',
    description: 'Tailored to your specific taste. Define your own rules and focus areas.',
    icon: Settings,
  },
];

export const CriteriaSelector: React.FC<CriteriaSelectorProps> = ({ value, onChange }) => {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-[#722F37]">Select Your Blend</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {criteriaOptions.map((option) => (
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
            <div>
              <h4 className={`font-medium ${value === option.value ? 'text-[#722F37]' : 'text-gray-900'}`}>
                {option.label}
              </h4>
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
