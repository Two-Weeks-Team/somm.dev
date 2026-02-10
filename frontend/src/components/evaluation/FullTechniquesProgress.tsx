import React, { useState, useEffect } from 'react';
import { useFullTechniquesStream } from '../../hooks/useFullTechniquesStream';
import { ProgressTopBar } from './ProgressTopBar';
import { CategoryGlassCard } from './CategoryGlassCard';
import { Sparkles, CheckCircle2, AlertTriangle } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface FullTechniquesProgressProps {
  evaluationId: string;
  repoUrl?: string;
}

export const FullTechniquesProgress: React.FC<FullTechniquesProgressProps> = ({ evaluationId, repoUrl = 'Repository' }) => {
  const router = useRouter();
  const state = useFullTechniquesStream(evaluationId);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      if (state.startedAt) {
        const start = new Date(state.startedAt).getTime();
        const now = Date.now();
        setElapsedSeconds(Math.floor((now - start) / 1000));
      } else {
        setElapsedSeconds(prev => prev + 1);
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [state.startedAt]);

  useEffect(() => {
    if (state.isComplete && state.currentStage === 'complete') {
      const timeout = setTimeout(() => {
        router.push(`/evaluate/${evaluationId}/result`);
      }, 2000);
      return () => clearTimeout(timeout);
    }
  }, [state.isComplete, state.currentStage, evaluationId, router]);

  const getTechniquesForCategory = (categoryId: string) => {
    return Object.values(state.techniques)
      .filter(t => t.category === categoryId)
      .sort((a, b) => {
        const order = { running: 0, complete: 1, error: 2, queued: 3 };
        return (order[a.status] || 3) - (order[b.status] || 3);
      });
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-emerald-600';
    if (score >= 80) return 'text-emerald-500';
    if (score >= 70) return 'text-yellow-600';
    if (score >= 60) return 'text-orange-500';
    return 'text-red-600';
  };

  return (
    <div className="min-h-screen bg-[#FAF4E8] flex flex-col font-sans text-gray-900">
      <ProgressTopBar 
        repoName={repoUrl}
        connectionStatus={state.connectionStatus}
        elapsedSeconds={elapsedSeconds}
        etaSeconds={state.etaSeconds}
        totalTechniques={state.totalTechniques}
        completedTechniques={state.completedTechniques}
        enrichmentMessage={state.enrichmentMessage}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6 space-y-8">
        
        <div className="text-center space-y-2 py-4">
          <h1 className="text-3xl md:text-4xl font-serif font-bold text-[#722F37] animate-fade-in">
            {state.currentStage === 'enrichment' ? 'Preparing Analysis...' :
             state.currentStage === 'deep_synthesis' ? 'Synthesizing Insights...' :
             state.currentStage === 'quality_gate' ? 'Final Quality Gate...' :
             state.currentStage === 'complete' ? 'Evaluation Complete' :
             'Tasting Flight in Progress'}
          </h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            {state.currentStage === 'enrichment' ? 'Gathering context through code analysis, RAG, and web search.' :
             state.currentStage === 'deep_synthesis' ? 'Our Master Sommelier is blending the notes from all 75 techniques.' :
             state.currentStage === 'quality_gate' ? 'Verifying final scores and generating the vintage report.' :
             state.currentStage === 'complete' ? 'Your vintage report is ready for review.' :
             'Analyzing your codebase across 8 dimensions and 75 distinct techniques.'}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
          {Object.values(state.categories).map((category) => (
            <CategoryGlassCard 
              key={category.id}
              category={category}
              techniques={getTechniquesForCategory(category.id)}
            />
          ))}
        </div>

        {(state.currentStage === 'deep_synthesis' || state.currentStage === 'quality_gate' || state.currentStage === 'complete') && (
          <div className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 flex items-center justify-center p-4 animate-in fade-in duration-500">
            <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full text-center border border-[#722F37]/20 relative overflow-hidden">
              
              <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#722F37] via-[#DAA520] to-[#722F37]" />
              
              {state.currentStage === 'complete' ? (
                <div className="space-y-6">
                  <div className="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <CheckCircle2 className="w-10 h-10 text-emerald-600" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-[#722F37] mb-2">Analysis Complete</h2>
                    <p className="text-gray-600">Your vintage report is ready.</p>
                  </div>
                  {state.totalScore !== undefined && (
                    <div className="py-4">
                      <span className={`text-5xl font-bold ${getScoreColor(state.totalScore)}`}>
                        {state.totalScore}
                      </span>
                      <span className="text-gray-400 text-xl">/100</span>
                    </div>
                  )}
                  <button 
                    onClick={() => router.push(`/evaluate/${evaluationId}/result`)}
                    className="w-full py-3 bg-[#722F37] text-white rounded-lg font-semibold hover:bg-[#5A252C] transition-colors"
                  >
                    View Report
                  </button>
                </div>
              ) : (
                <div className="space-y-6">
                  <div className="w-20 h-20 bg-[#FAF4E8] rounded-full flex items-center justify-center mx-auto mb-4 relative">
                    <Sparkles className="w-10 h-10 text-[#DAA520] animate-pulse" />
                    <div className="absolute inset-0 border-4 border-[#DAA520]/30 rounded-full border-t-[#DAA520] animate-spin" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-[#722F37] mb-2">
                      {state.currentStage === 'deep_synthesis' ? 'Deep Synthesis' : 'Quality Gate'}
                    </h2>
                    <p className="text-gray-600">
                      {state.currentStage === 'deep_synthesis' 
                        ? 'Connecting patterns across categories...' 
                        : 'Finalizing scores and recommendations...'}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {state.error && (
          <div className="fixed bottom-4 right-4 max-w-md bg-white border-l-4 border-red-500 shadow-lg rounded-r-lg p-4 animate-in slide-in-from-right">
            <div className="flex items-start gap-3">
              <AlertTriangle className="text-red-500 flex-shrink-0" />
              <div>
                <h3 className="font-bold text-gray-900">Error</h3>
                <p className="text-sm text-gray-600">{state.error}</p>
              </div>
            </div>
          </div>
        )}

      </main>
    </div>
  );
};
