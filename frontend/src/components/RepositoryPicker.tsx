import React, { useState, useMemo } from 'react';
import { Search, RefreshCw, Loader2, Github } from 'lucide-react';
import { Repository, AuthError } from '@/lib/api';
import { RepositoryCard } from './RepositoryCard';

interface RepositoryPickerProps {
  repositories: Repository[];
  isLoading: boolean;
  error: Error | null;
  selectedId?: number;
  onSelect: (repository: Repository) => void;
  onRefresh: () => void;
  onReLogin?: () => void;
}

export const RepositoryPicker: React.FC<RepositoryPickerProps> = ({
  repositories,
  isLoading,
  error,
  selectedId,
  onSelect,
  onRefresh,
  onReLogin,
}) => {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredRepositories = useMemo(() => {
    if (!searchQuery.trim()) return repositories;
    
    const query = searchQuery.toLowerCase();
    return repositories.filter(
      (repo) =>
        repo.name.toLowerCase().includes(query) ||
        (repo.description && repo.description.toLowerCase().includes(query)) ||
        repo.full_name.toLowerCase().includes(query)
    );
  }, [repositories, searchQuery]);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2 text-gray-500">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span>Loading repositories...</span>
        </div>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-24 rounded-lg border border-gray-200 bg-gray-50 animate-pulse"
            />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    const isAuth = error instanceof AuthError;
    const showLoginButton = isAuth && onReLogin;
    
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-center">
        <p className="text-red-600 mb-3">{error.message}</p>
        {showLoginButton ? (
          <button
            onClick={onReLogin}
            className="inline-flex items-center gap-2 px-4 py-2 bg-[#722F37] text-white rounded-lg hover:bg-[#5a252c] transition-colors"
          >
            <Github className="w-4 h-4" />
            Login with GitHub
          </button>
        ) : (
          <button
            onClick={onRefresh}
            className="inline-flex items-center gap-2 px-4 py-2 bg-[#722F37] text-white rounded-lg hover:bg-[#5a252c] transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Try Again
          </button>
        )}
      </div>
    );
  }

  if (repositories.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-gray-50 p-8 text-center">
        <p className="text-gray-600 mb-3">No repositories found</p>
        <button
          onClick={onRefresh}
          className="inline-flex items-center gap-2 px-4 py-2 bg-[#722F37] text-white rounded-lg hover:bg-[#5a252c] transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Search and Refresh */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search repositories..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#722F37] focus:border-[#722F37] outline-none"
          />
        </div>
        <button
          onClick={onRefresh}
          className="p-2 text-gray-600 hover:text-[#722F37] hover:bg-gray-100 rounded-lg transition-colors"
          title="Refresh repositories"
        >
          <RefreshCw className="w-5 h-5" />
        </button>
      </div>

      {/* Repository count */}
      <div className="text-sm text-gray-500">
        Showing {filteredRepositories.length} of {repositories.length} repositories
      </div>

      {/* Repository list */}
      <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2">
        {filteredRepositories.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No repositories match your search
          </div>
        ) : (
          filteredRepositories.map((repo) => (
            <RepositoryCard
              key={repo.id}
              repository={repo}
              isSelected={repo.id === selectedId}
              onSelect={onSelect}
            />
          ))
        )}
      </div>
    </div>
  );
};
