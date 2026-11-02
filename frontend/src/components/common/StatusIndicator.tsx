import React from 'react';
import { cn } from '../../utils/cn';

interface StatusIndicatorProps {
  status: 'healthy' | 'degraded' | 'offline' | 'checking';
  showLabel?: boolean;
  className?: string;
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status,
  showLabel = true,
  className,
}) => {
  const configs = {
    healthy: {
      color: 'bg-emerald-400',
      pingColor: 'bg-emerald-400',
      text: 'API Online',
      textColor: 'text-emerald-400',
    },
    degraded: {
      color: 'bg-amber-400',
      pingColor: 'bg-amber-400',
      text: 'API Degraded',
      textColor: 'text-amber-400',
    },
    offline: {
      color: 'bg-rose-400',
      pingColor: 'bg-rose-400',
      text: 'API Offline',
      textColor: 'text-rose-400',
    },
    checking: {
      color: 'bg-slate-400',
      pingColor: 'bg-slate-400',
      text: 'Connecting...',
      textColor: 'text-slate-400',
    },
  };

  const current = configs[status] || configs.checking;

  return (
    <div className={cn('inline-flex items-center gap-2 text-xs font-mono', className)}>
      <span className="relative flex h-2 w-2">
        {status === 'healthy' && (
          <span
            className={cn(
              'animate-ping absolute inline-flex h-full w-full rounded-full opacity-75',
              current.pingColor
            )}
          />
        )}
        <span className={cn('relative inline-flex rounded-full h-2 w-2', current.color)} />
      </span>
      {showLabel && <span className={cn('font-medium', current.textColor)}>{current.text}</span>}
    </div>
  );
};
