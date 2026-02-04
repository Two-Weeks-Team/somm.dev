/**
 * @jest-environment jsdom
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { EvaluationForm } from '../src/components/EvaluationForm';
import { CriteriaSelector } from '../src/components/CriteriaSelector';
import { CriteriaType } from '../src/types';

describe('EvaluationForm Component Tests', () => {
  const defaultProps = {
    onSubmit: jest.fn(),
    isLoading: false,
    error: null,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render all form elements', () => {
      render(<EvaluationForm {...defaultProps} />);

      expect(screen.getByLabelText(/Repository URL/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Start Tasting/i })).toBeInTheDocument();
    });

    it('should render with placeholder', () => {
      render(<EvaluationForm {...defaultProps} />);

      const input = screen.getByPlaceholderText(
        'https://github.com/username/repository'
      );
      expect(input).toBeInTheDocument();
    });
  });

  describe('Validation', () => {
    it('should show error for empty URL', async () => {
      const onSubmit = jest.fn();
      render(<EvaluationForm {...defaultProps} onSubmit={onSubmit} />);

      const submitButton = screen.getByRole('button', { name: /Start Tasting/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Repository URL is required/i)).toBeInTheDocument();
      });

      expect(onSubmit).not.toHaveBeenCalled();
    });

    it('should show error for invalid GitHub URL', async () => {
      const onSubmit = jest.fn();
      render(<EvaluationForm {...defaultProps} onSubmit={onSubmit} />);

      const input = screen.getByLabelText(/Repository URL/i);
      fireEvent.change(input, { target: { value: 'not-a-url' } });

      const submitButton = screen.getByRole('button', { name: /Start Tasting/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(
          screen.getByText(/Please enter a valid GitHub repository URL/i)
        ).toBeInTheDocument();
      });
    });

    it('should accept valid GitHub URL', async () => {
      const onSubmit = jest.fn().mockResolvedValue(undefined);
      render(<EvaluationForm {...defaultProps} onSubmit={onSubmit} />);

      const input = screen.getByLabelText(/Repository URL/i);
      fireEvent.change(input, {
        target: { value: 'https://github.com/owner/repo' },
      });

      const submitButton = screen.getByRole('button', { name: /Start Tasting/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledWith(
          'https://github.com/owner/repo',
          'basic'
        );
      });
    });

    it('should clear validation error when user types', async () => {
      const onSubmit = jest.fn();
      render(<EvaluationForm {...defaultProps} onSubmit={onSubmit} />);

      // Trigger validation error
      const submitButton = screen.getByRole('button', { name: /Start Tasting/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Repository URL is required/i)).toBeInTheDocument();
      });

      // Type valid URL
      const input = screen.getByLabelText(/Repository URL/i);
      fireEvent.change(input, {
        target: { value: 'https://github.com/owner/repo' },
      });

      await waitFor(() => {
        expect(
          screen.queryByText(/Repository URL is required/i)
        ).not.toBeInTheDocument();
      });
    });
  });

  describe('Loading State', () => {
    it('should show loading state when isLoading is true', () => {
      render(<EvaluationForm {...defaultProps} isLoading={true} />);

      const submitButton = screen.getByRole('button', { name: /Sommeliers are tasting/i });
      expect(submitButton).toBeInTheDocument();
      expect(submitButton).toBeDisabled();
    });

    it('should disable input when loading', () => {
      render(<EvaluationForm {...defaultProps} isLoading={true} />);

      const input = screen.getByLabelText(/Repository URL/i);
      expect(input).toBeDisabled();
    });
  });

  describe('Error Display', () => {
    it('should display error prop', () => {
      render(
        <EvaluationForm {...defaultProps} error="GitHub API rate limit exceeded" />
      );

      expect(
        screen.getByText(/GitHub API rate limit exceeded/i)
      ).toBeInTheDocument();
    });
  });

  describe('Form Submission', () => {
    it('should call onSubmit with correct arguments', async () => {
      const onSubmit = jest.fn().mockResolvedValue(undefined);
      render(<EvaluationForm {...defaultProps} onSubmit={onSubmit} />);

      const input = screen.getByLabelText(/Repository URL/i);
      fireEvent.change(input, {
        target: { value: 'https://github.com/hackathon/project' },
      });

      const submitButton = screen.getByRole('button', { name: /Start Tasting/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledWith(
          'https://github.com/hackathon/project',
          'basic'
        );
      });
    });

    it('should prevent default form submission', async () => {
      const onSubmit = jest.fn().mockResolvedValue(undefined);
      render(<EvaluationForm {...defaultProps} onSubmit={onSubmit} />);

      const form = screen.getByRole('form');
      const preventDefault = jest.fn();

      fireEvent.submit(form, { preventDefault });

      // The form should be submitted via handleSubmit
      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalled();
      });
    });
  });
});

describe('CriteriaSelector Component Tests', () => {
  const defaultProps = {
    value: 'basic' as CriteriaType,
    onChange: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render all criteria options', () => {
      render(<CriteriaSelector {...defaultProps} />);

      expect(
        screen.getByText(/House Blend \(Basic\)/i)
      ).toBeInTheDocument();
      expect(
        screen.getByText(/Beaujolais Nouveau \(Hackathon\)/i)
      ).toBeInTheDocument();
      expect(
        screen.getByText(/Grand Cru \(Academic\)/i)
      ).toBeInTheDocument();
      expect(
        screen.getByText(/Sommelier's Choice \(Custom\)/i)
      ).toBeInTheDocument();
    });

    it('should have heading', () => {
      render(<CriteriaSelector {...defaultProps} />);

      expect(screen.getByText(/Select Your Blend/i)).toBeInTheDocument();
    });
  });

  describe('Selection', () => {
    it('should call onChange when option is clicked', () => {
      render(<CriteriaSelector {...defaultProps} />);

      const hackathonOption = screen.getByText(
        /Beaujolais Nouveau \(Hackathon\)/i
      );
      fireEvent.click(hackathonOption);

      expect(defaultProps.onChange).toHaveBeenCalledWith('hackathon');
    });

    it('should highlight selected option', () => {
      render(<CriteriaSelector {...defaultProps} value="hackathon" />);

      const hackathonOption = screen.getByText(
        /Beaujolais Nouveau \(Hackathon\)/i
      );
      
      // The selected option should have different styling (border color)
      expect(hackathonOption.closest('div')).toHaveClass('border-[#722F37]');
    });

    it('should allow switching between all criteria types', () => {
      render(<CriteriaSelector {...defaultProps} />);

      const options = [
        { text: /Beaujolais Nouveau \(Hackathon\)/i, value: 'hackathon' },
        { text: /Grand Cru \(Academic\)/i, value: 'academic' },
        { text: /Sommelier's Choice \(Custom\)/i, value: 'custom' },
        { text: /House Blend \(Basic\)/i, value: 'basic' },
      ];

      options.forEach(({ text, value }) => {
        const option = screen.getByText(text);
        fireEvent.click(option);
        expect(defaultProps.onChange).toHaveBeenCalledWith(value);
      });
    });
  });

  describe('Descriptions', () => {
    it('should display descriptions for each option', () => {
      render(<CriteriaSelector {...defaultProps} />);

      expect(
        screen.getByText(/A balanced evaluation of code quality/i)
      ).toBeInTheDocument();
      expect(
        screen.getByText(/Quick, vibrant, and focused on innovation/i)
      ).toBeInTheDocument();
      expect(
        screen.getByText(/Rigorous, structured, and detail-oriented/i)
      ).toBeInTheDocument();
      expect(
        screen.getByText(/Tailored to your specific taste/i)
      ).toBeInTheDocument();
    });
  });

  describe('Icons', () => {
    it('should render icons for each option', () => {
      render(<CriteriaSelector {...defaultProps} />);

      // Check that icons are rendered (svg elements)
      const svgElements = document.querySelectorAll('svg');
      expect(svgElements.length).toBeGreaterThanOrEqual(4);
    });
  });
});
