import React, { useRef, useCallback } from 'react';
import { CriteriaType } from '../types';
import { Wine, Award, BookOpen, Settings, LucideIcon, Sparkles } from 'lucide-react';

interface CriteriaSelectorProps {
  value: CriteriaType;
  onChange: (value: CriteriaType) => void;
}

const criteriaOptions: { value: CriteriaType; label: string; description: string; icon: LucideIcon; recommended?: boolean }[] = [
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
    recommended: true,
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
  const optionRefs = useRef<(HTMLDivElement | null)[]>([]);

  const setOptionRef = useCallback((index: number) => (el: HTMLDivElement | null) => {
    optionRefs.current[index] = el;
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent, currentIndex: number) => {
    const optionsCount = criteriaOptions.length;
    let nextIndex: number | null = null;

    switch (e.key) {
      case 'ArrowRight':
      case 'ArrowDown':
        e.preventDefault();
        nextIndex = (currentIndex + 1) % optionsCount;
        break;
      case 'ArrowLeft':
      case 'ArrowUp':
        e.preventDefault();
        nextIndex = (currentIndex - 1 + optionsCount) % optionsCount;
        break;
      case 'Enter':
      case ' ':
        e.preventDefault();
        onChange(criteriaOptions[currentIndex].value);
        return;
      default:
        return;
    }

    if (nextIndex !== null) {
      const nextOption = criteriaOptions[nextIndex];
      onChange(nextOption.value);
      optionRefs.current[nextIndex]?.focus();
    }
  };

  return (
    <div className="space-y-4">
      <h3 id="criteria-label" className="text-lg font-semibold text-[#722F37]">Select Your Blend</h3>
      <div 
        role="radiogroup" 
        aria-labelledby="criteria-label"
        className="grid grid-cols-1 md:grid-cols-2 gap-4"
      >
        {criteriaOptions.map((option, index) => (
          <div
            key={option.value}
            ref={setOptionRef(index)}
            role="radio"
            aria-checked={value === option.value}
            tabIndex={value === option.value ? 0 : -1}
            onClick={() => onChange(option.value)}
            onKeyDown={(e) => handleKeyDown(e, index)}
            className={`relative cursor-pointer border-2 rounded-xl p-4 transition-all duration-200 flex items-start space-x-3 focus:outline-none focus:ring-2 focus:ring-[#722F37] focus:ring-offset-2 ${
              value === option.value
                ? 'border-[#722F37] bg-[#F7E7CE]/30 shadow-sm'
                : option.recommended
                ? 'border-[#DAA520]/50 hover:border-[#DAA520] hover:bg-[#DAA520]/5'
                : 'border-gray-200 hover:border-[#722F37] hover:bg-gray-50'
            }`}
          >
            {option.recommended && (
              <div className="absolute -top-2.5 right-3 flex items-center gap-1 px-2 py-0.5 bg-gradient-to-r from-[#DAA520] to-[#B8860B] text-white text-xs font-bold rounded-full shadow-sm">
                <Sparkles className="w-3 h-3" />
                RECOMMENDED
              </div>
            )}
            <div className={`p-2 rounded-full ${value === option.value ? 'bg-[#722F37] text-white' : option.recommended ? 'bg-[#DAA520]/20 text-[#DAA520]' : 'bg-gray-100 text-gray-500'}`}>
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
