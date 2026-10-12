import React from 'react';
import { Terminal, Moon, Sun, CheckCircle2, RefreshCw } from 'lucide-react';
import { GithubIcon } from './GithubIcon.tsx';

interface HeaderProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  isLightMode: boolean;
  setIsLightMode: (val: boolean) => void;
  onRefresh: () => void;
  isRefreshing: boolean;
  lastRefresh?: string;
}

export const Header: React.FC<HeaderProps> = ({
  currentTab,
  setCurrentTab,
  isLightMode,
  setIsLightMode,
  onRefresh,
  isRefreshing,
  lastRefresh,
}) => {
  const tabs = [
    { id: 'overview', label: 'Systems Overview' },
    { id: 'projects', label: 'Selected Work' },
    { id: 'telemetry', label: 'Telemetry & Stats' },
    { id: 'contribution', label: 'Art & Motion' },
    { id: 'readme', label: 'README Studio' },
    { id: 'verifier', label: 'System Verifier' },
  ];

  return (
    <header className={`sticky top-0 z-40 border-b backdrop-blur-md transition-colors ${
      isLightMode 
        ? 'bg-[#FFFFFF]/90 border-[#BAD6CB] text-[#11231F]' 
        : 'bg-[#0D1214]/90 border-[#285047] text-[#F0F3EE]'
    }`}>
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`p-2 rounded-lg border flex items-center justify-center font-mono ${
              isLightMode 
                ? 'bg-[#E2F0EA] border-[#BAD6CB] text-[#0D604B]' 
                : 'bg-[#14272A] border-[#285047] text-[#8DE0C1]'
            }`}>
              <Terminal className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold tracking-tight text-base sm:text-lg">Sarthak Sulkhlan</span>
                <span className={`text-xs px-2 py-0.5 rounded border font-mono ${
                  isLightMode
                    ? 'bg-[#E2F0EA] border-[#BAD6CB] text-[#0D604B]'
                    : 'bg-[#101B1D] border-[#285047] text-[#8DE0C1]'
                }`}>
                  B.Tech CSE (Data Science)
                </span>
              </div>
              <p className={`text-xs ${isLightMode ? 'text-[#466058]' : 'text-[#B3C3BE]'}`}>
                software · data science · applied AI
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2 sm:space-x-3">
            <button
              onClick={onRefresh}
              disabled={isRefreshing}
              title={lastRefresh ? `Last refreshed: ${lastRefresh}` : 'Refresh GitHub Data'}
              className={`p-2 rounded-lg border text-xs font-mono transition-all flex items-center space-x-1.5 cursor-pointer ${
                isLightMode
                  ? 'border-[#BAD6CB] bg-[#FFFFFF] hover:bg-[#E2F0EA] text-[#0D604B]'
                  : 'border-[#285047] bg-[#101B1D] hover:bg-[#14272A] text-[#8DE0C1]'
              } ${isRefreshing ? 'opacity-60 cursor-not-allowed' : ''}`}
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
              <span className="hidden md:inline">{isRefreshing ? 'Refreshing...' : 'Sync Telemetry'}</span>
            </button>

            <button
              onClick={() => setIsLightMode(!isLightMode)}
              title="Toggle Color Theme"
              className={`p-2 rounded-lg border transition-all cursor-pointer ${
                isLightMode
                  ? 'border-[#BAD6CB] bg-[#FFFFFF] hover:bg-[#E2F0EA] text-[#0D604B]'
                  : 'border-[#285047] bg-[#101B1D] hover:bg-[#14272A] text-[#8DE0C1]'
              }`}
            >
              {isLightMode ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
            </button>

            <a
              href="https://github.com/Sarthaksulkhlan"
              target="_blank"
              rel="noreferrer"
              className={`p-2 rounded-lg border transition-all flex items-center space-x-1 text-xs font-mono ${
                isLightMode
                  ? 'border-[#BAD6CB] bg-[#FFFFFF] hover:bg-[#E2F0EA] text-[#11231F]'
                  : 'border-[#285047] bg-[#101B1D] hover:bg-[#14272A] text-[#F0F3EE]'
              }`}
            >
              <GithubIcon className="w-4 h-4" />
              <span className="hidden sm:inline">GitHub</span>
            </a>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center space-x-1 overflow-x-auto mt-3 pt-2 border-t border-inherit no-scrollbar">
          {tabs.map((tab) => {
            const active = currentTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setCurrentTab(tab.id)}
                className={`px-3 py-1.5 text-xs sm:text-sm font-medium rounded-md whitespace-nowrap transition-colors cursor-pointer ${
                  active
                    ? isLightMode
                      ? 'bg-[#0D604B] text-white shadow-sm'
                      : 'bg-[#285047] text-[#8DE0C1] shadow-sm'
                    : isLightMode
                      ? 'text-[#466058] hover:text-[#11231F] hover:bg-[#E2F0EA]'
                      : 'text-[#B3C3BE] hover:text-[#F0F3EE] hover:bg-[#101B1D]'
                }`}
              >
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
};
