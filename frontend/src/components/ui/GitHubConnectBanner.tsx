import React, { useState } from 'react';
import { Github, ArrowRight, Shield, CheckCircle2, X } from 'lucide-react';
import { Button } from '../common/Button';

export const GitHubConnectBanner: React.FC = () => {
  const [showModal, setShowModal] = useState(false);

  return (
    <>
      <div className="relative overflow-hidden rounded-xl border border-brand-500/30 bg-gradient-to-r from-dark-850 via-dark-800 to-dark-850 p-6 shadow-glow-sm">
        {/* Subtle accent line */}
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
                  Phase 2 Integration
                </span>
              </div>
              <p className="text-xs text-slate-400 max-w-2xl leading-relaxed">
                Unlock automated repository sync, continuous static analysis, automated vulnerability detection, and interactive architecture dependency graphs powered by DevPilot AI.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 shrink-0 w-full md:w-auto">
            <Button
              variant="primary"
              size="md"
              icon={<Github className="w-4 h-4" />}
              onClick={() => setShowModal(true)}
              className="w-full md:w-auto"
            >
              Connect with GitHub
              <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
        </div>
      </div>

      {/* Preview Modal explaining Phase 1 status */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in">
          <div className="w-full max-w-md rounded-xl bg-dark-900 border border-white/[0.1] p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-brand-300">
                <Github className="w-5 h-5" />
                <span className="font-semibold text-white text-sm">GitHub OAuth Integration</span>
              </div>
              <button
                onClick={() => setShowModal(false)}
                className="text-slate-400 hover:text-white p-1 rounded-md"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              DevPilot Phase 1 establishes the full-stack architectural foundation. The GitHub OAuth client and webhooks integration will be connected in Phase 2.
            </p>

            <div className="space-y-2 p-3 rounded-lg bg-dark-850 border border-white/[0.06] text-xs">
              <div className="flex items-center gap-2 text-slate-300">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Backend GitHub Client Interface configured</span>
              </div>
              <div className="flex items-center gap-2 text-slate-300">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>OAuth callback redirect paths reserved</span>
              </div>
              <div className="flex items-center gap-2 text-slate-400">
                <Shield className="w-4 h-4 text-brand-400 shrink-0" />
                <span>Live token synchronization: Ready for Phase 2</span>
              </div>
            </div>

            <Button variant="secondary" size="md" className="w-full" onClick={() => setShowModal(false)}>
              Understood
            </Button>
          </div>
        </div>
      )}
    </>
  );
};
