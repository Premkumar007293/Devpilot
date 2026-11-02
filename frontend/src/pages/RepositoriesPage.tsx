import React from 'react';
import { GitBranch, Plus } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { useAppStore } from '../store/useAppStore';

export const RepositoriesPage: React.FC = () => {
  const { repositories } = useAppStore();

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-white/[0.06]">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Repositories</h1>
          <p className="text-xs text-slate-400 mt-1">
            Connected repositories indexed for AI assistance, static scans, and vulnerability detection.
          </p>
        </div>
        <Button
          variant="primary"
          size="md"
          icon={<Plus className="w-4 h-4" />}
          onClick={() => alert('Repository addition through GitHub OAuth is scheduled for Phase 2.')}
        >
          Add Repository
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {repositories.map((repo) => (
          <Card key={repo.id} glow className="p-5 space-y-4">
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-semibold text-white">{repo.name}</h3>
                  <Badge variant={repo.status === 'clean' ? 'success' : 'warning'} size="sm">
                    {repo.status.toUpperCase()}
                  </Badge>
                </div>
                <p className="text-xs font-mono text-slate-400">{repo.fullName}</p>
              </div>
              <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-brand-500/10 text-brand-300 border border-brand-500/20">
                Score: {repo.healthScore}%
              </span>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">{repo.description}</p>

            <div className="flex items-center justify-between pt-3 border-t border-white/[0.06] text-xs font-mono text-slate-400">
              <div className="flex items-center gap-3">
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: repo.languageColor }} />
                  {repo.language}
                </span>
                <span className="flex items-center gap-1 text-slate-400">
                  <GitBranch className="w-3.5 h-3.5" />
                  {repo.branch}
                </span>
              </div>
              <span>Scanned {repo.lastScanned}</span>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};
