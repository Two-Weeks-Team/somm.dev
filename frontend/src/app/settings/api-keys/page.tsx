"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { APIKeyManager } from "@/components/settings/APIKeyManager";
import { Settings, ChevronRight } from "lucide-react";

export default function APIKeysPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/");
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading) {
    return null;
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-[#FAF4E8] py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Breadcrumb / Header */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 text-sm text-[#722F37]/60">
            <Settings className="w-4 h-4" />
            <span>Settings</span>
            <ChevronRight className="w-4 h-4" />
            <span className="font-medium text-[#722F37]">API Keys</span>
          </div>
          
          <div>
            <h1 className="text-3xl font-bold text-[#722F37] font-serif-elegant">
              API Key Management
            </h1>
            <p className="mt-2 text-lg text-gray-600">
              Manage your personal API keys for accessing advanced evaluation features.
            </p>
          </div>
        </div>

        <APIKeyManager />
      </div>
    </div>
  );
}
