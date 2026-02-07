'use client';

import React, { useEffect, useState, lazy, Suspense, useCallback, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api } from '../../../../lib/api';
import { EvaluationResult } from '../../../../types';
import { ArrowLeft, Share2, Download, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { ResultTabs, useResultTab, ResultTabId } from '../../../../components/ResultTabs';
import { TastingNotesTab } from '../../../../components/TastingNotesTab';
import { GraphSkeleton } from '../../../../components/graph/GraphSkeleton';
import { cn } from '../../../../lib/utils';
import { exportResultToPdf } from '../../../../lib/exportPdf';

const Graph2DTab = lazy(() => import('../../../../components/Graph2DTab').then(m => ({ default: m.Graph2DTab })));
const Graph3DTab = lazy(() => import('../../../../components/Graph3DTab').then(m => ({ default: m.Graph3DTab })));

function TabLoadingFallback() {
  return (
    <div className="md:h-[600px] h-[400px]">
      <GraphSkeleton />
    </div>
  );
}

function getScoreTier(score: number): { label: string; color: string } {
  if (score >= 90) return { label: 'Grand Cru', color: 'bg-[#722F37]/20 text-[#722F37]' };
  if (score >= 80) return { label: 'Premier Cru', color: 'bg-emerald-100 text-emerald-700' };
  if (score >= 70) return { label: 'Village', color: 'bg-blue-100 text-blue-700' };
  return { label: 'Table Wine', color: 'bg-gray-100 text-gray-700' };
}

interface ToastState {
  message: string;
  type: 'success' | 'error';
  visible: boolean;
}

export default function ResultPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  
  const [result, setResult] = useState<EvaluationResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useResultTab('tasting');
  const [showStickyHeader, setShowStickyHeader] = useState(false);
  const [toast, setToast] = useState<ToastState>({ message: '', type: 'success', visible: false });
  const [isExporting, setIsExporting] = useState(false);
  const toastTimerRef = useRef<ReturnType<typeof setTimeout>>();

  const showToast = useCallback((message: string, type: 'success' | 'error' = 'success') => {
    if (toastTimerRef.current) {
      clearTimeout(toastTimerRef.current);
    }
    setToast({ message, type, visible: true });
    toastTimerRef.current = setTimeout(() => {
      setToast(prev => ({ ...prev, visible: false }));
    }, 3000);
  }, []);

  useEffect(() => {
    return () => {
      if (toastTimerRef.current) {
        clearTimeout(toastTimerRef.current);
      }
    };
  }, []);

  const handleShare = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      showToast('Link copied to clipboard!', 'success');
    } catch {
      showToast('Failed to copy link', 'error');
    }
  };

  const handleExportPdf = async () => {
    if (!result || isExporting) return;
    
    setIsExporting(true);
    try {
      await exportResultToPdf(result);
      showToast('PDF exported successfully!', 'success');
    } catch {
      showToast('Failed to export PDF', 'error');
    } finally {
      setIsExporting(false);
    }
  };

  useEffect(() => {
    const handleScroll = () => {
      setShowStickyHeader(window.scrollY > 300);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    const fetchResult = async () => {
      try {
        const data = await api.getEvaluationResult(id);
        setResult(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load results');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchResult();
    }
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#FAFAFA]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#722F37] mx-auto mb-4"></div>
          <p className="text-[#722F37] font-medium">Decanting results...</p>
        </div>
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#FAFAFA]">
        <div className="text-center max-w-md mx-auto p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Corked!</h2>
          <p className="text-gray-600 mb-6">{error || 'Result not found'}</p>
          <button
            onClick={() => router.push('/evaluate')}
            className="px-6 py-2 bg-[#722F37] text-white rounded-lg hover:bg-[#5a252c] transition-colors"
          >
            Try Another Vintage
          </button>
        </div>
      </div>
    );
  }

  const renderTabContent = (tabId: ResultTabId) => {
    switch (tabId) {
      case 'tasting':
        return <TastingNotesTab result={result} />;
      case 'graph-2d':
        return (
          <Suspense fallback={<TabLoadingFallback />}>
            <Graph2DTab evaluationId={id} />
          </Suspense>
        );
      case 'graph-3d':
        return (
          <Suspense fallback={<TabLoadingFallback />}>
            <Graph3DTab evaluationId={id} />
          </Suspense>
        );
      default:
        return null;
    }
  };

  const tier = result ? getScoreTier(result.totalScore || 0) : null;

  return (
    <div className="min-h-screen bg-[#FAFAFA]">
      <div
        className={cn(
          'fixed top-0 left-0 right-0 z-40 transition-all duration-300',
          showStickyHeader
            ? 'translate-y-0 opacity-100'
            : '-translate-y-full opacity-0 pointer-events-none'
        )}
      >
        <div className="bg-white/90 backdrop-blur-md border-b border-gray-200 shadow-sm">
          <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <button
                  onClick={() => router.push('/evaluate')}
                  className="p-2 text-gray-500 hover:text-[#722F37] transition-colors"
                >
                  <ArrowLeft size={20} />
                </button>
                <div className="flex items-center gap-3">
                  <span className="text-2xl font-bold text-[#722F37]">
                    {result?.totalScore || 0}
                  </span>
                  <span className="text-gray-400">/100</span>
                  {tier && (
                    <span className={cn('px-2 py-0.5 rounded-full text-xs font-medium', tier.color)}>
                      {tier.label}
                    </span>
                  )}
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => router.push('/evaluate')}
                  className="px-3 py-1.5 text-sm font-medium text-[#722F37] bg-white border border-[#722F37] rounded-lg hover:bg-gray-50 transition-colors"
                >
                  New Tasting
                </button>
                <button
                  onClick={handleShare}
                  className="p-2 text-[#722F37] hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <Share2 size={18} />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-6">
          <button
            onClick={() => router.push('/evaluate')}
            className="flex items-center text-gray-600 hover:text-[#722F37] transition-colors"
          >
            <ArrowLeft size={20} className="mr-2" />
            New Tasting
          </button>
          <div className="flex space-x-4">
            <button
              onClick={handleShare}
              className="flex items-center px-4 py-2 text-sm font-medium text-[#722F37] bg-white border border-[#722F37] rounded-lg hover:bg-[#FAFAFA] transition-colors"
            >
              <Share2 size={16} className="mr-2" />
              Share
            </button>
            <button
              onClick={handleExportPdf}
              disabled={isExporting}
              className="flex items-center px-4 py-2 text-sm font-medium text-white bg-[#722F37] rounded-lg hover:bg-[#5a252c] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isExporting ? (
                <Loader2 size={16} className="mr-2 animate-spin" />
              ) : (
                <Download size={16} className="mr-2" />
              )}
              {isExporting ? 'Exporting...' : 'Export PDF'}
            </button>
          </div>
        </div>

        <ResultTabs activeTab={activeTab} onTabChange={setActiveTab} />

        {renderTabContent(activeTab)}
      </div>

      <div
        role="status"
        aria-hidden={!toast.visible}
        className={cn(
          'fixed bottom-4 right-4 flex items-center gap-2 px-4 py-3 rounded-lg shadow-lg transition-all duration-300 z-50',
          toast.visible
            ? 'opacity-100 translate-y-0'
            : 'opacity-0 translate-y-2 pointer-events-none',
          toast.type === 'success'
            ? 'bg-green-50 text-green-700 border border-green-200'
            : 'bg-red-50 text-red-700 border border-red-200'
        )}
      >
        {toast.type === 'success' ? (
          <CheckCircle className="h-4 w-4" />
        ) : (
          <XCircle className="h-4 w-4" />
        )}
        <span className="text-sm font-medium">{toast.message}</span>
      </div>
    </div>
  );
}
