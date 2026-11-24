import React from 'react';
import { ArrowRight, CheckCircle2, Github, GitBranch, Sparkles, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Card, CardContent } from '../components/common/Card';

const steps = [
  {
    title: 'Welcome',
    description: 'DevPilot helps you understand GitHub repositories, analyze code quality, detect risks, and ask grounded questions about your codebase.',
    icon: Sparkles,
  },
  {
    title: 'Connect GitHub',
    description: 'Connect your GitHub account and approve only the repository access you need. We never request unnecessary permissions.',
    icon: Github,
  },
  {
    title: 'Select a repository',
    description: 'Browse your available repositories, choose one to connect, and review metadata before ingestion begins.',
    icon: GitBranch,
  },
  {
    title: 'Run initial analysis',
    description: 'Ingest the repository, scan code, run security checks, inspect architecture, and enable AI indexing when configured.',
    icon: ShieldCheck,
  },
];

export const OnboardingPage: React.FC = () => {
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="rounded-2xl border border-brand-500/20 bg-gradient-to-r from-brand-600/10 via-dark-900 to-dark-850 p-6">
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-brand-300">Welcome to the beta</p>
            <h1 className="mt-2 text-3xl font-bold text-white">Set up DevPilot in a few minutes</h1>
          </div>
          <Link
            to="/repositories"
            className="inline-flex items-center gap-2 rounded-lg border border-brand-500/30 bg-brand-500/10 px-4 py-2 text-sm font-medium text-brand-200 hover:bg-brand-500/15"
          >
            Skip onboarding
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {steps.map((step, index) => {
          const Icon = step.icon;
          return (
            <Card key={step.title} className="p-4 h-full">
              <CardContent className="p-0 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-500/10 text-brand-300">
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="text-[11px] font-mono text-slate-400">0{index + 1}</span>
                </div>
                <div>
                  <h2 className="text-base font-semibold text-white">{step.title}</h2>
                  <p className="mt-2 text-sm leading-6 text-slate-300">{step.description}</p>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Card className="p-6">
        <div className="flex items-start gap-3">
          <div className="mt-0.5 rounded-full bg-emerald-500/15 p-1 text-emerald-300">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">What you can do next</h2>
            <p className="mt-2 text-sm text-slate-300">
              Connect GitHub, select a repository, and start the initial analysis cycle. DevPilot then surfaces code quality findings, architecture insight, security observations, and repository-grounded AI answers in a single workspace.
            </p>
            <div className="mt-4 flex flex-wrap gap-3">
              <Link
                to="/repositories"
                className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-400"
              >
                Open repositories
              </Link>
              <Link
                to="/settings"
                className="rounded-lg border border-white/10 bg-dark-800 px-4 py-2 text-sm font-medium text-slate-200 hover:border-brand-500/40 hover:text-white"
              >
                View settings
              </Link>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};
