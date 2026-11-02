import React from 'react';
import { Database, Server } from 'lucide-react';
import { Card } from '../components/common/Card';
import { useAppStore } from '../store/useAppStore';
import { StatusIndicator } from '../components/common/StatusIndicator';

export const SettingsPage: React.FC = () => {
  const { backendHealth } = useAppStore();

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between pb-2 border-b border-white/[0.06]">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Platform Settings</h1>
          <p className="text-xs text-slate-400 mt-1">
            Environment configuration, API endpoints, database status, and AI provider credentials.
          </p>
        </div>
        <StatusIndicator status={backendHealth.status} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <Card className="p-5 space-y-4">
          <div className="flex items-center gap-2 text-brand-300">
            <Server className="w-5 h-5" />
            <h3 className="text-sm font-semibold text-white">Backend Infrastructure</h3>
          </div>

          <div className="space-y-2 text-xs font-mono">
            <div className="flex justify-between p-2.5 rounded bg-dark-800 border border-white/[0.04]">
              <span className="text-slate-400">Application</span>
              <span className="text-white font-semibold">{backendHealth.application}</span>
            </div>
            <div className="flex justify-between p-2.5 rounded bg-dark-800 border border-white/[0.04]">
              <span className="text-slate-400">Version</span>
              <span className="text-white font-semibold">v{backendHealth.version}</span>
            </div>
            <div className="flex justify-between p-2.5 rounded bg-dark-800 border border-white/[0.04]">
              <span className="text-slate-400">Health Endpoint</span>
              <span className="text-brand-300">/api/v1/health</span>
            </div>
          </div>
        </Card>

        <Card className="p-5 space-y-4">
          <div className="flex items-center gap-2 text-emerald-300">
            <Database className="w-5 h-5" />
            <h3 className="text-sm font-semibold text-white">Persistence & Caching</h3>
          </div>

          <div className="space-y-2 text-xs font-mono">
            <div className="flex justify-between p-2.5 rounded bg-dark-800 border border-white/[0.04]">
              <span className="text-slate-400">Database Engine</span>
              <span className="text-white">PostgreSQL 16 (SQLAlchemy 2.0)</span>
            </div>
            <div className="flex justify-between p-2.5 rounded bg-dark-800 border border-white/[0.04]">
              <span className="text-slate-400">Cache & Queue</span>
              <span className="text-white">Redis 7 (Celery integration ready)</span>
            </div>
            <div className="flex justify-between p-2.5 rounded bg-dark-800 border border-white/[0.04]">
              <span className="text-slate-400">Schema Migrations</span>
              <span className="text-white">Alembic Configured</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};
