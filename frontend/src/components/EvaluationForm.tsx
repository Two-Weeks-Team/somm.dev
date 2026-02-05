import React, { useState, useEffect } from 'react';
import { CriteriaType } from '../types';
import { CriteriaSelector } from './CriteriaSelector';
import { RepositoryPicker } from './RepositoryPicker';
import { useAuth } from '@/contexts/AuthContext';
import { useRepoValidation } from '@/hooks/useRepoValidation';
import { api, Repository, AuthError } from '@/lib/api';
import { Search, Loader2, AlertCircle, Github, CheckCircle, Lock, XCircle } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.somm.dev";

interface EvaluationFormProps {
  onSubmit: (repoUrl: string, criteria: CriteriaType) => Promise<void>;
  isLoading?: boolean;
  error?: string | null;
}

type TabType = 'repos' | 'url';

export const EvaluationForm: React.FC<EvaluationFormProps> = ({ onSubmit, isLoading = false, error = null }) => {
  const [activeTab, setActiveTab] = useState<TabType>('repos');
  const [repoUrl, setRepoUrl] = useState('');
  const [criteria, setCriteria] = useState<CriteriaType>('basic');
  const [validationError, setValidationError] = useState<string | null>(null);
  const [selectedRepoId, setSelectedRepoId] = useState<number | undefined>();

  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [isLoadingRepos, setIsLoadingRepos] = useState(false);
  const [reposError, setReposError] = useState<Error | null>(null);

  const { isAuthenticated, token, login } = useAuth();
  const { validation, validateRepo, clearValidation } = useRepoValidation(500);

  useEffect(() => {
    if (activeTab === 'repos' && isAuthenticated && token) {
      loadRepositories();
    }
  }, [activeTab, isAuthenticated, token]);

  const loadRepositories = async () => {
    if (!token) return;

    setIsLoadingRepos(true);
    setReposError(null);

    try {
      const response = await api.getRepositories(token);
      setRepositories(response.repositories);
    } catch (err) {
      setReposError(err instanceof Error ? err : new Error('Failed to load repositories'));
    } finally {
      setIsLoadingRepos(false);
    }
  };

  const handleRefresh = async () => {
    if (!token) return;

    setIsLoadingRepos(true);
    setReposError(null);

    try {
      const response = await api.refreshRepositories(token);
      setRepositories(response.repositories);
    } catch (err) {
      setReposError(err instanceof Error ? err : new Error('Failed to refresh repositories'));
    } finally {
      setIsLoadingRepos(false);
    }
  };

  const handleRepoSelect = (repo: Repository) => {
    setSelectedRepoId(repo.id);
    setRepoUrl(repo.html_url);
    setValidationError(null);
    clearValidation();
  };

  const validateUrl = (url: string) => {
    const githubUrlRegex = /^https:\/\/github\.com\/[\w-]+\/[\w-.]+$/;
    if (!url) return 'Repository URL is required';
    if (!githubUrlRegex.test(url)) return 'Please enter a valid GitHub repository URL (e.g., https://github.com/owner/repo)';
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    if (!isAuthenticated) {
      setValidationError("Please login to submit an evaluation.");
      return;
    }

    const error = validateUrl(repoUrl);
    if (error) {
      setValidationError(error);
      return;
    }

    await onSubmit(repoUrl, criteria);
  };

  const handleOAuthLogin = () => {
    window.location.href = `${API_URL}/auth/github`;
  };

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const hashParams = new URLSearchParams(window.location.hash.replace('#', ''));
    const oauthToken = urlParams.get('token') || hashParams.get('token');
    if (oauthToken) {
      login(oauthToken).then(() => {
        window.history.replaceState({}, document.title, window.location.pathname);
      });
    }
  }, [login]);

  return (
    <form onSubmit={handleSubmit} className="space-y-8 max-w-2xl mx-auto p-6 bg-white rounded-xl shadow-sm border border-gray-100">
      <div className="flex border-b border-gray-200">
        <button
          type="button"
          onClick={() => setActiveTab('repos')}
          className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'repos'
              ? 'border-[#722F37] text-[#722F37]'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Github className="w-4 h-4" />
          My Repos
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('url')}
          className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'url'
              ? 'border-[#722F37] text-[#722F37]'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Search className="w-4 h-4" />
          Enter URL
        </button>
      </div>

      {activeTab === 'repos' ? (
        <div className="space-y-4">
          {!isAuthenticated ? (
            <div className="text-center py-8">
              <p className="text-gray-600 mb-4">Sign in with GitHub to see your repositories</p>
              <button
                type="button"
                onClick={handleOAuthLogin}
                className="inline-flex items-center gap-2 px-6 py-3 bg-[#722F37] text-white rounded-lg hover:bg-[#5a252c] transition-colors"
              >
                <Github className="w-5 h-5" />
                Login with GitHub
              </button>
            </div>
          ) : (
            <RepositoryPicker
              repositories={repositories}
              isLoading={isLoadingRepos}
              error={reposError}
              selectedId={selectedRepoId}
              onSelect={handleRepoSelect}
              onRefresh={handleRefresh}
              onReLogin={handleOAuthLogin}
            />
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {!isAuthenticated && (
            <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
              Login is required to submit a repository URL.
            </div>
          )}
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
                const value = e.target.value;
                setRepoUrl(value);
                if (validationError) setValidationError(null);
                validateRepo(value);
              }}
              placeholder="https://github.com/username/repository"
              className={`block w-full pl-10 pr-10 py-3 border rounded-lg text-gray-900 placeholder:text-gray-400 focus:ring-[#722F37] focus:border-[#722F37] transition-colors ${
                validationError || error || validation.status === 'invalid'
                  ? 'border-red-300 bg-red-50'
                  : validation.status === 'valid'
                  ? 'border-green-300 bg-green-50'
                  : 'border-gray-300'
              }`}
              disabled={isLoading}
            />
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
              {validation.status === 'checking' && (
                <Loader2 className="h-5 w-5 text-gray-400 animate-spin" />
              )}
              {validation.status === 'valid' && (
                <CheckCircle className="h-5 w-5 text-green-500" />
              )}
              {validation.status === 'invalid' && (
                <XCircle className="h-5 w-5 text-red-500" />
              )}
              {validation.status === 'private' && (
                <Lock className="h-5 w-5 text-amber-500" />
              )}
              {validation.status === 'error' && (
                <AlertCircle className="h-5 w-5 text-red-500" />
              )}
            </div>
          </div>
          {validation.message && (
            <div
              className={`text-sm flex items-center gap-2 ${
                validation.status === 'valid'
                  ? 'text-green-600'
                  : validation.status === 'private'
                  ? 'text-amber-600'
                  : 'text-red-600'
              }`}
            >
              {validation.status === 'checking' && <Loader2 className="w-4 h-4 animate-spin" />}
              {validation.status === 'valid' && <CheckCircle className="w-4 h-4" />}
              {validation.status === 'invalid' && <XCircle className="w-4 h-4" />}
              {validation.status === 'private' && <Lock className="w-4 h-4" />}
              {validation.status === 'error' && <AlertCircle className="w-4 h-4" />}
              {validation.message}
            </div>
          )}
        </div>
      )}

      {(validationError || error) && (
        <div className="flex items-center space-x-2 text-red-600 text-sm">
          <AlertCircle size={16} />
          <span>{validationError || error}</span>
        </div>
      )}

      <CriteriaSelector value={criteria} onChange={setCriteria} />

      <button
        type="submit"
        disabled={isLoading || !repoUrl || !isAuthenticated}
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
