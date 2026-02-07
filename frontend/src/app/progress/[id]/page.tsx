'use client';

import React, { useEffect, useMemo } from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import Image from 'next/image';
import { useEvaluationStream } from '../../../hooks/useEvaluationStream';
import { Sparkles, CheckCircle2, Loader2, AlertTriangle, XCircle, ArrowLeft, WifiOff, Clock, GitBranch } from 'lucide-react';
import { EvaluationMode } from '../../../types';

const SIX_SOMMELIERS = [
  { id: 'marcel', name: 'Marcel', role: 'Structure & Metrics', color: '#8B4513' },
  { id: 'isabella', name: 'Isabella', role: 'Code Quality', color: '#C41E3A' },
  { id: 'heinrich', name: 'Heinrich', role: 'Security & Testing', color: '#2F4F4F' },
  { id: 'sofia', name: 'Sofia', role: 'Innovation', color: '#DAA520' },
  { id: 'laurent', name: 'Laurent', role: 'Implementation', color: '#4A0E0E' },
  { id: 'jeanpierre', name: 'Jean-Pierre', role: 'Final Verdict', color: '#722F37' },
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
  const modeParam = searchParams.get('mode');
  const mode: EvaluationMode = modeParam === 'grand_tasting' ? 'grand_tasting' : 'six_sommeliers';
  
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

  // Estimate remaining time based on progress
  const estimatedMinutes = useMemo(() => {
    if (progress === 0) return 2;
    if (progress >= 100) return 0;
    const remaining = Math.ceil((100 - progress) / 50);
    return Math.max(1, remaining);
  }, [progress]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#FDFBF7] via-[#FAF4E8] to-[#F5EED8] py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Decorative circles */}
      <div className="absolute top-20 left-10 w-64 h-64 bg-[#722F37]/5 rounded-full blur-3xl" />
      <div className="absolute bottom-20 right-10 w-96 h-96 bg-[#DAA520]/5 rounded-full blur-3xl" />
      
      <div className="max-w-3xl mx-auto relative">
        {/* Header */}
        <div className="text-center mb-10">
          {/* Powered badge */}
          <div className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-gradient-to-r from-[#DAA520]/20 to-[#FFD700]/20 border border-[#DAA520]/30 text-[#8B6914] text-sm font-semibold mb-6 shadow-lg shadow-[#DAA520]/10">
            <Sparkles className="w-5 h-5 text-[#DAA520] animate-pulse" />
            <span>{isGrandTasting ? 'Grand Tasting Mode' : 'Six Sommeliers'}</span>
          </div>

          <h1 className="text-4xl font-bold text-[#722F37] mb-4 font-serif">
            {isGrandTasting ? 'Grand Tasting in Progress' : 'Tasting in Progress'}
          </h1>
          <p className="text-gray-600 mb-4">
            {isGrandTasting 
              ? 'Our expert panel is conducting a comprehensive analysis with 75 techniques.'
              : 'Our sommeliers are analyzing the notes and nuances of your codebase.'
            }
          </p>
          
          {/* Sommelier avatars preview */}
          {!isGrandTasting && (
            <div className="flex justify-center items-center gap-1 mb-4">
              {SIX_SOMMELIERS.map((s, index) => {
                const isCompleted = completedSommeliers.some(c => c.id === s.id);
                const isActive = !isCompleted && completedSommeliers.length === index;
                return (
                  <div 
                    key={s.id}
                    className={`relative w-10 h-10 rounded-full overflow-hidden border-2 transition-all duration-300 ${
                      isCompleted 
                        ? 'border-green-500 scale-100' 
                        : isActive 
                          ? 'border-[#722F37] scale-110 shadow-lg animate-pulse'
                          : 'border-gray-300 opacity-50 grayscale'
                    }`}
                  >
                    <Image 
                      src={`/sommeliers/${s.id}.png`}
                      alt={s.name}
                      fill
                      className="object-cover object-top"
                    />
                    {isCompleted && (
                      <div className="absolute inset-0 bg-green-500/20 flex items-center justify-center">
                        <CheckCircle2 className="w-5 h-5 text-green-600" />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {/* Estimated time */}
          <div className="inline-flex items-center gap-2 text-sm text-gray-500">
            <Clock className="w-4 h-4" />
            <span>Estimated: ~{estimatedMinutes} minute{estimatedMinutes !== 1 ? 's' : ''} remaining</span>
          </div>
        </div>

        {/* Main progress card */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-[#722F37]/10 p-8 mb-8">
          {/* Progress bar */}
          <div className="mb-8">
            <div className="flex justify-between text-sm font-medium text-gray-600 mb-2">
              <span>Analysis Progress</span>
              <span className="text-[#722F37] font-bold">{progress}%</span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-3 overflow-hidden">
              <div 
                className={`h-3 rounded-full transition-all duration-500 ease-out ${
                  isGrandTasting 
                    ? 'bg-gradient-to-r from-amber-500 to-amber-600' 
                    : 'bg-gradient-to-r from-[#722F37] to-[#5A252C]'
                }`}
                style={{ width: `${progress}%` }}
              />
            </div>
            {connectionStatus === 'retrying' && retryInfo && (
              <div className="mt-3 flex items-center text-sm text-amber-600 bg-amber-50 px-3 py-2 rounded-lg">
                <WifiOff size={14} className="mr-2" />
                <span>
                  Reconnecting ({retryInfo.attempt}/{retryInfo.maxAttempts})...
                </span>
              </div>
            )}
          </div>

          {/* Sommelier list */}
          <div className="space-y-3">
            {evaluators.map((evaluator, index) => {
              const isCompleted = completedSommeliers.some(s => s.id === evaluator.id);
              const isActive = !isCompleted && completedSommeliers.length >= index && completedSommeliers.length < evaluators.length;
              const completedData = completedSommeliers.find(s => s.id === evaluator.id);
              
              return (
                <div 
                  key={evaluator.id}
                  className={`flex items-center p-4 rounded-xl border-2 transition-all duration-300 ${
                    isCompleted 
                      ? 'bg-green-50/50 border-green-200'
                      : isActive
                        ? 'bg-white border-[#722F37]/30 shadow-md scale-[1.02]'
                        : 'bg-gray-50/50 border-transparent opacity-50'
                  }`}
                >
                  {/* Avatar */}
                  <div className={`relative w-14 h-14 rounded-full overflow-hidden mr-4 border-2 transition-all ${
                    isCompleted 
                      ? 'border-green-500'
                      : isActive
                        ? 'border-[#722F37] shadow-lg'
                        : 'border-gray-200 grayscale'
                  }`}>
                    {!isGrandTasting ? (
                      <Image 
                        src={`/sommeliers/${evaluator.id}.png`}
                        alt={evaluator.name}
                        fill
                        className="object-cover object-top"
                      />
                    ) : (
                      <div className={`w-full h-full flex items-center justify-center ${
                        isCompleted ? 'bg-amber-100' : isActive ? 'bg-amber-50' : 'bg-gray-100'
                      }`}>
                        <Sparkles className={`w-6 h-6 ${
                          isCompleted ? 'text-amber-600' : isActive ? 'text-amber-500' : 'text-gray-400'
                        }`} />
                      </div>
                    )}
                    {isActive && (
                      <div className="absolute inset-0 bg-[#722F37]/10 animate-pulse" />
                    )}
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className={`font-semibold ${
                        isCompleted ? 'text-green-700' : isActive ? 'text-[#722F37]' : 'text-gray-600'
                      }`}>
                        {evaluator.name}
                      </h3>
                      {isActive && (
                        <span className="px-2 py-0.5 bg-[#722F37]/10 text-[#722F37] text-xs font-medium rounded-full">
                          Analyzing...
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-500">{evaluator.role}</p>
                    {isCompleted && completedData?.feedback && (
                      <p className="text-xs text-green-600 mt-1 truncate">{completedData.feedback}</p>
                    )}
                  </div>

                  {/* Status indicator */}
                  <div className="flex-shrink-0">
                    {isCompleted ? (
                      <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                        <CheckCircle2 className="w-6 h-6 text-green-600" />
                      </div>
                    ) : isActive ? (
                      <div className="w-10 h-10 rounded-full bg-[#722F37]/10 flex items-center justify-center">
                        <Loader2 className="w-6 h-6 text-[#722F37] animate-spin" />
                      </div>
                    ) : (
                      <div className="w-10 h-10 rounded-full border-2 border-gray-200 border-dashed" />
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Error state */}
        {status === 'failed' && (
          <div className="bg-white/80 backdrop-blur-sm border-2 border-red-200 rounded-2xl p-8 text-center shadow-lg">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-100 flex items-center justify-center">
              <XCircle className="text-red-500" size={32} />
            </div>
            <h2 className="text-2xl font-bold text-red-700 mb-2">Evaluation Failed</h2>
            <p className="text-red-600 mb-6 max-w-md mx-auto">
              {errors.length > 0 ? errors[errors.length - 1] : 'An unexpected error occurred during evaluation.'}
            </p>
            <button
              onClick={() => router.push('/evaluate')}
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-[#722F37] to-[#5A252C] text-white font-semibold rounded-xl hover:from-[#5A252C] hover:to-[#4A1F24] transition-all shadow-lg"
            >
              <ArrowLeft size={18} />
              Try Another Repository
            </button>
          </div>
        )}

        {/* Warnings */}
        {errors.length > 0 && status !== 'failed' && (
          <div className="bg-amber-50/80 backdrop-blur-sm border border-amber-200 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="text-amber-600" size={18} />
              <h3 className="font-semibold text-amber-800">Warnings</h3>
            </div>
            <ul className="list-disc list-inside text-sm text-amber-700 space-y-1">
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
