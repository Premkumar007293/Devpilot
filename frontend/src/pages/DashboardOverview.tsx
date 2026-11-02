import React from 'react';
import {
  FolderGit2,
  ScanEye,
  Bug,
  ShieldAlert,
  Sparkles,
  Server,
  Terminal,
} from 'lucide-react';
import { MetricCard } from '../components/ui/MetricCard';
import { RecentActivityTable } from '../components/ui/RecentActivityTable';
import { AnalysisTimeline } from '../components/ui/AnalysisTimeline';
import { GitHubConnectBanner } from '../components/ui/GitHubConnectBanner';
import { useAppStore } from '../store/useAppStore';

export const DashboardOverview: React.FC = () => {
  const { repositories, activities, backendHealth } = useAppStore();

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Welcome & Overview Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-white/[0.06]">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-white">
              Engineering Intelligence Dashboard
            </h1>
            <span className="flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded-full bg-brand-500/15 text-brand-300 border border-brand-500/30">
              <Sparkles className="w-3 h-3 text-brand-400" />
              Phase 1 Architecture Active
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
            Continuous static analysis, AST code intelligence, and vulnerability auditing across connected repositories.
          </p>
        </div>

        {/* Live Architecture Status Pill */}
        <div className="flex items-center gap-3 p-2 rounded-lg bg-dark-850/80 border border-white/[0.06] text-xs font-mono">
          <div className="flex items-center gap-1.5 text-slate-300">
            <Server className="w-3.5 h-3.5 text-brand-400" />
            <span>FastAPI:</span>
            <span className={backendHealth.status === 'healthy' ? 'text-emerald-400' : 'text-amber-400'}>
              {backendHealth.status}
            </span>
          </div>
          <span className="text-slate-400">•</span>
          <div className="flex items-center gap-1.5 text-slate-400">
            <Terminal className="w-3.5 h-3.5" />
            <span>v{backendHealth.version}</span>
          </div>
        </div>
      </div>

      {/* Metrics Row (4 Cards as requested) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Total Repositories"
          value="12"
          change="+2 this week"
          changeType="positive"
          description="4 repositories currently synced"
          icon={FolderGit2}
          accentColor="violet"
        />
        <MetricCard
          label="Analyzed Repositories"
          value="8"
          change="67% coverage"
          changeType="positive"
          description="AST & static graphs parsed"
          icon={ScanEye}
          accentColor="cyan"
        />
        <MetricCard
          label="Issues Detected"
          value="34"
          change="-6 resolved"
          changeType="positive"
          description="Linting, dead code & complexity"
          icon={Bug}
          accentColor="amber"
        />
        <MetricCard
          label="Security Alerts"
          value="2"
          change="0 zero-day"
          changeType="negative"
          description="Requires engineer review"
          icon={ShieldAlert}
          accentColor="rose"
        />
      </div>

      {/* Quick Action: Connect GitHub Banner */}
      <GitHubConnectBanner />

      {/* Two-Column Activity & Analysis Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <RecentActivityTable repositories={repositories} />
        </div>
        <div className="lg:col-span-1">
          <AnalysisTimeline activities={activities} />
        </div>
      </div>
    </div>
  );
};
