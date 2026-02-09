'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { Shield, Users, Crown, Loader2, AlertCircle, Check } from 'lucide-react';
import { cn } from '@/lib/utils';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.somm.dev';

interface AdminUser {
  id: string;
  username: string;
  email: string | null;
  github_id: string | null;
  avatar_url: string | null;
  role: string;
  plan: string;
  created_at: string | null;
}

const ROLE_OPTIONS = ['user', 'admin'] as const;
const PLAN_OPTIONS = ['free', 'premium', 'pro', 'enterprise'] as const;

const PLAN_COLORS: Record<string, string> = {
  free: 'bg-gray-100 text-gray-700',
  premium: 'bg-amber-100 text-amber-800',
  pro: 'bg-purple-100 text-purple-800',
  enterprise: 'bg-blue-100 text-blue-800',
};

const ROLE_COLORS: Record<string, string> = {
  user: 'bg-gray-100 text-gray-700',
  admin: 'bg-red-100 text-red-800',
};

export default function AdminPage() {
  const { token, isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState<string | null>(null);
  const [saved, setSaved] = useState<string | null>(null);
  const [accessDenied, setAccessDenied] = useState(false);
  const savedTimerRef = useRef<ReturnType<typeof setTimeout>>(null);

  const fetchUsers = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/api/admin/users`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.status === 403) {
        setAccessDenied(true);
        return;
      }
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setUsers(await res.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load users');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth');
      return;
    }
    if (isAuthenticated) fetchUsers();
  }, [isAuthenticated, authLoading, fetchUsers, router]);

  useEffect(() => {
    return () => {
      if (savedTimerRef.current) clearTimeout(savedTimerRef.current);
    };
  }, []);

  const updateUser = async (userId: string, field: 'role' | 'plan', value: string) => {
    if (!token) return;
    setSaving(userId);
    try {
      const res = await fetch(`${API_URL}/api/admin/users/${userId}`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ [field]: value }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `HTTP ${res.status}`);
      }
      const updated: AdminUser = await res.json();
      setUsers((prev) => prev.map((u) => (u.id === userId ? updated : u)));
      setSaved(userId);
      if (savedTimerRef.current) clearTimeout(savedTimerRef.current);
      savedTimerRef.current = setTimeout(() => setSaved(null), 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Update failed');
    } finally {
      setSaving(null);
    }
  };

  if (authLoading || loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-[#722F37]" />
      </div>
    );
  }

  if (accessDenied) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <Shield className="w-16 h-16 text-red-400" />
        <h1 className="text-2xl font-bold text-gray-900">Access Denied</h1>
        <p className="text-gray-600">관리자 권한이 필요합니다.</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="flex items-center gap-3 mb-8">
        <div className="rounded-full bg-[#722F37] p-2.5">
          <Shield className="h-6 w-6 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
          <p className="text-sm text-gray-500">Manage user roles and subscription plans</p>
        </div>
      </div>

      {error && (
        <div className="mb-6 flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          <AlertCircle size={16} />
          {error}
          <button onClick={() => setError(null)} className="ml-auto text-red-600 hover:text-red-800">✕</button>
        </div>
      )}

      <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-100 bg-gray-50/50">
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">User</th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Role</th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Plan</th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {users.map((user) => (
              <tr key={user.id} className="hover:bg-gray-50/50 transition-colors">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    {user.avatar_url ? (
                      <img src={user.avatar_url} alt="" className="w-9 h-9 rounded-full" />
                    ) : (
                      <div className="w-9 h-9 rounded-full bg-[#722F37]/10 flex items-center justify-center">
                        <Users size={16} className="text-[#722F37]" />
                      </div>
                    )}
                    <div>
                      <p className="font-medium text-gray-900">{user.username}</p>
                      <p className="text-xs text-gray-500">{user.email || user.id}</p>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <select
                    value={user.role}
                    onChange={(e) => updateUser(user.id, 'role', e.target.value)}
                    disabled={saving === user.id}
                    className="rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-sm focus:border-[#722F37] focus:ring-1 focus:ring-[#722F37] outline-none"
                  >
                    {ROLE_OPTIONS.map((r) => (
                      <option key={r} value={r}>{r}</option>
                    ))}
                  </select>
                </td>
                <td className="px-6 py-4">
                  <select
                    value={user.plan}
                    onChange={(e) => updateUser(user.id, 'plan', e.target.value)}
                    disabled={saving === user.id}
                    className="rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-sm focus:border-[#722F37] focus:ring-1 focus:ring-[#722F37] outline-none"
                  >
                    {PLAN_OPTIONS.map((p) => (
                      <option key={p} value={p}>{p}</option>
                    ))}
                  </select>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <span className={cn('inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium', ROLE_COLORS[user.role] || ROLE_COLORS.user)}>
                      {user.role === 'admin' && <Shield size={10} className="mr-1" />}
                      {user.role}
                    </span>
                    <span className={cn('inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium', PLAN_COLORS[user.plan] || PLAN_COLORS.free)}>
                      {user.plan !== 'free' && <Crown size={10} className="mr-1" />}
                      {user.plan}
                    </span>
                    {saving === user.id && <Loader2 size={14} className="animate-spin text-gray-400" />}
                    {saved === user.id && <Check size={14} className="text-green-500" />}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {users.length === 0 && !loading && (
          <div className="px-6 py-12 text-center text-gray-500">No users found</div>
        )}
      </div>
    </div>
  );
}
