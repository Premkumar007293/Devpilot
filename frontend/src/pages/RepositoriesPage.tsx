import React, { useEffect, useState } from 'react';
import {
  GitBranch,
  Plus,
  Github,
  Star,
  Lock,
  Globe,
  ExternalLink,
  CheckCircle2,
  Loader2,
  RefreshCw,
  Search,
  X,
  AlertCircle,
} from 'lucide-react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { useAppStore } from '../store/useAppStore';
import {
  openGitHubConnectFlow,
  apiService,
  GitHubStatus,
  ConnectedRepository,
  GitHubAccessibleRepo,
} from '../services/api';

export const RepositoriesPage: React.FC = () => {
  const { repositories: sampleRepositories } = useAppStore();

  const [githubStatus, setGithubStatus] = useState<GitHubStatus>({
    connected: false,
    user: null,
    repository_count: 0,
  });
  const [connectedRepos, setConnectedRepos] = useState<ConnectedRepository[]>([]);
  const [accessibleRepos, setAccessibleRepos] = useState<GitHubAccessibleRepo[]>([]);
  const [loading, setLoading] = useState(true);
  const [showImportModal, setShowImportModal] = useState(false);
  const [importLoading, setImportLoading] = useState(false);
  const [connectingRepoId, setConnectingRepoId] = useState<number | null>(null);
  const [modalSearch, setModalSearch] = useState('');
  const [importError, setImportError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const status = await apiService.getGitHubStatus();
      setGithubStatus(status);

      if (status.connected) {
        const connected = await apiService.getConnectedRepositories();
        setConnectedRepos(connected);
      }
    } catch {
      // Graceful fallback to unauthenticated state
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleOpenImportModal = async () => {
    setShowImportModal(true);
    setImportError(null);
    setImportLoading(true);
    try {
      const repos = await apiService.getAccessibleGitHubRepositories();
      setAccessibleRepos(repos);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load accessible repositories from GitHub.';
      setImportError(msg);
    } finally {
      setImportLoading(false);
    }
  };

  const handleConnectRepo = async (repo: GitHubAccessibleRepo) => {
    setConnectingRepoId(repo.id);
    setImportError(null);
    try {
      await apiService.connectRepository(repo.id);
      // Refresh connected list
      const connected = await apiService.getConnectedRepositories();
      setConnectedRepos(connected);
      // Mark as connected in accessible list
      setAccessibleRepos((prev) =>
        prev.map((r) => (r.id === repo.id ? { ...r, is_connected: true } : r))
      );
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to connect repository.';
      setImportError(msg);
    } finally {
      setConnectingRepoId(null);
    }
  };

  const handleConnectGitHub = async () => {
    try {
      await openGitHubConnectFlow();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'GitHub connection could not be started.';
      window.alert(msg);
    }
  };

  const filteredAccessibleRepos = accessibleRepos.filter((repo) =>
    repo.full_name.toLowerCase().includes(modalSearch.toLowerCase()) ||
    (repo.description && repo.description.toLowerCase().includes(modalSearch.toLowerCase()))
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-white/[0.06]">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Repositories</h1>
          <p className="text-xs text-slate-400 mt-1">
            Connected repositories indexed for AI assistance, static scans, and vulnerability detection.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {githubStatus.connected ? (
            <Button
              variant="primary"
              size="md"
              icon={<Plus className="w-4 h-4" />}
              onClick={handleOpenImportModal}
            >
              Add Repository
            </Button>
          ) : (
            <Button
              variant="primary"
              size="md"
              icon={<Github className="w-4 h-4" />}
              onClick={handleConnectGitHub}
            >
              Connect GitHub
            </Button>
          )}
        </div>
      </div>

      {/* GitHub Connected Profile Banner */}
      {githubStatus.connected && githubStatus.user && (
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-xl bg-dark-850 border border-white/[0.08]">
          <div className="flex items-center gap-3">
            {githubStatus.user.avatar_url ? (
              <img
                src={githubStatus.user.avatar_url}
                alt={githubStatus.user.login}
                className="w-10 h-10 rounded-lg border border-emerald-500/40 object-cover"
              />
            ) : (
              <div className="w-10 h-10 rounded-lg bg-dark-900 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                <Github className="w-5 h-5" />
              </div>
            )}
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-white">
                  {githubStatus.user.name || githubStatus.user.login}
                </span>
                <span className="text-xs font-mono text-slate-400">
                  (@{githubStatus.user.login})
                </span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3 text-emerald-400" /> Connected
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                {connectedRepos.length} repository connected • {githubStatus.repository_count} accessible on GitHub
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="secondary"
              size="sm"
              icon={<RefreshCw className="w-3.5 h-3.5" />}
              onClick={loadData}
            >
              Refresh
            </Button>
            <Button
              variant="primary"
              size="sm"
              icon={<Plus className="w-3.5 h-3.5" />}
              onClick={handleOpenImportModal}
            >
              Import Repository
            </Button>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-12 text-slate-400 gap-2">
          <Loader2 className="w-5 h-5 animate-spin text-brand-400" />
          <span className="text-xs font-mono">Loading repositories...</span>
        </div>
      )}

      {/* Real Connected Repositories Grid */}
      {!loading && connectedRepos.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-white tracking-tight">
              Active Connected Repositories ({connectedRepos.length})
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {connectedRepos.map((repo) => (
              <Card key={repo.id} glow className="p-5 space-y-4">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <h3 className="text-sm font-semibold text-white">{repo.name}</h3>
                      <Badge variant={repo.is_active ? 'success' : 'default'} size="sm">
                        {repo.is_active ? 'ACTIVE' : 'INACTIVE'}
                      </Badge>
                      {repo.is_private ? (
                        <span className="flex items-center gap-1 text-[10px] text-slate-400 font-mono">
                          <Lock className="w-3 h-3" /> Private
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-[10px] text-slate-400 font-mono">
                          <Globe className="w-3 h-3" /> Public
                        </span>
                      )}
                    </div>
                    <p className="text-xs font-mono text-slate-400">{repo.full_name}</p>
                  </div>
                  {repo.html_url && (
                    <a
                      href={repo.html_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-slate-400 hover:text-white transition-colors p-1"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                </div>

                <p className="text-xs text-slate-300 leading-relaxed min-h-[32px]">
                  {repo.description || 'No description provided.'}
                </p>

                <div className="flex items-center justify-between pt-3 border-t border-white/[0.06] text-xs font-mono text-slate-400">
                  <div className="flex items-center gap-3">
                    {repo.language && (
                      <span className="flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-brand-400" />
                        {repo.language}
                      </span>
                    )}
                    <span className="flex items-center gap-1 text-slate-400">
                      <GitBranch className="w-3.5 h-3.5" />
                      {repo.default_branch}
                    </span>
                    {(repo.stars_count ?? 0) > 0 && (
                      <span className="flex items-center gap-1 text-amber-400">
                        <Star className="w-3 h-3 fill-amber-400" />
                        {repo.stars_count}
                      </span>
                    )}
                  </div>
                  <span>
                    {repo.last_scanned_at
                      ? `Scanned ${new Date(repo.last_scanned_at).toLocaleDateString()}`
                      : 'Pending initial scan'}
                  </span>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* If connected but no repos imported yet */}
      {!loading && githubStatus.connected && connectedRepos.length === 0 && (
        <Card className="p-8 text-center space-y-4 border-dashed border-white/[0.15]">
          <div className="w-12 h-12 rounded-xl bg-dark-850 border border-white/[0.1] flex items-center justify-center mx-auto text-brand-300">
            <Github className="w-6 h-6" />
          </div>
          <div className="space-y-1">
            <h3 className="text-base font-semibold text-white">No Repositories Connected Yet</h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              Your GitHub account is connected. Select which repositories you would like DevPilot to index for code analysis and intelligence.
            </p>
          </div>
          <Button
            variant="primary"
            size="md"
            icon={<Plus className="w-4 h-4" />}
            onClick={handleOpenImportModal}
          >
            Import from GitHub ({githubStatus.repository_count} Available)
          </Button>
        </Card>
      )}

      {/* Fallback / Sample Repositories (Visible when not connected) */}
      {!loading && !githubStatus.connected && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-semibold text-white tracking-tight">
                Preview Repositories
              </h2>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-brand-500/10 text-brand-300 border border-brand-500/20">
                Phase 1 Demo Workspace
              </span>
            </div>
            <span className="text-xs text-slate-400">Connect GitHub to load your live repositories</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {sampleRepositories.map((repo) => (
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
      )}

      {/* Accessible Repositories Import Modal */}
      {showImportModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in">
          <div className="w-full max-w-2xl rounded-xl bg-dark-900 border border-white/[0.1] shadow-2xl flex flex-col max-h-[85vh]">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-5 border-b border-white/[0.08]">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-dark-850 border border-white/[0.1] flex items-center justify-center text-brand-300">
                  <Github className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-white">Import GitHub Repositories</h3>
                  <p className="text-xs text-slate-400">
                    Select repositories accessible to @{githubStatus.user?.login}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowImportModal(false)}
                className="text-slate-400 hover:text-white p-1 rounded-md"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Search Input */}
            <div className="p-4 border-b border-white/[0.06] bg-dark-850/50">
              <div className="relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Filter repositories..."
                  value={modalSearch}
                  onChange={(e) => setModalSearch(e.target.value)}
                  className="w-full pl-9 pr-4 py-2 text-xs bg-dark-900 border border-white/[0.08] rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-brand-500/50"
                />
              </div>
            </div>

            {/* Error Message */}
            {importError && (
              <div className="mx-4 mt-3 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 flex items-center gap-2 text-xs text-rose-300">
                <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
                <span>{importError}</span>
              </div>
            )}

            {/* Repositories List */}
            <div className="overflow-y-auto p-4 space-y-2 flex-1">
              {importLoading ? (
                <div className="py-12 flex flex-col items-center justify-center text-slate-400 gap-2">
                  <Loader2 className="w-6 h-6 animate-spin text-brand-400" />
                  <span className="text-xs font-mono">Fetching accessible repositories from GitHub...</span>
                </div>
              ) : filteredAccessibleRepos.length === 0 ? (
                <div className="py-12 text-center text-xs text-slate-400">
                  No repositories matched your filter.
                </div>
              ) : (
                filteredAccessibleRepos.map((repo) => (
                  <div
                    key={repo.id}
                    className="flex items-center justify-between p-3.5 rounded-lg bg-dark-850 border border-white/[0.06] hover:border-white/[0.12] transition-colors"
                  >
                    <div className="space-y-1 pr-4 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-semibold text-white truncate">
                          {repo.full_name}
                        </span>
                        {repo.private ? (
                          <span className="flex items-center gap-1 text-[10px] text-slate-400 font-mono">
                            <Lock className="w-3 h-3" /> Private
                          </span>
                        ) : (
                          <span className="flex items-center gap-1 text-[10px] text-slate-400 font-mono">
                            <Globe className="w-3 h-3" /> Public
                          </span>
                        )}
                      </div>
                      {repo.description && (
                        <p className="text-[11px] text-slate-400 line-clamp-1">
                          {repo.description}
                        </p>
                      )}
                      <div className="flex items-center gap-3 text-[10px] font-mono text-slate-400 pt-0.5">
                        {repo.language && (
                          <span className="flex items-center gap-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-brand-400" />
                            {repo.language}
                          </span>
                        )}
                        <span className="flex items-center gap-1">
                          <GitBranch className="w-3 h-3" />
                          {repo.default_branch}
                        </span>
                        {repo.stargazers_count > 0 && (
                          <span className="flex items-center gap-1 text-amber-400">
                            <Star className="w-2.5 h-2.5 fill-amber-400" />
                            {repo.stargazers_count}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="shrink-0">
                      {repo.is_connected ? (
                        <span className="text-xs font-mono text-emerald-400 flex items-center gap-1 px-2.5 py-1 rounded bg-emerald-500/10 border border-emerald-500/20">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          Connected
                        </span>
                      ) : (
                        <Button
                          variant="secondary"
                          size="sm"
                          disabled={connectingRepoId === repo.id}
                          onClick={() => handleConnectRepo(repo)}
                          icon={connectingRepoId === repo.id ? <Loader2 className="w-3 h-3 animate-spin" /> : undefined}
                        >
                          {connectingRepoId === repo.id ? 'Connecting...' : 'Connect'}
                        </Button>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-white/[0.08] flex justify-end">
              <Button variant="secondary" size="md" onClick={() => setShowImportModal(false)}>
                Done
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
