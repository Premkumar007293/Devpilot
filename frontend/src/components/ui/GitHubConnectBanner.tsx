import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Github,
  ArrowRight,
  Shield,
  CheckCircle2,
  X,
  Loader2,
  FolderGit2,
  ExternalLink,
  LogOut,
  AlertCircle,
} from 'lucide-react';
import { Button } from '../common/Button';
import {
  openGitHubConnectFlow,
  apiService,
  GitHubStatus,
} from '../../services/api';

export const GitHubConnectBanner: React.FC = () => {
  const navigate = useNavigate();
  const [showModal, setShowModal] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [statusLoading, setStatusLoading] = useState(true);
  const [githubStatus, setGithubStatus] = useState<GitHubStatus>({
    connected: false,
    user: null,
    repository_count: 0,
  });

  const loadStatus = async () => {
    try {
      setStatusLoading(true);
      const status = await apiService.getGitHubStatus();
      setGithubStatus(status);
    } catch {
      setGithubStatus({ connected: false, user: null, repository_count: 0 });
    } finally {
      setStatusLoading(false);
    }
  };

  useEffect(() => {
    loadStatus();
  }, []);

  const handleContinue = async () => {
    setIsConnecting(true);
    setErrorMessage(null);
    try {
      await openGitHubConnectFlow();
      // Browser navigation will occur inside openGitHubConnectFlow
    } catch (err: unknown) {
      setIsConnecting(false);
      const msg = err instanceof Error ? err.message : 'GitHub connection could not be started.';
      setErrorMessage(msg);
    }
  };

  const handleDisconnect = async () => {
    if (!window.confirm('Disconnect your GitHub account from DevPilot?')) return;
    try {
      await apiService.disconnectGitHub();
      await loadStatus();
    } catch {
      window.alert('Failed to disconnect GitHub account.');
    }
  };

  // If already connected, show the real connected status card
  if (!statusLoading && githubStatus.connected && githubStatus.user) {
    return (
      <div className="relative overflow-hidden rounded-xl border border-emerald-500/30 bg-gradient-to-r from-dark-850 via-dark-800 to-dark-850 p-6 shadow-glow-sm">
        <div className="absolute top-0 inset-x-0 h-[2px] bg-gradient-to-r from-transparent via-emerald-400 to-transparent" />

        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-5">
          <div className="flex items-center gap-4">
            <div className="relative shrink-0">
              {githubStatus.user.avatar_url ? (
                <img
                  src={githubStatus.user.avatar_url}
                  alt={githubStatus.user.login}
                  className="w-12 h-12 rounded-xl border border-emerald-500/40 object-cover shadow-glow-sm"
                />
              ) : (
                <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-dark-900 border border-emerald-500/30 text-emerald-400 shadow-glow-sm">
                  <Github className="w-6 h-6" />
                </div>
              )}
              <span className="absolute -bottom-1 -right-1 flex h-3.5 w-3.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-emerald-500 border-2 border-dark-900" />
              </span>
            </div>

            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <h3 className="text-base font-semibold text-white tracking-tight">
                  {githubStatus.user.name || githubStatus.user.login}
                </h3>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                  GitHub Connected
                </span>
              </div>
              <p className="text-xs text-slate-400 flex items-center gap-3">
                <a
                  href={githubStatus.user.html_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-emerald-300 transition-colors flex items-center gap-1 font-mono"
                >
                  @{githubStatus.user.login}
                  <ExternalLink className="w-3 h-3 text-slate-500" />
                </a>
                <span>•</span>
                <span className="flex items-center gap-1">
                  <FolderGit2 className="w-3.5 h-3.5 text-slate-400" />
                  {githubStatus.repository_count} accessible repositories
                </span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 shrink-0 w-full md:w-auto">
            <Button
              variant="secondary"
              size="sm"
              icon={<LogOut className="w-3.5 h-3.5" />}
              onClick={handleDisconnect}
              className="text-slate-400 hover:text-rose-400 border-white/[0.08]"
            >
              Disconnect
            </Button>
            <Button
              variant="primary"
              size="md"
              icon={<FolderGit2 className="w-4 h-4" />}
              onClick={() => navigate('/repositories')}
              className="w-full md:w-auto"
            >
              View Repositories
              <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="relative overflow-hidden rounded-xl border border-brand-500/30 bg-gradient-to-r from-dark-850 via-dark-800 to-dark-850 p-6 shadow-glow-sm">
        <div className="absolute top-0 inset-x-0 h-[2px] bg-gradient-to-r from-transparent via-brand-accent to-transparent" />

        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-5">
          <div className="flex items-start gap-4">
            <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-dark-900 border border-brand-500/30 text-white shadow-glow-sm shrink-0">
              <Github className="w-6 h-6 text-brand-300" />
            </div>

            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <h3 className="text-base font-semibold text-white tracking-tight">
                  Connect GitHub Repositories
                </h3>
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-brand-500/15 text-brand-300 border border-brand-500/25">
                  Secure OAuth
                </span>
              </div>
              <p className="text-xs text-slate-400 max-w-2xl leading-relaxed">
                Connect your GitHub account to browse repositories, import selected repositories, and power DevPilot code intelligence with repository-aware analysis.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 shrink-0 w-full md:w-auto">
            <Button
              variant="primary"
              size="md"
              icon={<Github className="w-4 h-4" />}
              onClick={() => {
                setErrorMessage(null);
                setShowModal(true);
              }}
              className="w-full md:w-auto"
            >
              Connect with GitHub
              <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in">
          <div className="w-full max-w-md rounded-xl bg-dark-900 border border-white/[0.1] p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-brand-300">
                <Github className="w-5 h-5" />
                <span className="font-semibold text-white text-sm">Authorize GitHub</span>
              </div>
              <button
                disabled={isConnecting}
                onClick={() => setShowModal(false)}
                className="text-slate-400 hover:text-white p-1 rounded-md transition-colors disabled:opacity-50"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              We will request access to your public profile and repository metadata needed to browse, select, and analyze repositories connected to DevPilot.
            </p>

            <div className="space-y-2 p-3 rounded-lg bg-dark-850 border border-white/[0.06] text-xs">
              <div className="flex items-center gap-2 text-slate-300">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Read your public GitHub profile</span>
              </div>
              <div className="flex items-center gap-2 text-slate-300">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>List repositories available to your account</span>
              </div>
              <div className="flex items-center gap-2 text-slate-400">
                <Shield className="w-4 h-4 text-brand-400 shrink-0" />
                <span>Private access respects the permissions you grant</span>
              </div>
            </div>

            {errorMessage && (
              <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 flex items-start gap-2.5 text-xs text-rose-300">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" />
                <div className="space-y-1">
                  <p className="font-medium">Connection Error</p>
                  <p className="text-rose-300/90 leading-relaxed">{errorMessage}</p>
                </div>
              </div>
            )}

            <div className="flex gap-3 pt-1">
              <Button
                variant="secondary"
                size="md"
                className="flex-1"
                disabled={isConnecting}
                onClick={() => setShowModal(false)}
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                size="md"
                className="flex-1"
                disabled={isConnecting}
                onClick={handleContinue}
                icon={isConnecting ? <Loader2 className="w-4 h-4 animate-spin" /> : undefined}
              >
                {isConnecting ? 'Redirecting to GitHub...' : 'Continue'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
