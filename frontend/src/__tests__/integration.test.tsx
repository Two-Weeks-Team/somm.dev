import { render, screen, fireEvent } from '@testing-library/react';
import { AuthProvider } from '@/contexts/AuthContext';
import { RepositoryPicker } from '@/components/RepositoryPicker';
import { RepositoryCard } from '@/components/RepositoryCard';
import { Repository } from '@/lib/api';

describe('Repository Selection Flow Integration', () => {
  const mockRepository: Repository = {
    id: 1,
    name: 'test-repo',
    full_name: 'owner/test-repo',
    description: 'Test repository for integration tests',
    private: false,
    html_url: 'https://github.com/owner/test-repo',
    default_branch: 'main',
    stars: 10,
    forks: 5,
    language: 'TypeScript',
    updated_at: '2024-01-01T00:00:00Z',
    pushed_at: '2024-01-01T00:00:00Z',
  };

  describe('RepositoryCard', () => {
    it('renders repository information correctly', () => {
      render(<RepositoryCard repository={mockRepository} />);

      expect(screen.getByText('test-repo')).toBeInTheDocument();
      expect(screen.getByText('Test repository for integration tests')).toBeInTheDocument();
      expect(screen.getByText('TypeScript')).toBeInTheDocument();
    });

    it('calls onSelect when clicked', () => {
      const onSelect = jest.fn();
      render(<RepositoryCard repository={mockRepository} onSelect={onSelect} />);

      fireEvent.click(screen.getByText('test-repo'));
      expect(onSelect).toHaveBeenCalledWith(mockRepository);
    });

    it('shows selected state when isSelected is true', () => {
      render(<RepositoryCard repository={mockRepository} isSelected={true} />);

      const card = screen.getByTestId('repository-card');
      expect(card).toHaveClass('border-[#722F37]');
    });
  });

  describe('RepositoryPicker', () => {
    const mockRepos: Repository[] = [
      mockRepository,
      {
        id: 2,
        name: 'another-repo',
        full_name: 'owner/another-repo',
        description: 'Another test repo',
        private: true,
        html_url: 'https://github.com/owner/another-repo',
        default_branch: 'main',
        stars: 5,
        forks: 2,
        language: 'Python',
        updated_at: '2024-01-02T00:00:00Z',
        pushed_at: '2024-01-02T00:00:00Z',
      },
    ];

    it('renders list of repositories', () => {
      render(
        <RepositoryPicker
          repositories={mockRepos}
          isLoading={false}
          error={null}
          onSelect={jest.fn()}
          onRefresh={jest.fn()}
        />
      );

      expect(screen.getByText('test-repo')).toBeInTheDocument();
      expect(screen.getByText('another-repo')).toBeInTheDocument();
    });

    it('filters repositories based on search query', () => {
      render(
        <RepositoryPicker
          repositories={mockRepos}
          isLoading={false}
          error={null}
          onSelect={jest.fn()}
          onRefresh={jest.fn()}
        />
      );

      const searchInput = screen.getByPlaceholderText('Search repositories...');
      fireEvent.change(searchInput, { target: { value: 'another' } });

      expect(screen.queryByText('test-repo')).not.toBeInTheDocument();
      expect(screen.getByText('another-repo')).toBeInTheDocument();
    });

    it('shows loading state', () => {
      render(
        <RepositoryPicker
          repositories={[]}
          isLoading={true}
          error={null}
          onSelect={jest.fn()}
          onRefresh={jest.fn()}
        />
      );

      expect(screen.getByText('Loading repositories...')).toBeInTheDocument();
    });

    it('shows error state with retry button', () => {
      const onRefresh = jest.fn();
      const error = new Error('Failed to load repositories');
      render(
        <RepositoryPicker
          repositories={[]}
          isLoading={false}
          error={error}
          onSelect={jest.fn()}
          onRefresh={onRefresh}
        />
      );

      expect(screen.getByText('Failed to load repositories')).toBeInTheDocument();
      fireEvent.click(screen.getByText('Try Again'));
      expect(onRefresh).toHaveBeenCalled();
    });

    it('shows empty state when no repositories', () => {
      render(
        <RepositoryPicker
          repositories={[]}
          isLoading={false}
          error={null}
          onSelect={jest.fn()}
          onRefresh={jest.fn()}
        />
      );

      expect(screen.getByText('No repositories found')).toBeInTheDocument();
    });
  });
});

describe('AuthContext Integration', () => {
  it('provides auth context to children', () => {
    const TestComponent = () => {
      return <div>Test Component</div>;
    };

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByText('Test Component')).toBeInTheDocument();
  });
});
