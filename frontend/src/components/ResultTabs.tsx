'use client';

import React, { useEffect, useCallback } from 'react';
import { Wine, BarChart3, Box } from 'lucide-react';

export type ResultTabId = 'tasting' | 'graph-2d' | 'graph-3d';

interface Tab {
  id: ResultTabId;
  label: string;
  icon: React.ReactNode;
  hash: string;
  mobileHidden?: boolean;
}

const TABS: Tab[] = [
  { id: 'tasting', label: 'Tasting Notes', icon: <Wine size={18} />, hash: '#tasting' },
  { id: 'graph-2d', label: '2D Graph', icon: <BarChart3 size={18} />, hash: '#graph-2d' },
  { id: 'graph-3d', label: '3D Graph', icon: <Box size={18} />, hash: '#graph-3d', mobileHidden: true },
];

interface ResultTabsProps {
  activeTab: ResultTabId;
  onTabChange: (tabId: ResultTabId) => void;
}

export function ResultTabs({ activeTab, onTabChange }: ResultTabsProps) {
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    const currentIndex = TABS.findIndex(t => t.id === activeTab);
    if (e.key === 'ArrowRight') {
      const nextIndex = (currentIndex + 1) % TABS.length;
      onTabChange(TABS[nextIndex].id);
    } else if (e.key === 'ArrowLeft') {
      const prevIndex = (currentIndex - 1 + TABS.length) % TABS.length;
      onTabChange(TABS[prevIndex].id);
    }
  }, [activeTab, onTabChange]);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  const handleTabClick = (tab: Tab) => {
    onTabChange(tab.id);
    window.history.replaceState(null, '', tab.hash);
  };

  return (
    <div className="sticky top-0 z-10 bg-white border-b border-gray-200 mb-6">
      <div className="flex overflow-x-auto scrollbar-hide">
        {TABS.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => handleTabClick(tab)}
              className={`
                flex items-center gap-2 px-6 py-4 font-medium text-sm whitespace-nowrap
                transition-all duration-150 border-b-2
                ${tab.mobileHidden ? 'hidden md:flex' : 'flex'}
                ${isActive 
                  ? 'text-[#722F37] border-[#722F37] bg-[#F7E7CE]/30' 
                  : 'text-gray-600 border-transparent hover:text-[#722F37] hover:bg-gray-50'
                }
              `}
              role="tab"
              aria-selected={isActive}
              tabIndex={isActive ? 0 : -1}
            >
              {tab.icon}
              {tab.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}

function getInitialTabFromHash(initialTab: ResultTabId): ResultTabId {
  if (typeof window === 'undefined') return initialTab;
  const hash = window.location.hash;
  const tab = TABS.find(t => t.hash === hash);
  return tab?.id ?? initialTab;
}

export function useResultTab(initialTab: ResultTabId = 'tasting') {
  const [activeTab, setActiveTab] = React.useState<ResultTabId>(() => 
    getInitialTabFromHash(initialTab)
  );

  return [activeTab, setActiveTab] as const;
}
