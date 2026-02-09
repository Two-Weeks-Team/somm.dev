import React, { useState, useEffect, useRef } from 'react';
import { Eye, EyeOff, Key, Loader2, AlertCircle, CheckCircle, ArrowRight } from 'lucide-react';
import { api } from '@/lib/api';

interface APIKeyFormProps {
  onSuccess: () => void;
}

export const APIKeyForm: React.FC<APIKeyFormProps> = ({ onSuccess }) => {
  const [apiKey, setApiKey] = useState('');
  const [showKey, setShowKey] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!apiKey.trim()) {
      setError('API key is required');
      return;
    }

    setIsLoading(true);
    setError(null);
    setSuccess(false);

    try {
      await api.registerKey('google', apiKey);
      setSuccess(true);
      setApiKey('');
      timeoutRef.current = setTimeout(() => {
        onSuccess();
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to register API key');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-[#722F37]/10 p-6 md:p-8">
      <div className="mb-6">
        <h3 className="text-xl font-semibold text-[#722F37] flex items-center gap-2">
          <Key className="w-5 h-5" />
          Register New API Key
        </h3>
        <p className="text-gray-600 mt-2 text-sm">
          Add your Google Gemini API key to enable AI evaluation features.
          Your key will be encrypted and stored securely.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-2">
          <label className="block text-sm font-medium text-[#722F37]">
            Provider
          </label>
          <div className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-500 text-sm font-medium">
            Google Gemini
          </div>
        </div>

        <div className="space-y-2">
          <label htmlFor="apiKey" className="block text-sm font-medium text-[#722F37]">
            API Key
          </label>
          <div className="relative">
            <input
              id="apiKey"
              type={showKey ? 'text' : 'password'}
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="AIza..."
              className="w-full pl-4 pr-12 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-[#722F37] focus:border-[#722F37] transition-colors outline-none"
              disabled={isLoading}
            />
            <button
              type="button"
              onClick={() => setShowKey(!showKey)}
              aria-label={showKey ? 'Hide API key' : 'Show API key'}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-[#722F37] transition-colors"
            >
              {showKey ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </button>
          </div>
          <p className="text-xs text-amber-600 flex items-start gap-1.5 mt-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            Your key will be validated by making a test API call to Google.
          </p>
        </div>

        {error && (
          <div className="p-4 bg-red-50 border border-red-100 rounded-xl flex items-start gap-3 text-red-700 text-sm">
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="p-4 bg-green-50 border border-green-100 rounded-xl flex items-start gap-3 text-green-700 text-sm">
            <CheckCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <span>API key registered successfully! Redirecting...</span>
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading || !apiKey.trim()}
          className="w-full flex items-center justify-center gap-2 py-3 px-6 bg-[#722F37] text-[#F7E7CE] rounded-xl font-medium hover:bg-[#5A252C] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#722F37] disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Validating...
            </>
          ) : (
            <>
              Register Key
              <ArrowRight className="w-5 h-5" />
            </>
          )}
        </button>
      </form>
    </div>
  );
};
