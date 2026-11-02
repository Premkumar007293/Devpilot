import React from 'react';
import { Cpu, GitCommit, Clock } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { AnalysisActivity } from '../../types';

interface AnalysisTimelineProps {
  activities: AnalysisActivity[];
}

export const AnalysisTimeline: React.FC<AnalysisTimelineProps> = ({ activities }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Analysis Activity</CardTitle>
        <span className="text-[11px] font-mono text-slate-400">Live Queue</span>
      </CardHeader>

      <CardContent className="p-5 space-y-4">
        {activities.map((act) => (
          <div
            key={act.id}
            className="flex items-start gap-3 p-3 rounded-lg bg-dark-800/40 hover:bg-dark-800/80 border border-white/[0.04] hover:border-white/[0.08] transition-all"
          >
            <div className="flex items-center justify-center w-7 h-7 rounded-md bg-brand-500/10 border border-brand-500/20 text-brand-300 shrink-0 mt-0.5">
              <Cpu className="w-3.5 h-3.5" />
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-semibold text-slate-200 truncate">{act.type}</span>
                <span className="text-[11px] font-mono text-slate-400 shrink-0">{act.timestamp}</span>
              </div>

              <div className="flex items-center gap-2 mt-1 text-[11px] text-slate-400 font-mono">
                <span className="text-slate-300 font-medium">{act.repository}</span>
                <span>•</span>
                <span className="flex items-center gap-0.5">
                  <GitCommit className="w-3 h-3" />
                  {act.commitHash}
                </span>
                <span>•</span>
                <span className="flex items-center gap-0.5 text-slate-400">
                  <Clock className="w-3 h-3" />
                  {act.duration}
                </span>
              </div>

              {/* Findings preview */}
              <div className="flex items-center gap-2 mt-2">
                {act.findings.critical > 0 && (
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-rose-500/15 text-rose-300 border border-rose-500/20">
                    {act.findings.critical} critical
                  </span>
                )}
                {act.findings.warnings > 0 && (
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-300 border border-amber-500/20">
                    {act.findings.warnings} warnings
                  </span>
                )}
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-white/[0.06]">
                  {act.findings.info} info
                </span>
              </div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
};
