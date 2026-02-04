import React, { useState } from 'react';
import { CriteriaType } from '../types';
import { CriteriaSelector } from './CriteriaSelector';
import { Search, Loader2, AlertCircle } from 'lucide-react';

interface EvaluationFormProps {
  onSubmit: (repoUrl: string, criteria: CriteriaType) => Promise<void>;
  isLoading?: boolean;
  error?: string | null;
}

export const EvaluationForm: React.FC<EvaluationFormProps> = ({ onSubmit, isLoading = false, error = null }) => {
  const [repoUrl, setRepoUrl] = useState('');
  const [criteria, setCriteria] = useState<CriteriaType>('basic');
  const [validationError, setValidationError] = useState<string | null>(null);

  const validateUrl = (url: string) => {
    const githubUrlRegex = /^https:\/\/github\.com\/[\w-]+\/[\w-.]+$/;
    if (!url) return 'Repository URL is required';
    if (!githubUrlRegex.test(url)) return 'Please enter a valid GitHub repository URL (e.g., https://github.com/owner/repo)';
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    const error = validateUrl(repoUrl);
    if (error) {
      setValidationError(error);
      return;
    }

    await onSubmit(repoUrl, criteria);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8 max-w-2xl mx-auto p-6 bg-white rounded-xl shadow-sm border border-gray-100">
      <div className="space-y-4">
        <label htmlFor="repoUrl" className="block text-lg font-semibold text-[#722F37]">
          Repository URL
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            id="repoUrl"
            value={repoUrl}
            onChange={(e) => {
              setRepoUrl(e.target.value);
              if (validationError) setValidationError(null);
            }}
            placeholder="https://github.com/username/repository"
            className={`block w-full pl-10 pr-3 py-3 border rounded-lg focus:ring-[#722F37] focus:border-[#722F37] transition-colors ${
              validationError || error ? 'border-red-300 bg-red-50' : 'border-gray-300'
            }`}
            disabled={isLoading}
          />
        </div>
        {(validationError || error) && (
          <div className="flex items-center space-x-2 text-red-600 text-sm animate-in fade-in slide-in-from-top-1">
            <AlertCircle size={16} />
            <span>{validationError || error}</span>
          </div>
        )}
      </div>

      <CriteriaSelector value={criteria} onChange={setCriteria} />

      <button
        type="submit"
        disabled={isLoading}
        className="w-full flex items-center justify-center py-4 px-6 border border-transparent rounded-lg shadow-sm text-lg font-medium text-white bg-[#722F37] hover:bg-[#5a252c] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#722F37] disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
      >
        {isLoading ? (
          <>
            <Loader2 className="animate-spin -ml-1 mr-3 h-5 w-5" />
            Sommeliers are tasting...
          </>
        ) : (
          'Start Tasting'
        )}
      </button>
    </form>
  );
};
