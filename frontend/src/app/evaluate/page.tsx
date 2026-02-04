'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { EvaluationForm } from '../../components/EvaluationForm';
import { api } from '../../lib/api';
import { CriteriaType } from '../../types';

export default function EvaluatePage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleEvaluationSubmit = async (repoUrl: string, criteria: CriteriaType) => {
    setIsLoading(true);
    setError(null);

    try {
      const { id } = await api.startEvaluation(repoUrl, criteria);
      router.push(`/progress/${id}`);
    } catch (err) {
      console.error('Evaluation failed:', err);
      setError(err instanceof Error ? err.message : 'Failed to start evaluation. Please try again.');
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#FAFAFA] py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-[#722F37] mb-4 font-serif">
            Let the Tasting Begin
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Submit your repository for a comprehensive code review by our panel of expert AI sommeliers.
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
