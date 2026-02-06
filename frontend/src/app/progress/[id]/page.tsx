'use client';

import React, { useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useEvaluationStream } from '../../../hooks/useEvaluationStream';
import { Wine, CheckCircle2, Loader2, AlertTriangle, XCircle, ArrowLeft, WifiOff } from 'lucide-react';

export default function ProgressPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  
  const { completedSommeliers, errors, isComplete, progress, status, connectionStatus, retryInfo } = useEvaluationStream(id);

  useEffect(() => {
    if (isComplete && status === 'completed') {
      const timeout = setTimeout(() => {
        router.push(`/evaluate/${id}/result`);
      }, 1500);
      return () => clearTimeout(timeout);
    }
  }, [isComplete, status, id, router]);

  const sommeliers = [
    { name: 'Marcel', role: 'Structure & Metrics' },
    { name: 'Isabella', role: 'Code Quality' },
    { name: 'Heinrich', role: 'Security & Testing' },
    { name: 'Sofia', role: 'Innovation' },
    { name: 'Laurent', role: 'Implementation' },
    { name: 'Jean-Pierre', role: 'Final Verdict' },
  ];

  return (
    <div className="min-h-screen bg-[#FAFAFA] py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold text-[#722F37] mb-4 font-serif">
            Tasting in Progress
          </h1>
          <p className="text-gray-600">
            Our sommeliers are analyzing the notes and nuances of your codebase.
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 mb-8">
          <div className="mb-8">
            <div className="flex justify-between text-sm font-medium text-gray-600 mb-2">
              <span>Analysis Progress</span>
              <span>{progress}%</span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-2.5 overflow-hidden">
              <div 
                className="bg-[#722F37] h-2.5 rounded-full transition-all duration-500 ease-out"
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
            {sommeliers.map((somm) => {
              const isCompleted = completedSommeliers.some(s => s.name === somm.name);
              const isNext = !isCompleted && completedSommeliers.length === sommeliers.indexOf(somm);
              
              return (
                <div 
                  key={somm.name}
                  className={`flex items-center p-4 rounded-lg border transition-all duration-300 ${
                    isCompleted 
                      ? 'bg-[#F7E7CE] bg-opacity-20 border-[#F7E7CE]' 
                      : isNext
                        ? 'bg-white border-[#722F37] border-opacity-30 shadow-sm'
                        : 'bg-gray-50 border-transparent opacity-60'
                  }`}
                >
                  <div className={`p-2 rounded-full mr-4 ${
                    isCompleted ? 'bg-[#722F37] text-white' : 'bg-gray-200 text-gray-400'
                  }`}>
                    <Wine size={20} />
                  </div>
                  <div className="flex-1">
                    <h3 className={`font-medium ${isCompleted ? 'text-[#722F37]' : 'text-gray-900'}`}>
                      {somm.name}
                    </h3>
                    <p className="text-sm text-gray-500">{somm.role}</p>
                  </div>
                  <div className="text-[#722F37]">
                    {isCompleted ? (
                      <CheckCircle2 className="text-green-600" />
                    ) : isNext ? (
                      <Loader2 className="animate-spin text-[#722F37]" />
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
