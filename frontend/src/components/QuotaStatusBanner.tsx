import React, { useEffect, useState } from 'react';
import { Wine, Key, Sparkles, AlertCircle, Infinity as InfinityIcon } from 'lucide-react';
import { api, QuotaStatus } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { EvaluationMode } from '@/types';
import Link from 'next/link';

interface QuotaStatusBannerProps {
  evaluationMode: EvaluationMode;
}

export const QuotaStatusBanner: React.FC<QuotaStatusBannerProps> = ({ evaluationMode }) => {
  const { isAuthenticated } = useAuth();
  const [quota, setQuota] = useState<QuotaStatus | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      loadQuota();
    }
  }, [isAuthenticated]);

  const loadQuota = async () => {
    try {
      setLoading(true);
      const data = await api.getQuotaStatus();
      setQuota(data);
    } catch (error) {
      console.error('Failed to load quota status:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated || loading || !quota) return null;

  // Admin / Unlimited Plan
  if (quota.is_unlimited && !quota.has_byok) {
    return null;
  }

  const isGrandTasting = evaluationMode === 'grand_tasting';
  const isFree = quota.plan === 'free';
  const hasByok = quota.has_byok;
  const isQuotaExceeded = quota.remaining <= 0;

  // Case: Full Techniques (Grand Tasting) selected + Free + No BYOK
  if (isGrandTasting && isFree && !hasByok) {
    return (
      <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 shadow-sm">
        <div className="flex items-start gap-3">
          <div className="rounded-full bg-amber-100 p-2 text-amber-600">
            <Key size={20} />
          </div>
          <div className="flex-1">
            <h4 className="font-medium text-amber-900">API Key Required for Grand Tasting</h4>
            <p className="mt-1 text-sm text-amber-700">
              The Grand Tasting mode uses 75+ evaluation techniques and requires your own Gemini API key.
            </p>
            <Link 
              href="/settings/api-keys"
              className="mt-3 inline-flex items-center gap-2 text-sm font-medium text-amber-800 hover:text-amber-900 hover:underline"
            >
              Register API Key <span aria-hidden="true">&rarr;</span>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Case: Free + BYOK Registered
  if (isFree && hasByok) {
    return (
      <div className="rounded-xl border border-[#2E4A3F]/20 bg-[#2E4A3F]/5 p-4 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="rounded-full bg-[#2E4A3F]/10 p-2 text-[#2E4A3F]">
            <InfinityIcon size={20} />
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-[#2E4A3F]">
              Unlimited evaluations (using your API key)
            </p>
          </div>
          <div className="flex items-center gap-1 rounded-full bg-[#2E4A3F]/10 px-2.5 py-0.5 text-xs font-medium text-[#2E4A3F]">
            <Key size={12} />
            <span>Active</span>
          </div>
        </div>
      </div>
    );
  }

  // Case: Free + Quota Exceeded
  if (isFree && isQuotaExceeded) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-4 shadow-sm">
        <div className="flex items-start gap-3">
          <div className="rounded-full bg-red-100 p-2 text-red-600">
            <AlertCircle size={20} />
          </div>
          <div className="flex-1">
            <h4 className="font-medium text-red-900">Daily limit reached</h4>
            <p className="mt-1 text-sm text-red-700">
              You have used all your free evaluations for today. Register your own API key for unlimited access.
            </p>
            <Link 
              href="/settings/api-keys"
              className="mt-3 inline-flex items-center gap-2 text-sm font-medium text-red-800 hover:text-red-900 hover:underline"
            >
              Register Free API Key <span aria-hidden="true">&rarr;</span>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Case: Free + Remaining > 0
  if (isFree) {
    return (
      <div className="rounded-xl border border-[#722F37]/10 bg-[#FAF4E8] p-4 shadow-sm">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <div className="rounded-full bg-[#722F37]/10 p-2 text-[#722F37]">
              <Wine size={20} />
            </div>
            <div>
              <p className="text-sm font-medium text-[#722F37]">
                Free evaluations today: <span className="font-bold">{quota.remaining}/{quota.daily_limit}</span>
              </p>
              <p className="text-xs text-[#722F37]/70">
                Resets at midnight UTC
              </p>
            </div>
          </div>
          <Link 
            href="/settings/api-keys"
            className="group flex items-center gap-2 rounded-lg bg-white px-3 py-2 text-xs font-medium text-[#722F37] shadow-sm ring-1 ring-inset ring-[#722F37]/10 transition-colors hover:bg-[#F7E7CE]/20"
          >
            <Sparkles size={14} className="text-amber-500" />
            <span>Get Unlimited</span>
          </Link>
        </div>
      </div>
    );
  }

  // Case: Paid Plan
  return (
    <div className="rounded-xl border border-[#722F37]/10 bg-[#FAF4E8] p-4 shadow-sm">
      <div className="flex items-center gap-3">
        <div className="rounded-full bg-[#722F37]/10 p-2 text-[#722F37]">
          <Wine size={20} />
        </div>
        <div className="flex-1">
          <p className="text-sm font-medium text-[#722F37]">
            Today: {quota.used_today}/{quota.daily_limit} evaluations
          </p>
        </div>
        <div className="rounded-full bg-[#722F37] px-2.5 py-0.5 text-xs font-medium text-[#F7E7CE]">
          Premium
        </div>
      </div>
    </div>
  );
};
