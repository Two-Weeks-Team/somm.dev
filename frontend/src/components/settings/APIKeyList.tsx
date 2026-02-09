import React, { useState } from 'react';
import { Trash2, Calendar, Key, ShieldCheck, Loader2 } from 'lucide-react';
import { api, KeyStatusResponse } from '@/lib/api';

interface APIKeyListProps {
  keys: KeyStatusResponse[];
  onDelete: () => void;
}

export const APIKeyList: React.FC<APIKeyListProps> = ({ keys, onDelete }) => {
  const [deletingProvider, setDeletingProvider] = useState<string | null>(null);

  const handleDelete = async (provider: string) => {
    if (!confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
      return;
    }

    setDeletingProvider(provider);
    try {
      await api.deleteKey(provider);
      onDelete();
    } catch (error) {
      console.error('Failed to delete key:', error);
      alert('Failed to delete API key. Please try again.');
    } finally {
      setDeletingProvider(null);
    }
  };

  if (keys.length === 0) {
    return (
      <div className="text-center py-12 bg-white/50 rounded-2xl border border-dashed border-gray-300">
        <Key className="w-12 h-12 text-gray-300 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900">No API keys registered</h3>
        <p className="text-gray-500 mt-1">Add a key above to get started.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-[#722F37] flex items-center gap-2">
        <ShieldCheck className="w-5 h-5" />
        Registered Keys
      </h3>
      
      <div className="grid gap-4">
        {keys.map((key) => (
          <div 
            key={key.provider}
            className="bg-white rounded-xl border border-gray-200 p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="flex items-start gap-4">
              <div className="p-3 bg-[#FAF4E8] rounded-lg text-[#722F37]">
                <Key className="w-6 h-6" />
              </div>
              <div>
                <h4 className="font-medium text-gray-900 capitalize">
                  {key.provider === 'google' ? 'Google Gemini' : key.provider}
                </h4>
                <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
                  <span className="font-mono bg-gray-100 px-2 py-0.5 rounded text-xs">
                    {key.key_hint}
                  </span>
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    {key.registered_at ? new Date(key.registered_at).toLocaleDateString() : 'Unknown'}
                  </span>
                </div>
              </div>
            </div>

            <button
              onClick={() => handleDelete(key.provider)}
              disabled={deletingProvider === key.provider}
              className="flex items-center justify-center gap-2 px-4 py-2 text-red-600 bg-red-50 hover:bg-red-100 rounded-lg transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {deletingProvider === key.provider ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Trash2 className="w-4 h-4" />
              )}
              Delete
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
