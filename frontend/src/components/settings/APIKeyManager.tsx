import React, { useEffect, useState } from 'react';
import { api, KeyStatusResponse } from '@/lib/api';
import { APIKeyForm } from './APIKeyForm';
import { APIKeyList } from './APIKeyList';
import { Loader2 } from 'lucide-react';

export const APIKeyManager: React.FC = () => {
  const [keys, setKeys] = useState<KeyStatusResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchKeys = async () => {
    try {
      const data = await api.getKeyStatus();
      setKeys(data);
    } catch (error) {
      console.error('Failed to fetch API keys:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchKeys();
  }, []);

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-[#722F37]" />
      </div>
    );
  }

  const hasKeys = keys.length > 0;

  return (
    <div className="space-y-8">
      {!hasKeys && <APIKeyForm onSuccess={fetchKeys} />}
      <APIKeyList keys={keys} onDelete={fetchKeys} />
    </div>
  );
};
