import React from 'react';
import { Network } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';

export const ArchitecturePage: React.FC = () => {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between pb-2 border-b border-white/[0.06]">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Interactive Architecture Visualization</h1>
          <p className="text-xs text-slate-400 mt-1">
            Dependency graph generation, component coupling analysis, and microservice boundary maps.
          </p>
        </div>
        <Badge variant="violet">Phase 1 Foundation</Badge>
      </div>

      <Card className="p-8 text-center space-y-4">
        <div className="mx-auto flex items-center justify-center w-16 h-16 rounded-2xl bg-brand-500/10 border border-brand-500/25 text-brand-300 shadow-glow-sm">
          <Network className="w-8 h-8" />
        </div>
        <div className="max-w-md mx-auto space-y-2">
          <h3 className="text-base font-semibold text-white">Architecture Dependency Graph</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            In future phases, this view will render an interactive canvas showing circular dependencies, module coupling, API service contracts, and database schema relationships.
          </p>
        </div>
        <div className="pt-2 flex justify-center gap-3">
          <span className="text-[11px] font-mono px-3 py-1 rounded bg-dark-800 text-slate-300 border border-white/10">
            Engine: GraphViz / Cytoscape Canvas Ready
          </span>
        </div>
      </Card>
    </div>
  );
};
