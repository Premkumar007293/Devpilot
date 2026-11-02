import React, { useState } from 'react';
import { Search, X, GitBranch, ArrowRight } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';
import { useKeyboardShortcut } from '../../hooks/useKeyboardShortcut';

export const SearchModal: React.FC = () => {
  const { searchModalOpen, setSearchModalOpen, repositories } = useAppStore();
  const [query, setQuery] = useState('');

  // Register Ctrl+K and Escape
  useKeyboardShortcut('k', () => setSearchModalOpen(true), { ctrlOrMeta: true });
  useKeyboardShortcut('Escape', () => setSearchModalOpen(false));

  if (!searchModalOpen) return null;

  const filteredRepos = repositories.filter((r) =>
    r.name.toLowerCase().includes(query.toLowerCase()) ||
    r.language.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 px-4 bg-black/80 backdrop-blur-md animate-in fade-in">
      <div className="w-full max-w-2xl rounded-xl bg-dark-900 border border-white/[0.12] shadow-2xl overflow-hidden">
        {/* Search Input Bar */}
        <div className="flex items-center gap-3 px-4 py-3.5 border-b border-white/[0.08]">
          <Search className="w-5 h-5 text-slate-400 shrink-0" />
          <input
            type="text"
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search repositories, AST nodes, security alerts, documentation..."
            className="flex-1 bg-transparent text-sm text-white placeholder-slate-400 focus:outline-none"
          />
          <button
            onClick={() => setSearchModalOpen(false)}
            className="p-1 rounded text-slate-400 hover:text-white hover:bg-white/[0.06]"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Results */}
        <div className="max-h-96 overflow-y-auto p-3 space-y-2 text-xs">
          <div className="px-3 py-1 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            Repositories ({filteredRepos.length})
          </div>
          {filteredRepos.map((repo) => (
            <div
              key={repo.id}
              onClick={() => setSearchModalOpen(false)}
              className="flex items-center justify-between p-2.5 rounded-lg hover:bg-white/[0.05] cursor-pointer transition-colors group"
            >
              <div className="flex items-center gap-3">
                <div className="p-1.5 rounded bg-dark-800 text-slate-300">
                  <GitBranch className="w-4 h-4" />
                </div>
                <div>
                  <div className="font-semibold text-slate-200 group-hover:text-brand-300 transition-colors">
                    {repo.name}
                  </div>
                  <div className="text-[11px] text-slate-400">{repo.fullName}</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-slate-400">{repo.language}</span>
                <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-white transition-colors" />
              </div>
            </div>
          ))}

          {/* Quick Shortcuts */}
          <div className="pt-2 border-t border-white/[0.06] flex items-center justify-between text-[11px] text-slate-400 px-3">
            <span>Navigation: <kbd className="px-1.5 py-0.5 rounded bg-dark-800 border border-white/10">↑</kbd> <kbd className="px-1.5 py-0.5 rounded bg-dark-800 border border-white/10">↓</kbd></span>
            <span>Close: <kbd className="px-1.5 py-0.5 rounded bg-dark-800 border border-white/10">Esc</kbd></span>
          </div>
        </div>
      </div>
    </div>
  );
};
