import React from 'react';
import { Cpu, CheckCircle2, AlertCircle, Layers } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';

export const CodeAnalysisPage: React.FC = () => {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between pb-2 border-b border-white/[0.06]">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Code Intelligence & Static Analysis</h1>
          <p className="text-xs text-slate-400 mt-1">
            AST syntax trees, code complexity metrics, dead code detection, and cyclomatic score evaluations.
          </p>
        </div>
        <Badge variant="violet">Phase 1 Foundation</Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <Card className="p-5 space-y-3">
          <div className="flex items-center gap-2 text-brand-300">
            <Cpu className="w-5 h-5" />
            <h3 className="font-semibold text-sm text-white">AST Parser Engine</h3>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Abstract Syntax Tree parsing engine architecture registered in backend <code className="text-brand-300">app.engines.analyzer</code>.
          </p>
          <div className="pt-2 text-xs font-mono text-emerald-400 flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4" />
            <span>Interface Architecture Defined</span>
          </div>
        </Card>

        <Card className="p-5 space-y-3">
          <div className="flex items-center gap-2 text-cyan-300">
            <Layers className="w-5 h-5" />
            <h3 className="font-semibold text-sm text-white">Cyclomatic Complexity</h3>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Measures nested branch complexity, function line length, and cognitive load across repository files.
          </p>
          <div className="pt-2 text-xs font-mono text-emerald-400 flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4" />
            <span>Service Contract Prepared</span>
          </div>
        </Card>

        <Card className="p-5 space-y-3">
          <div className="flex items-center gap-2 text-amber-300">
            <AlertCircle className="w-5 h-5" />
            <h3 className="font-semibold text-sm text-white">Rule Evaluation</h3>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Static linting and quality gate rules designed to prevent regressions and anti-patterns.
          </p>
          <div className="pt-2 text-xs font-mono text-emerald-400 flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4" />
            <span>Ready for Phase 2 Workers</span>
          </div>
        </Card>
      </div>
    </div>
  );
};
