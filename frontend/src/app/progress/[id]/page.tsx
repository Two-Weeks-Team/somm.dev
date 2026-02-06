'use client';

import React, { useEffect, useMemo } from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import { useEvaluationStream } from '../../../hooks/useEvaluationStream';
import { Wine, Sparkles, CheckCircle2, Loader2, AlertTriangle, XCircle, ArrowLeft, WifiOff } from 'lucide-react';
import { EvaluationMode } from '../../../types';

const SIX_SOMMELIERS = [
  { id: 'marcel', name: 'Marcel', role: 'Structure & Metrics' },
  { id: 'isabella', name: 'Isabella', role: 'Code Quality' },
  { id: 'heinrich', name: 'Heinrich', role: 'Security & Testing' },
  { id: 'sofia', name: 'Sofia', role: 'Innovation' },
  { id: 'laurent', name: 'Laurent', role: 'Implementation' },
  { id: 'jeanpierre', name: 'Jean-Pierre', role: 'Final Verdict' },
];

const GRAND_TASTING_NOTES = [
  { id: 'aroma', name: 'Aroma', role: 'Problem Analysis' },
  { id: 'palate', name: 'Palate', role: 'Innovation & Creativity' },
  { id: 'body', name: 'Body', role: 'Technical Depth' },
  { id: 'finish', name: 'Finish', role: 'User Experience' },
  { id: 'balance', name: 'Balance', role: 'Architecture & Design' },
  { id: 'vintage', name: 'Vintage', role: 'Market Opportunity' },
  { id: 'terroir', name: 'Terroir', role: 'Presentation Quality' },
  { id: 'cellar', name: 'Cellar', role: 'Final Synthesis' },
];

export default function ProgressPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const id = params.id as string;
  const mode = (searchParams.get('mode') as EvaluationMode) || 'six_sommeliers';
  
  const { completedSommeliers, errors, isComplete, progress, status, connectionStatus, retryInfo } = useEvaluationStream(id);

  const evaluators = useMemo(() => {
    return mode === 'grand_tasting' ? GRAND_TASTING_NOTES : SIX_SOMMELIERS;
  }, [mode]);

  const isGrandTasting = mode === 'grand_tasting';

  useEffect(() => {
    if (isComplete && status === 'completed') {
      const timeout = setTimeout(() => {
        router.push(`/evaluate/${id}/result`);
      }, 1500);
      return () => clearTimeout(timeout);
    }
  }, [isComplete, status, id, router]);

  return (
    <div className="min-h-screen bg-[#FAFAFA] py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold text-[#722F37] mb-4 font-serif">
            {isGrandTasting ? 'Grand Tasting in Progress' : 'Tasting in Progress'}
          </h1>
          <p className="text-gray-600">
            {isGrandTasting 
              ? 'Our expert panel is conducting a comprehensive analysis with 75 techniques.'
              : 'Our sommeliers are analyzing the notes and nuances of your codebase.'
            }
          </p>
          {isGrandTasting && (
            <div className="mt-2 inline-flex items-center px-3 py-1 bg-amber-100 text-amber-800 rounded-full text-sm">
              <Sparkles size={14} className="mr-1" />
              Hackathon Mode
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 mb-8">
          <div className="mb-8">
            <div className="flex justify-between text-sm font-medium text-gray-600 mb-2">
              <span>Analysis Progress</span>
              <span>{progress}%</span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-2.5 overflow-hidden">
              <div 
                className={`h-2.5 rounded-full transition-all duration-500 ease-out ${
                  isGrandTasting ? 'bg-amber-600' : 'bg-[#722F37]'
                }`}
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            {connectionStatus === 'retrying' && retryInfo && (
              <div className="mt-3 flex items-center text-sm text-amber-600">
                <WifiOff size={14} className="mr-2" />
                <span>
                  Connection lost - retrying ({retryInfo.attempt}/{retryInfo.maxAttempts})...
                </span>
              </div>
            )}
          </div>

          <div className="space-y-4">
            {evaluators.map((evaluator, index) => {
              const isCompleted = completedSommeliers.some(s => s.id === evaluator.id);
              const isActive = !isCompleted && completedSommeliers.length >= index && completedSommeliers.length < evaluators.length;
              
              return (
                <div 
                  key={evaluator.id}
                  className={`flex items-center p-4 rounded-lg border transition-all duration-300 ${
                    isCompleted 
                      ? isGrandTasting 
                        ? 'bg-amber-50 border-amber-200'
                        : 'bg-[#F7E7CE] bg-opacity-20 border-[#F7E7CE]'
                      : isActive
                        ? isGrandTasting
                          ? 'bg-white border-amber-400 border-opacity-50 shadow-sm'
                          : 'bg-white border-[#722F37] border-opacity-30 shadow-sm'
                        : 'bg-gray-50 border-transparent opacity-60'
                  }`}
                >
                  <div className={`p-2 rounded-full mr-4 ${
                    isCompleted 
                      ? isGrandTasting ? 'bg-amber-600 text-white' : 'bg-[#722F37] text-white'
                      : 'bg-gray-200 text-gray-400'
                  }`}>
                    {isGrandTasting ? <Sparkles size={20} /> : <Wine size={20} />}
                  </div>
                  <div className="flex-1">
                    <h3 className={`font-medium ${
                      isCompleted 
                        ? isGrandTasting ? 'text-amber-800' : 'text-[#722F37]'
                        : 'text-gray-900'
                    }`}>
                      {evaluator.name}
                    </h3>
                    <p className="text-sm text-gray-500">{evaluator.role}</p>
                  </div>
                  <div>
                    {isCompleted ? (
                      <CheckCircle2 className="text-green-600" />
                    ) : isActive ? (
                      <Loader2 className={`animate-spin ${isGrandTasting ? 'text-amber-600' : 'text-[#722F37]'}`} />
                    ) : (
                      <div className="w-6 h-6 rounded-full border-2 border-gray-200"></div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {status === 'failed' && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
            <XCircle className="mx-auto text-red-500 mb-4" size={48} />
            <h2 className="text-xl font-bold text-red-700 mb-2">Evaluation Failed</h2>
            <p className="text-red-600 mb-4">
              {errors.length > 0 ? errors[errors.length - 1] : 'An unexpected error occurred during evaluation.'}
            </p>
            <button
              onClick={() => router.push('/evaluate')}
              className="inline-flex items-center px-4 py-2 bg-[#722F37] text-white rounded-lg hover:bg-[#5a252c] transition-colors"
            >
              <ArrowLeft size={16} className="mr-2" />
              Try Another Repository
            </button>
          </div>
        )}

        {errors.length > 0 && status !== 'failed' && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-yellow-700">
            <div className="flex items-center mb-2">
              <AlertTriangle className="mr-2" size={20} />
              <h3 className="font-semibold">Warnings</h3>
            </div>
            <ul className="list-disc list-inside text-sm">
              {errors.map((err, index) => (
                <li key={index}>{err}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
