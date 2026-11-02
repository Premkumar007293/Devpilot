import React from 'react';
import { ShieldAlert, Lock } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';

export const SecurityPage: React.FC = () => {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between pb-2 border-b border-white/[0.06]">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Security Vulnerability Detection</h1>
          <p className="text-xs text-slate-400 mt-1">
            OWASP Top 10, CWE security checks, hardcoded secret scanners, and dependency CVE vulnerability tracking.
          </p>
        </div>
        <Badge variant="violet">Phase 1 Foundation</Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="p-5 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-rose-400">
              <ShieldAlert className="w-5 h-5" />
              <h3 className="text-sm font-semibold text-white">Hardcoded Secret Detection</h3>
            </div>
            <Badge variant="error" size="sm">Rule Architecture Ready</Badge>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Detects leaked API keys, private tokens, passwords, and database credentials before they reach production branches.
          </p>
        </Card>

        <Card className="p-5 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-amber-400">
              <Lock className="w-5 h-5" />
              <h3 className="text-sm font-semibold text-white">CVE Dependency Audits</h3>
            </div>
            <Badge variant="warning" size="sm">Integrations Hooked</Badge>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Cross-references package manifests (package.json, requirements.txt, Cargo.lock, go.mod) against the National Vulnerability Database.
          </p>
        </Card>
      </div>
    </div>
  );
};
