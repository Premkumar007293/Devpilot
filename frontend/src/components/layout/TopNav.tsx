import React from 'react';
import { useLocation } from 'react-router-dom';
import { Search, Bell, ChevronRight, Github, Command } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';

const ROUTE_LABELS: Record<string, string> = {
  '/': 'Overview',
  '/repositories': 'Repositories',
  '/analysis': 'Code Analysis',
  '/security': 'Security Audits',
  '/architecture': 'Architecture Graph',
  '/assistant': 'AI Assistant',
  '/settings': 'Settings',
};

export const TopNav: React.FC = () => {
  const location = useLocation();
  const { setSearchModalOpen, notificationsCount } = useAppStore();

  const currentTitle = ROUTE_LABELS[location.pathname] || 'Workspace';

  return (
    <header className="sticky top-0 z-20 flex items-center justify-between h-16 px-6 border-b border-white/[0.07] bg-dark-900/80 backdrop-blur-xl">
      {/* Breadcrumb Navigation */}
      <div className="flex items-center gap-2 text-xs font-medium text-slate-400">
        <span className="text-slate-400 hover:text-slate-300 transition-colors">Workspace</span>
        <ChevronRight className="w-3.5 h-3.5 text-slate-400 shrink-0" />
        <span className="text-slate-400 hover:text-slate-300 transition-colors">DevPilot</span>
        <ChevronRight className="w-3.5 h-3.5 text-slate-400 shrink-0" />
        <span className="text-slate-100 font-semibold">{currentTitle}</span>
      </div>

      {/* Global Actions */}
      <div className="flex items-center gap-3">
        {/* Global Search Bar */}
        <button
          onClick={() => setSearchModalOpen(true)}
          className="flex items-center justify-between w-64 md:w-80 px-3 py-1.5 text-xs text-slate-400 rounded-lg bg-dark-850/80 hover:bg-dark-800 border border-white/[0.08] hover:border-white/15 transition-all group"
        >
          <div className="flex items-center gap-2">
            <Search className="w-3.5 h-3.5 text-slate-400 group-hover:text-slate-300 transition-colors" />
            <span className="text-slate-400 group-hover:text-slate-300">Search repos, files, AST...</span>
          </div>
          <div className="flex items-center gap-1 font-mono text-[10px] bg-dark-900 px-1.5 py-0.5 rounded border border-white/[0.08] text-slate-400">
            <Command className="w-3 h-3" />
            <span>K</span>
          </div>
        </button>

        {/* GitHub Shortcut */}
        <button
          onClick={() => {
            alert('GitHub OAuth Integration is scheduled for Phase 2 implementation.');
          }}
          title="Connect GitHub Account"
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-300 hover:text-white rounded-lg bg-dark-850 border border-white/[0.08] hover:border-white/20 transition-all"
        >
          <Github className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Connect</span>
        </button>

        {/* Notifications Icon with Badge */}
        <button
          onClick={() => alert('No new critical alerts. 3 informational audits logged.')}
          className="relative p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-white/[0.05] border border-transparent hover:border-white/10 transition-colors"
          aria-label="Notifications"
        >
          <Bell className="w-4 h-4" />
          {notificationsCount > 0 && (
            <span className="absolute top-1.5 right-1.5 flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-500" />
            </span>
          )}
        </button>

        {/* User Profile Placeholder */}
        <div className="flex items-center gap-2 pl-2 border-l border-white/[0.08]">
          <div className="relative flex items-center justify-center w-8 h-8 rounded-full bg-gradient-to-tr from-brand-600 to-brand-accent text-white font-semibold text-xs border border-white/20 shadow-glow-sm">
            <span>DA</span>
            <span className="absolute bottom-0 right-0 w-2 h-2 rounded-full bg-emerald-400 ring-2 ring-dark-900" />
          </div>
          <div className="hidden lg:flex flex-col text-left">
            <span className="text-xs font-semibold text-slate-200 leading-none">Dev Architect</span>
            <span className="text-[10px] text-brand-300 font-mono mt-0.5">Enterprise Tier</span>
          </div>
        </div>
      </div>
    </header>
  );
};
