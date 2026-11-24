import React, { useEffect, useMemo, useState } from 'react';
import { Activity, AlertTriangle, ArrowRight, GitBranch, Layers3, Network, Route, ShieldCheck } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { useAppStore } from '../store/useAppStore';
import { apiService, type ArchitectureSnapshot } from '../services/api';

const buildMockArchitecture = (repoName: string): ArchitectureSnapshot => {
  const baseEdges = [
    { edge_id: 'a1', source_node: 'app.init', target_node: 'app.api.routes', relationship_type: 'imports', source_file: 'app/init.py', source_line: 8, confidence: 0.96, detection_method: 'static-import' },
    { edge_id: 'a2', source_node: 'app.api.routes', target_node: 'app.services.user_service', relationship_type: 'imports', source_file: 'app/api/routes.py', source_line: 12, confidence: 0.94, detection_method: 'static-import' },
    { edge_id: 'a3', source_node: 'app.services.user_service', target_node: 'app.repositories.user_repo', relationship_type: 'imports', source_file: 'app/services/user_service.py', source_line: 21, confidence: 0.92, detection_method: 'static-import' },
    { edge_id: 'a4', source_node: 'app.repositories.user_repo', target_node: 'app.models.user', relationship_type: 'imports', source_file: 'app/repositories/user_repo.py', source_line: 7, confidence: 0.9, detection_method: 'static-import' },
    { edge_id: 'a5', source_node: 'app.api.routes', target_node: 'app.auth', relationship_type: 'imports', source_file: 'app/api/routes.py', source_line: 33, confidence: 0.88, detection_method: 'static-import' },
  ];

  return {
    summary: {
      repository_id: repoName,
      node_count: 9,
      file_count: 23,
      dependency_count: baseEdges.length,
      cycle_count: 1,
      layer_count: 5,
      entrypoint_count: 2,
      analysis_version: 'architecture-v1',
    },
    nodes: [
      { node_id: 'root', name: 'repository', path: '.', node_type: 'root', language: 'repo' },
      { node_id: 'app.init', name: 'init', path: 'app/init.py', node_type: 'file', language: 'python' },
      { node_id: 'app.api.routes', name: 'routes', path: 'app/api/routes.py', node_type: 'file', language: 'python' },
      { node_id: 'app.auth', name: 'auth', path: 'app/auth.py', node_type: 'file', language: 'python' },
      { node_id: 'app.services.user_service', name: 'user_service', path: 'app/services/user_service.py', node_type: 'file', language: 'python' },
      { node_id: 'app.repositories.user_repo', name: 'user_repo', path: 'app/repositories/user_repo.py', node_type: 'file', language: 'python' },
      { node_id: 'app.models.user', name: 'user', path: 'app/models/user.py', node_type: 'file', language: 'python' },
      { node_id: 'app.api.events', name: 'events', path: 'app/api/events.py', node_type: 'file', language: 'python' },
      { node_id: 'app.config', name: 'config', path: 'app/config.py', node_type: 'file', language: 'python' },
    ],
    edges: baseEdges,
    cycles: [
      {
        cycle_id: 'cycle-1',
        participants: ['app.api.routes', 'app.services.user_service', 'app.repositories.user_repo'],
        chain: ['app.api.routes', 'app.services.user_service', 'app.repositories.user_repo', 'app.api.routes'],
        cycle_length: 3,
        severity: 'medium',
        remediation: 'Isolate the shared repository contract or move the dependency behind an interface layer.',
      },
    ],
    layers: [
      { file_path: 'app/api/routes.py', layer_name: 'API', confidence: 0.96, evidence: ['router naming', 'request entry handlers'] },
      { file_path: 'app/services/user_service.py', layer_name: 'Services', confidence: 0.93, evidence: ['service naming', 'domain orchestration'] },
      { file_path: 'app/repositories/user_repo.py', layer_name: 'Data Access', confidence: 0.89, evidence: ['repository pattern', 'persistent access'] },
      { file_path: 'app/models/user.py', layer_name: 'Models', confidence: 0.92, evidence: ['model naming', 'entity definition'] },
      { file_path: 'app/config.py', layer_name: 'Configuration', confidence: 0.8, evidence: ['config file naming'] },
    ],
    entrypoints: [
      { file_path: 'app/init.py', symbol_name: 'create_app', entry_type: 'application', detection_evidence: ['FastAPI application factory', 'startup bootstrap'] },
      { file_path: 'app/api/routes.py', symbol_name: 'router', entry_type: 'api', detection_evidence: ['router registration', 'route handlers'] },
    ],
    impact_analysis: {
      'app.services.user_service': {
        target: 'app.services.user_service',
        direct_dependents: ['app.api.routes'],
        transitive_dependents: ['app.init'],
        confidence: 0.82,
        risk_level: 'medium',
        evidence: ['route layer consumes this service', 'startup configuration wires route registration'],
      },
    },
  };
};

