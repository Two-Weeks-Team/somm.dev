import React from 'react';
import { X, Key, Sparkles, AlertCircle } from 'lucide-react';
import Link from 'next/link';

interface QuotaExceededModalProps {
  isOpen: boolean;
  onClose: () => void;
  reason: 'quota_exceeded' | 'byok_required';
}

export const QuotaExceededModal: React.FC<QuotaExceededModalProps> = ({ isOpen, onClose, reason }) => {
  if (!isOpen) return null;

  const isByokRequired = reason === 'byok_required';
  
  const title = isByokRequired 
    ? "Grand Tasting Requires API Key" 
    : "Daily Evaluation Limit Reached";
    
  const description = isByokRequired
    ? "The Grand Tasting mode uses 75+ evaluation techniques which requires significant processing power. Please register your own Gemini API key to use this mode."
    : "You've used all your free evaluations for today. To continue evaluating repositories, you can register your own API key or upgrade to a premium plan.";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="relative w-full max-w-md bg-white rounded-2xl shadow-xl border border-[#722F37]/10 overflow-hidden animate-in fade-in zoom-in duration-200">
        {/* Header */}
        <div className="p-6 pb-0 flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-50 text-red-600 rounded-full">
              <AlertCircle size={24} />
            </div>
            <h3 className="text-xl font-serif font-semibold text-[#722F37]">
              {title}
            </h3>
          </div>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Body */}
        <div className="p-6">
          <p className="text-gray-600 mb-6">
            {description}
          </p>

          <div className="space-y-3">
            {/* Option 1: BYOK */}
            <Link 
              href="/settings/api-keys"
              onClick={onClose}
              className="flex items-center gap-4 p-4 rounded-xl border border-[#722F37]/20 hover:border-[#722F37] hover:bg-[#FAF4E8] transition-all group"
            >
              <div className="p-2 bg-[#722F37]/10 text-[#722F37] rounded-lg group-hover:bg-[#722F37] group-hover:text-white transition-colors">
                <Key size={20} />
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-[#722F37]">Register API Key</h4>
                <p className="text-xs text-gray-500">Use your own Gemini key (Free)</p>
              </div>
              <div className="text-[#722F37] opacity-0 group-hover:opacity-100 transition-opacity">
                &rarr;
              </div>
            </Link>

            {/* Option 2: Premium (Placeholder) */}
            <button 
              className="w-full flex items-center gap-4 p-4 rounded-xl border border-gray-200 hover:border-amber-400 hover:bg-amber-50 transition-all group text-left"
              onClick={() => {
                // Placeholder for premium upgrade
                alert("Premium plans coming soon!");
              }}
            >
              <div className="p-2 bg-amber-100 text-amber-600 rounded-lg group-hover:bg-amber-500 group-hover:text-white transition-colors">
                <Sparkles size={20} />
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-gray-900">Upgrade to Premium</h4>
                <p className="text-xs text-gray-500">Get more daily evaluations</p>
              </div>
            </button>
          </div>
        </div>
        
        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-100 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-800 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
