'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { EvaluationForm } from '../../components/EvaluationForm';
import { api } from '../../lib/api';
import { CriteriaType, EvaluationMode } from '../../types';
import { Sparkles } from 'lucide-react';

export default function EvaluatePage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleEvaluationSubmit = async (repoUrl: string, criteria: CriteriaType, evaluationMode: EvaluationMode) => {
    setIsLoading(true);
    setError(null);

    try {
      const { id } = await api.startEvaluation(repoUrl, criteria, evaluationMode);
      router.push(`/progress/${id}?mode=${evaluationMode}`);
    } catch (err) {
      console.error('Evaluation failed:', err);
      setError(err instanceof Error ? err.message : 'Failed to start evaluation. Please try again.');
      setIsLoading(false);
    }
  };

  const sommelierIds = ['marcel', 'isabella', 'heinrich', 'sofia', 'laurent', 'jeanpierre'];

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#FDFBF7] via-[#FAF4E8] to-[#F5EED8] py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Decorative circles */}
      <div className="absolute top-20 left-10 w-64 h-64 bg-[#722F37]/5 rounded-full blur-3xl" />
      <div className="absolute bottom-20 right-10 w-96 h-96 bg-[#DAA520]/5 rounded-full blur-3xl" />
      
      <div className="max-w-4xl mx-auto relative">
        {/* Header with badge and avatars */}
        <div className="text-center mb-10">
          {/* Powered by Gemini badge */}
          <div className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-gradient-to-r from-[#DAA520]/20 to-[#FFD700]/20 border border-[#DAA520]/30 text-[#8B6914] text-sm font-semibold mb-6 shadow-lg shadow-[#DAA520]/10">
            <Sparkles className="w-5 h-5 text-[#DAA520] animate-pulse" />
            <span>Powered by Gemini 3</span>
            <span className="px-2 py-0.5 bg-[#DAA520] text-white text-xs rounded-full">NEW</span>
          </div>

          <h1 className="text-4xl md:text-5xl font-bold text-[#722F37] mb-4 font-serif">
            Let the Tasting Begin
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
            Submit your repository for a comprehensive code review by our panel of expert AI sommeliers.
          </p>

          {/* Sommelier avatars */}
          <div className="flex justify-center items-center gap-1 mb-2">
            {sommelierIds.map((id, index) => (
              <div 
                key={id} 
                className="w-10 h-10 rounded-full overflow-hidden border-2 border-white shadow-md -ml-2 first:ml-0 hover:scale-110 hover:z-10 transition-transform"
                style={{ zIndex: sommelierIds.length - index }}
              >
                <Image 
                  src={`/sommeliers/${id}.png`} 
                  alt={id} 
                  width={40} 
                  height={40} 
                  className="object-cover object-top"
                />
              </div>
            ))}
          </div>
          <p className="text-sm text-gray-500 flex items-center justify-center gap-1">
            <Sparkles className="w-4 h-4 text-[#DAA520]" />
            6 AI sommeliers ready to evaluate
          </p>
        </div>

        <EvaluationForm 
          onSubmit={handleEvaluationSubmit} 
          isLoading={isLoading} 
          error={error} 
        />
      </div>
    </div>
  );
}