export const ArchitecturePage: React.FC = () => {
  const { repositories } = useAppStore();
  const [selectedRepoId, setSelectedRepoId] = useState(repositories[0]?.id ?? 'repo-1');
  const [data, setData] = useState<ArchitectureSnapshot | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;

    const loadArchitecture = async () => {
      setLoading(true);
      const repo = repositories.find((item) => item.id === selectedRepoId) ?? repositories[0];
      const fromApi = await apiService.getRepositoryArchitecture(selectedRepoId);
      if (!cancelled) {
        setData(fromApi ?? buildMockArchitecture(repo?.name ?? 'devpilot-core'));
        setLoading(false);
      }
    };

    loadArchitecture();
    return () => {
      cancelled = true;
    };
  }, [repositories, selectedRepoId]);

  const currentRepo = useMemo(
    () => repositories.find((repo) => repo.id === selectedRepoId) ?? repositories[0],
    [repositories, selectedRepoId]
  );

  const summaryCards = data
    ? [
        { label: 'Nodes', value: data.summary.node_count, accent: 'violet', icon: Network },
        { label: 'Dependencies', value: data.summary.dependency_count, accent: 'cyan', icon: ArrowRight },
        { label: 'Cycles', value: data.summary.cycle_count, accent: 'amber', icon: AlertTriangle },
        { label: 'Entrypoints', value: data.summary.entrypoint_count, accent: 'emerald', icon: Route },
      ]
    : [];

  const nodePositions = useMemo(() => {
    const width = 760;
    const height = 360;
    const nodes = data?.nodes ?? [];
    const active = nodes.filter((node) => node.node_type === 'file').slice(0, 8);
    return Object.fromEntries(
      active.map((node, index) => {
        const column = index % 4;
        const row = Math.floor(index / 4);
        return [
          node.node_id,
          {
            x: 80 + column * 170,
            y: 70 + row * 120 + (index % 2 === 0 ? 18 : 0),
            baseX: 80 + column * 170,
            baseY: 70 + row * 120 + (index % 2 === 0 ? 18 : 0),
          },
        ];
      })
    );
  }, [data]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col gap-4 border-b border-white/[0.06] pb-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Architecture Explorer</h1>
          <p className="mt-1 text-xs text-slate-400">
            Repository structure, dependency graph, cycle detection, layer classification, and impact analysis.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <label className="text-[11px] font-mono uppercase tracking-[0.18em] text-slate-400">Repository</label>
          <select
            value={selectedRepoId}
            onChange={(event) => setSelectedRepoId(event.target.value)}
            className="rounded-lg border border-white/10 bg-dark-900 px-3 py-2 text-sm text-slate-200 outline-none ring-0"
          >
            {repositories.map((repo) => (
              <option key={repo.id} value={repo.id}>
                {repo.name}
              </option>
            ))}
          </select>
          <Badge variant="violet">{loading ? 'Analyzing...' : 'Live graph'}</Badge>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {summaryCards.map((item) => {
          const Icon = item.icon;
          const isViolet = item.accent === 'violet';
          const isCyan = item.accent === 'cyan';
          const isAmber = item.accent === 'amber';
          const isEmerald = item.accent === 'emerald';

          return (
            <Card key={item.label} className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-[11px] font-mono uppercase tracking-[0.18em] text-slate-400">{item.label}</p>
                  <p className="mt-3 text-3xl font-bold text-white">{item.value}</p>
                </div>
                <div
                  className={`flex h-11 w-11 items-center justify-center rounded-xl border ${
                    isViolet ? 'border-brand-500/30 bg-brand-500/10 text-brand-200' :
                    isCyan ? 'border-cyan-500/30 bg-cyan-500/10 text-cyan-200' :
                    isAmber ? 'border-amber-500/30 bg-amber-500/10 text-amber-200' :
                    'border-emerald-500/30 bg-emerald-500/10 text-emerald-200'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.7fr_0.9fr]">
        <Card className="p-4">
          <div className="mb-3 flex items-center justify-between">
            <div>
              <h2 className="text-base font-semibold text-white">Dependency Map</h2>
              <p className="text-xs text-slate-400">Direct static relationships and import flow</p>
            </div>
            <Badge variant="success">{currentRepo?.name ?? 'Repository'}</Badge>
          </div>

          <div className="overflow-hidden rounded-xl border border-white/[0.06] bg-dark-950/50">
            <svg viewBox="0 0 760 360" className="h-[360px] w-full">
              {data?.edges?.map((edge, index) => {
                const from = nodePositions[edge.source_node];
                const to = nodePositions[edge.target_node];
                if (!from || !to) return null;
                return (
                  <g key={`${edge.edge_id}-${index}`}>
                    <line
                      x1={from.x}
                      y1={from.y}
                      x2={to.x}
                      y2={to.y}
                      stroke={edge.confidence >= 0.9 ? '#8b5cf6' : '#60a5fa'}
                      strokeWidth={edge.confidence >= 0.9 ? 2.5 : 1.5}
                      strokeOpacity={0.9}
                    />
                    <circle cx={(from.x + to.x) / 2} cy={(from.y + to.y) / 2} r={2.5} fill="#cbd5e1" />
                  </g>
                );
              })}

              {data?.nodes?.filter((node) => node.node_type === 'file').slice(0, 8).map((node) => {
                const position = nodePositions[node.node_id];
                if (!position) return null;
                return (
                  <g key={node.node_id}>
                    <circle
                      cx={position.x}
                      cy={position.y}
                      r={18}
                      fill={node.language === 'python' ? '#6d28d9' : '#0ea5e9'}
                      opacity={0.9}
                    />
                    <text x={position.x} y={position.y + 4} textAnchor="middle" fontSize="8" fill="#f8fafc" fontWeight={600}>
                      {node.name.slice(0, 6)}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>
        </Card>

        <div className="space-y-6">
          <Card className="p-4">
            <div className="mb-3 flex items-center gap-2">
              <Layers3 className="h-4 w-4 text-brand-300" />
              <h3 className="text-base font-semibold text-white">Layer Classification</h3>
            </div>
            <div className="space-y-3">
              {(data?.layers ?? []).slice(0, 5).map((layer) => (
                <div key={`${layer.file_path}-${layer.layer_name}`} className="rounded-lg border border-white/[0.05] bg-dark-900/60 p-3">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-sm font-medium text-slate-100">{layer.layer_name}</span>
                    <span className="text-[10px] font-mono text-brand-300">{Math.round(layer.confidence * 100)}%</span>
                  </div>
                  <p className="mt-2 text-[11px] text-slate-400">{layer.file_path}</p>
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-4">
            <div className="mb-3 flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-emerald-300" />
              <h3 className="text-base font-semibold text-white">Entry Points</h3>
            </div>
            <div className="space-y-3 text-sm text-slate-300">
              {(data?.entrypoints ?? []).map((entry) => (
                <div key={`${entry.file_path}-${entry.symbol_name ?? 'root'}`} className="rounded-lg border border-white/[0.05] bg-dark-900/60 p-3">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-medium text-white">{entry.symbol_name ?? 'main'}</span>
                    <Badge variant="success" size="sm">{entry.entry_type}</Badge>
                  </div>
                  <p className="mt-2 text-[11px] text-slate-400">{entry.file_path}</p>
                  <p className="mt-2 text-[11px] text-slate-300">{entry.detection_evidence[0]}</p>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card className="p-4">
          <div className="mb-3 flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-amber-300" />
            <h3 className="text-base font-semibold text-white">Cycle Detection</h3>
          </div>
          {(data?.cycles ?? []).length > 0 ? (
            <div className="space-y-3">
              {(data?.cycles ?? []).map((cycle) => (
                <div key={cycle.cycle_id} className="rounded-lg border border-amber-500/20 bg-amber-500/5 p-3">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-white">{cycle.cycle_id}</span>
                    <Badge variant="warning" size="sm">{cycle.severity}</Badge>
                  </div>
                  <p className="mt-2 text-[11px] text-slate-300">{cycle.chain.join(' → ')}</p>
                  <p className="mt-2 text-[11px] text-slate-400">{cycle.remediation}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-400">No cycles detected in the current static graph.</p>
          )}
        </Card>

        <Card className="p-4">
          <div className="mb-3 flex items-center gap-2">
            <Activity className="h-4 w-4 text-cyan-300" />
            <h3 className="text-base font-semibold text-white">Impact Analysis</h3>
          </div>
          {data && Object.keys(data.impact_analysis ?? {}).length > 0 ? (
            <div className="space-y-3">
              {Object.values(data.impact_analysis ?? {}).map((impact) => (
                <div key={impact.target} className="rounded-lg border border-white/[0.05] bg-dark-900/60 p-3">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-medium text-white">{impact.target}</span>
                    <Badge variant={impact.risk_level === 'high' ? 'warning' : 'success'} size="sm">{impact.risk_level}</Badge>
                  </div>
                  <p className="mt-2 text-[11px] text-slate-400">Direct dependents: {impact.direct_dependents.join(', ') || 'none'}</p>
                  <p className="mt-1 text-[11px] text-slate-400">Transitive dependents: {impact.transitive_dependents.join(', ') || 'none'}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-400">No direct impact relationships identified for the current repository snapshot.</p>
          )}
        </Card>
      </div>
    </div>
  );
};
