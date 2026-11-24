import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  GitBranch,
  Code2,
  ShieldAlert,
  Network,
  Bot,
  Settings,
  Sparkles,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  Rocket,
} from 'lucide-react';
import { cn } from '../../utils/cn';
import { useAppStore } from '../../store/useAppStore';
import { StatusIndicator } from '../common/StatusIndicator';

interface NavItemDef {
  name: string;
  path: string;
  icon: React.ElementType;
  badge?: string;
  badgeVariant?: 'default' | 'violet';
}

const NAV_ITEMS: NavItemDef[] = [
  { name: 'Overview', path: '/', icon: LayoutDashboard },
  { name: 'Onboarding', path: '/onboarding', icon: Rocket },
  { name: 'Repositories', path: '/repositories', icon: GitBranch, badge: '4' },
  { name: 'Code Analysis', path: '/analysis', icon: Code2 },
  { name: 'Security', path: '/security', icon: ShieldAlert, badge: '2 Critical', badgeVariant: 'violet' },
  { name: 'Architecture', path: '/architecture', icon: Network },
  { name: 'AI Assistant', path: '/assistant', icon: Bot, badge: 'Phase 2' },
  { name: 'Settings', path: '/settings', icon: Settings },
];

export const Sidebar: React.FC = () => {
  const { sidebarOpen, toggleSidebar, backendHealth } = useAppStore();

  return (
    <aside
      className={cn(
        'relative flex flex-col h-screen border-r border-white/[0.07] bg-dark-900/90 backdrop-blur-xl transition-all duration-300 z-30 select-none shrink-0',
        sidebarOpen ? 'w-64' : 'w-20'
      )}
    >
      {/* Brand Header */}
      <div className="flex items-center justify-between h-16 px-4 border-b border-white/[0.06]">
        <NavLink to="/" className="flex items-center gap-3 overflow-hidden group">
          <div className="relative flex items-center justify-center w-9 h-9 rounded-lg bg-gradient-to-br from-brand-600/40 via-brand-accent/20 to-transparent border border-brand-500/30 group-hover:border-brand-400/50 shadow-glow-sm transition-all shrink-0">
            <Sparkles className="w-4 h-4 text-brand-300 animate-pulse-subtle" />
          </div>
          {sidebarOpen && (
            <div className="flex flex-col min-w-0">
              <div className="flex items-center gap-1.5">
                <span className="font-bold text-base tracking-tight text-white group-hover:text-brand-200 transition-colors">
                  DevPilot
                </span>
                <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-brand-500/10 text-brand-300 border border-brand-500/20">
                  v1.0
                </span>
              </div>
              <span className="text-[11px] text-slate-400 truncate">Code Intelligence</span>
            </div>
          )}
        </NavLink>

        {/* Collapse Toggle */}
        <button
          onClick={toggleSidebar}
          aria-label={sidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/[0.06] border border-transparent hover:border-white/10 transition-colors"
        >
          {sidebarOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </button>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className={cn('px-2 mb-2 text-[11px] font-medium uppercase tracking-wider text-slate-400', !sidebarOpen && 'hidden')}>
          Platform
        </div>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  'group flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150',
                  isActive
                    ? 'bg-brand-600/15 text-white border border-brand-500/30 shadow-glow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.04] border border-transparent'
                )
              }
              title={!sidebarOpen ? item.name : undefined}
            >
              <Icon className="w-4 h-4 shrink-0 transition-transform group-hover:scale-105" />
              {sidebarOpen && (
                <div className="flex items-center justify-between w-full min-w-0">
                  <span className="truncate">{item.name}</span>
                  {item.badge && (
                    <span
                      className={cn(
                        'text-[10px] font-mono px-1.5 py-0.5 rounded border leading-none',
                        item.badgeVariant === 'violet'
                          ? 'bg-brand-500/20 text-brand-300 border-brand-500/30'
                          : 'bg-dark-800 text-slate-400 border-white/10'
                      )}
                    >
                      {item.badge}
                    </span>
                  )}
                </div>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Footer Info / Live Status */}
      <div className="p-3 border-t border-white/[0.06] bg-dark-950/40">
        {sidebarOpen ? (
          <div className="flex flex-col gap-2 p-2.5 rounded-lg bg-dark-850/60 border border-white/[0.05]">
            <div className="flex items-center justify-between">
              <span className="text-[11px] text-slate-400">Backend Service</span>
              <StatusIndicator status={backendHealth.status} />
            </div>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-between text-[11px] text-brand-300 hover:text-brand-200 transition-colors font-mono pt-1 border-t border-white/[0.04]"
            >
              <span>FastAPI Docs</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        ) : (
          <div className="flex justify-center py-1">
            <StatusIndicator status={backendHealth.status} showLabel={false} />
          </div>
        )}
      </div>
    </aside>
  );
};
