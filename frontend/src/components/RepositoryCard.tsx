import React from 'react';
import { Star, GitFork, Lock, Globe, Building2, User } from 'lucide-react';
import { Repository } from '@/lib/api';

interface RepositoryCardProps {
  repository: Repository;
  isSelected?: boolean;
  onSelect?: (repository: Repository) => void;
}

export const RepositoryCard: React.FC<RepositoryCardProps> = ({
  repository,
  isSelected = false,
  onSelect,
}) => {
  const handleClick = () => {
    onSelect?.(repository);
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div
      data-testid="repository-card"
      onClick={handleClick}
      className={`
        relative p-4 rounded-lg border cursor-pointer transition-all duration-200
        ${isSelected 
          ? 'border-[#722F37] bg-[#722F37]/5 ring-2 ring-[#722F37]/20' 
          : 'border-gray-200 hover:border-[#722F37]/50 hover:bg-gray-50'
        }
      `}
    >
      {/* Header: Owner badge, Name and Visibility */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          {repository.owner && (
            <span
              className={`inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-full flex-shrink-0 ${
                repository.owner.type === 'Organization'
                  ? 'bg-purple-100 text-purple-700'
                  : 'bg-blue-100 text-blue-700'
              }`}
              title={repository.owner.type === 'Organization' ? 'Organization' : 'Personal'}
            >
              {repository.owner.type === 'Organization' ? (
                <Building2 className="w-3 h-3" />
              ) : (
                <User className="w-3 h-3" />
              )}
              {repository.owner.login}
            </span>
          )}
          <h3 className="font-semibold text-gray-900 truncate" title={repository.name}>
            {repository.name}
          </h3>
        </div>
        <span className="flex-shrink-0">
          {repository.private ? (
            <Lock className="w-4 h-4 text-gray-500" />
          ) : (
            <Globe className="w-4 h-4 text-gray-500" />
          )}
        </span>
      </div>

      {/* Description */}
      {repository.description && (
        <p className="mt-1 text-sm text-gray-600 line-clamp-2">
          {repository.description}
        </p>
      )}

      {/* Footer: Stats */}
      <div className="mt-3 flex items-center gap-4 text-xs text-gray-500">
        {/* Language */}
        {repository.language && (
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-[#722F37]" />
            {repository.language}
          </span>
        )}

        {/* Stars */}
        {repository.stars > 0 && (
          <span className="flex items-center gap-1">
            <Star className="w-3 h-3" />
            {repository.stars}
          </span>
        )}

        {/* Forks */}
        {repository.forks > 0 && (
          <span className="flex items-center gap-1">
            <GitFork className="w-3 h-3" />
            {repository.forks}
          </span>
        )}

        {/* Updated date */}
        {repository.updated_at && (
          <span className="ml-auto">
            Updated {formatDate(repository.updated_at)}
          </span>
        )}
      </div>

      {/* Selected indicator */}
      {isSelected && (
        <div className="absolute top-2 right-2 w-2 h-2 rounded-full bg-[#722F37]" />
      )}
    </div>
  );
};
