import React from 'react';
import { GitBranch, ArrowUpRight } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { Badge } from '../common/Badge';
import { RepositoryItem } from '../../types';

interface RecentActivityTableProps {
  repositories: RepositoryItem[];
}

export const RecentActivityTable: React.FC<RecentActivityTableProps> = ({ repositories }) => {
  const getStatusBadge = (status: RepositoryItem['status']) => {
    switch (status) {
      case 'clean':
        return (
          <Badge variant="success" dot>
            Passed
          </Badge>
        );
      case 'warning':
        return (
          <Badge variant="warning" dot>
            4 Warnings
          </Badge>
        );
      case 'alert':
        return (
          <Badge variant="error" dot>
            2 Critical
          </Badge>
        );
      default:
        return <Badge variant="outline">Idle</Badge>;
    }
  };

  return (
    <Card className="overflow-hidden">
      <CardHeader>
        <div className="flex items-center justify-between w-full">
          <div>
            <CardTitle>Recent Repository Activity</CardTitle>
            <p className="text-xs text-slate-400 mt-0.5">Monitored repositories & automated intelligence scans</p>
          </div>
          <Badge variant="violet" size="sm">
            Phase 1 Mock Preview
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-white/[0.06] bg-dark-900/60 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                <th className="py-3 px-5">Repository</th>
                <th className="py-3 px-4">Language & Branch</th>
                <th className="py-3 px-4">Security Status</th>
                <th className="py-3 px-4 text-center">Health Score</th>
                <th className="py-3 px-4 text-right">Last Scanned</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.04] text-xs">
              {repositories.map((repo) => (
                <tr
                  key={repo.id}
                  className="hover:bg-white/[0.02] transition-colors group cursor-pointer"
                  onClick={() => alert(`Phase 2 will open repository deep-dive for ${repo.fullName}`)}
                >
                  <td className="py-3.5 px-5">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-slate-200 group-hover:text-brand-300 transition-colors">
                        {repo.name}
                      </span>
                      <ArrowUpRight className="w-3.5 h-3.5 text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                    <span className="text-[11px] text-slate-400 truncate block max-w-xs">{repo.description}</span>
                  </td>

                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-2">
                      <span
                        className="w-2 h-2 rounded-full shrink-0"
                        style={{ backgroundColor: repo.languageColor }}
                      />
                      <span className="font-mono text-slate-300">{repo.language}</span>
                      <span className="text-slate-400">•</span>
                      <span className="flex items-center gap-1 font-mono text-slate-400">
                        <GitBranch className="w-3 h-3" />
                        {repo.branch}
                      </span>
                    </div>
                  </td>

                  <td className="py-3.5 px-4">{getStatusBadge(repo.status)}</td>

                  <td className="py-3.5 px-4 text-center">
                    <span
                      className={`font-mono font-bold px-2 py-0.5 rounded text-xs ${
                        repo.healthScore >= 90
                          ? 'text-emerald-400 bg-emerald-500/10'
                          : repo.healthScore >= 75
                          ? 'text-amber-400 bg-amber-500/10'
                          : 'text-rose-400 bg-rose-500/10'
                      }`}
                    >
                      {repo.healthScore}%
                    </span>
                  </td>

                  <td className="py-3.5 px-4 text-right font-mono text-slate-400 whitespace-nowrap">
                    {repo.lastScanned}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
};
