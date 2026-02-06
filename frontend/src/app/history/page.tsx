'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '../../lib/api';
import { EvaluationHistoryItem } from '../../types';
import { Calendar, ChevronRight, Search, Loader2 } from 'lucide-react';

export default function HistoryPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [history, setHistory] = useState<EvaluationHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  useEffect(() => {
    if (authLoading) return;
    
    if (!isAuthenticated) {
      router.push('/evaluate');
      return;
    }

    const fetchHistory = async () => {
      try {
        setLoading(true);
        const { items } = await api.getHistory(page, 10);
        setHistory((prev) => (page === 1 ? items : [...prev, ...items]));
        setHasMore(items.length === 10);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load history');
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [page, isAuthenticated, authLoading, router]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'processing':
        return 'bg-blue-100 text-blue-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (authLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-[#722F37]" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FAFAFA] py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-[#722F37] font-serif">
            Tasting History
          </h1>
          <button
            onClick={() => router.push('/evaluate')}
            className="px-4 py-2 bg-[#722F37] text-white rounded-lg hover:bg-[#5a252c] transition-colors"
          >
            New Tasting
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 text-red-700">
            {error}
          </div>
        )}

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          {history.length === 0 && !loading ? (
            <div className="p-12 text-center text-gray-500">
              <Search className="mx-auto h-12 w-12 text-gray-300 mb-4" />
              <p className="text-lg">No tastings found yet.</p>
              <p className="text-sm">Start your first evaluation to see it here.</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-100">
              {history.map((item) => (
                <div
                  key={item.id}
                  onClick={() => router.push(item.status === 'completed' ? `/evaluate/${item.id}/result` : `/progress/${item.id}`)}
                  className="p-6 hover:bg-gray-50 transition-colors cursor-pointer flex items-center justify-between group"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center mb-1">
                      <h3 className="text-lg font-medium text-gray-900 truncate mr-3">
                        {item.repoUrl.replace('https://github.com/', '')}
                      </h3>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${getStatusColor(item.status)}`}>
                        {item.status}
                      </span>
                    </div>
                    <div className="flex items-center text-sm text-gray-500">
                      <Calendar size={14} className="mr-1.5" />
                      {formatDate(item.createdAt)}
                    </div>
                  </div>

                  <div className="flex items-center ml-4">
                    {item.totalScore !== undefined && (
                      <div className="text-right mr-4">
                        <div className="text-2xl font-bold text-[#722F37]">{item.totalScore}</div>
                        <div className="text-xs text-gray-500">Score</div>
                      </div>
                    )}
                    <ChevronRight className="text-gray-300 group-hover:text-[#722F37] transition-colors" />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {hasMore && (
          <div className="mt-8 text-center">
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={loading}
              className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#722F37] disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin -ml-1 mr-2 h-4 w-4" />
                  Loading...
                </>
              ) : (
                'Load More'
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
