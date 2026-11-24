import React, { useState } from 'react';
import { Database, Server, Send } from 'lucide-react';
import { Card } from '../components/common/Card';
import { useAppStore } from '../store/useAppStore';
import { StatusIndicator } from '../components/common/StatusIndicator';
import { apiService } from '../services/api';

export const SettingsPage: React.FC = () => {
  const { backendHealth } = useAppStore();
  const [category, setCategory] = useState('bug');
  const [description, setDescription] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [feedbackError, setFeedbackError] = useState('');

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!description.trim()) {
      setFeedbackError('Please describe the issue or suggestion before submitting feedback.');
      return;
    }

    const result = await apiService.submitFeedback({
      category,
      description: description.trim(),
      related_resource_type: 'settings',
      related_resource_id: 'beta-feedback',
    });

    if (!result) {
      setFeedbackError('Feedback could not be submitted. Please sign in and try again.');
      return;
    }

    setSubmitted(true);
    setDescription('');
    setFeedbackError('');
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between pb-2 border-b border-white/[0.06]">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Platform Settings</h1>
          <p className="text-xs text-slate-400 mt-1">
            Environment configuration, API endpoints, database status, and AI provider credentials.
          </p>
        </div>
        <StatusIndicator status={backendHealth.status} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <Card className="p-5 space-y-4">
          <div className="flex items-center gap-2 text-brand-300">
            <Server className="w-5 h-5" />
            <h3 className="text-sm font-semibold text-white">Backend Infrastructure</h3>
          </div>

          <div className="space-y-2 text-xs font-mono">
            <div className="flex justify-between p-2.5 rounded bg-dark-800 border border-white/[0.04]">
              <span className="text-slate-400">Application</span>
              <span className="text-white font-semibold">{backendHealth.application}</span>
            </div>
            <div className="flex justify-between p-2.5 rounded bg-dark-800 border border-white/[0.04]">
              <span className="text-slate-400">Version</span>
              <span className="text-white font-semibold">v{backendHealth.version}</span>
            </div>
            <div className="flex justify-between p-2.5 rounded bg-dark-800 border border-white/[0.04]">
              <span className="text-slate-400">Health Endpoint</span>
              <span className="text-brand-300">/api/v1/health</span>
            </div>
          </div>
        </Card>

        <Card className="p-5 space-y-4">
          <div className="flex items-center gap-2 text-emerald-300">
            <Database className="w-5 h-5" />
            <h3 className="text-sm font-semibold text-white">Persistence & Caching</h3>
          </div>

          <div className="space-y-2 text-xs font-mono">
            <div className="flex justify-between p-2.5 rounded bg-dark-800 border border-white/[0.04]">
              <span className="text-slate-400">Database Engine</span>
              <span className="text-white">SQLite default / PostgreSQL ready</span>
            </div>
            <div className="flex justify-between p-2.5 rounded bg-dark-800 border border-white/[0.04]">
              <span className="text-slate-400">Cache & Queue</span>
              <span className="text-white">Redis optional</span>
            </div>
            <div className="flex justify-between p-2.5 rounded bg-dark-800 border border-white/[0.04]">
              <span className="text-slate-400">Schema Migrations</span>
              <span className="text-white">Alembic Configured</span>
            </div>
          </div>
        </Card>
      </div>

      <Card className="p-5">
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-white">Beta feedback</h3>
          <p className="text-sm text-slate-400 mt-1">
            Share bugs, feature requests, or analysis-quality issues during the controlled beta.
          </p>
        </div>

        <form className="space-y-4" onSubmit={handleSubmit}>
          <div>
            <label className="mb-2 block text-xs uppercase tracking-[0.15em] text-slate-400">Category</label>
            <select
              value={category}
              onChange={(event) => setCategory(event.target.value)}
              className="w-full rounded-lg border border-white/10 bg-dark-900 px-3 py-2 text-sm text-white outline-none focus:border-brand-500"
            >
              <option value="bug">Bug report</option>
              <option value="feature_request">Feature request</option>
              <option value="usability">Usability feedback</option>
              <option value="analysis_quality">Analysis quality</option>
              <option value="general">General feedback</option>
            </select>
          </div>

          <div>
            <label className="mb-2 block text-xs uppercase tracking-[0.15em] text-slate-400">Description</label>
            <textarea
              rows={5}
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              placeholder="Describe the issue, what you expected, and any repository or resource involved."
              className="w-full rounded-lg border border-white/10 bg-dark-900 px-3 py-2 text-sm text-white outline-none focus:border-brand-500 resize-none"
            />
          </div>

          {feedbackError && <p className="text-sm text-rose-300">{feedbackError}</p>}
          {submitted && !feedbackError && (
            <p className="text-sm text-emerald-300">Feedback submitted. Thank you for helping improve DevPilot.</p>
          )}

          <button
            type="submit"
            className="inline-flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-400"
          >
            <Send className="w-4 h-4" />
            Submit feedback
          </button>
        </form>
      </Card>
    </div>
  );
};
