import React from 'react';
import { Sparkles, MessageSquareCode, Zap } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';

export const AIAssistantPage: React.FC = () => {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between pb-2 border-b border-white/[0.06]">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">AI-Powered Repository Assistant</h1>
          <p className="text-xs text-slate-400 mt-1">
            Context-aware AI conversational partner with direct understanding of your codebase, AST graph, and Git history.
          </p>
        </div>
        <Badge variant="violet">Phase 2 Preview</Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <Card className="p-5 space-y-3">
          <div className="flex items-center gap-2 text-brand-300">
            <Sparkles className="w-5 h-5" />
            <h3 className="font-semibold text-sm text-white">Provider Agnostic</h3>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Seamlessly switch between Google Gemini Pro 1.5, OpenAI GPT-4o, and local models through unified interfaces in <code className="text-brand-300">app.engines.ai</code>.
          </p>
        </Card>

        <Card className="p-5 space-y-3">
          <div className="flex items-center gap-2 text-cyan-300">
            <MessageSquareCode className="w-5 h-5" />
            <h3 className="font-semibold text-sm text-white">Code Intelligence Context</h3>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Prompts are enriched with localized file references, symbol definitions, call hierarchies, and recent pull request diffs.
          </p>
        </Card>

        <Card className="p-5 space-y-3">
          <div className="flex items-center gap-2 text-emerald-300">
            <Zap className="w-5 h-5" />
            <h3 className="font-semibold text-sm text-white">Automated Refactoring</h3>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Generates verifiable patch diffs that address security alerts, optimize complexity, and modernize legacy patterns.
          </p>
        </Card>
      </div>
    </div>
  );
};
