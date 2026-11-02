import React from 'react';
import { TrendingUp, TrendingDown, Minus, LucideIcon } from 'lucide-react';
import { Card, CardContent } from '../common/Card';
import { cn } from '../../utils/cn';

interface MetricCardProps {
  label: string;
  value: string | number;
  change: string;
  changeType: 'positive' | 'negative' | 'neutral';
  description: string;
  icon: LucideIcon;
  accentColor?: 'violet' | 'cyan' | 'emerald' | 'amber' | 'rose';
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  change,
  changeType,
  description,
  icon: Icon,
  accentColor = 'violet',
}) => {
  const accentGradients = {
    violet: 'from-brand-600/20 via-brand-accent/10 to-transparent border-brand-500/30 text-brand-300',
    cyan: 'from-cyan-600/20 via-cyan-500/10 to-transparent border-cyan-500/30 text-cyan-300',
    emerald: 'from-emerald-600/20 via-emerald-500/10 to-transparent border-emerald-500/30 text-emerald-300',
    amber: 'from-amber-600/20 via-amber-500/10 to-transparent border-amber-500/30 text-amber-300',
    rose: 'from-rose-600/20 via-rose-500/10 to-transparent border-rose-500/30 text-rose-300',
  };

  const changeStyles = {
    positive: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
    negative: 'text-rose-400 bg-rose-500/10 border-rose-500/20',
    neutral: 'text-slate-400 bg-dark-800 border-white/10',
  };

  const ChangeIcon =
    changeType === 'positive'
      ? TrendingUp
      : changeType === 'negative'
      ? TrendingDown
      : Minus;

  return (
    <Card glow className="relative overflow-hidden group">
      {/* Top subtle highlight gradient */}
      <div className="absolute top-0 inset-x-0 h-[1px] bg-gradient-to-r from-transparent via-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">{label}</span>
          <div
            className={cn(
              'flex items-center justify-center w-8 h-8 rounded-lg border bg-gradient-to-br transition-all group-hover:scale-110 shrink-0',
              accentGradients[accentColor]
            )}
          >
            <Icon className="w-4 h-4" />
          </div>
        </div>

        <div className="mt-3 flex items-baseline gap-2">
          <span className="text-2xl font-bold tracking-tight text-white font-mono">{value}</span>
          <span
            className={cn(
              'inline-flex items-center gap-1 text-[11px] font-mono font-medium px-1.5 py-0.5 rounded border',
              changeStyles[changeType]
            )}
          >
            <ChangeIcon className="w-3 h-3" />
            {change}
          </span>
        </div>

        <p className="mt-2 text-xs text-slate-400 truncate">{description}</p>
      </CardContent>
    </Card>
  );
};
