import React from 'react';
import { Github, X } from 'lucide-react';

interface ReAuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ReAuthModal: React.FC<ReAuthModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const handleLogin = () => {
    window.location.href = `${process.env.NEXT_PUBLIC_API_URL}/auth/github`;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="relative w-full max-w-md bg-white rounded-xl shadow-lg p-6">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="text-center">
          <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-amber-100 flex items-center justify-center">
            <Github className="w-6 h-6 text-amber-600" />
          </div>

          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Session Expired
          </h2>

          <p className="text-gray-600 mb-6">
            Your session has expired. Please login again to continue.
          </p>

          <button
            onClick={handleLogin}
            className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-[#722F37] text-white rounded-lg hover:bg-[#5a252c] transition-colors"
          >
            <Github className="w-5 h-5" />
            Login with GitHub
          </button>
        </div>
      </div>
    </div>
  );
};
