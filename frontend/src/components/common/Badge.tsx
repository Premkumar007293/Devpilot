import React from 'react';
import { cn } from '../../utils/cn';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'error' | 'violet' | 'outline';
  size?: 'sm' | 'md';
  className?: string;
  dot?: boolean;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  size = 'sm',
  className,
  dot = false,
}) => {
  const variantStyles = {
    default: 'bg-dark-800 text-slate-300 border-white/10',
    success: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    warning: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    error: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
    violet: 'bg-brand-500/10 text-brand-300 border-brand-500/20',
    outline: 'bg-transparent text-slate-400 border-white/10',
  };

  const dotColors = {
    default: 'bg-slate-400',
    success: 'bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.6)]',
    warning: 'bg-amber-400 shadow-[0_0_6px_rgba(251,191,36,0.6)]',
    error: 'bg-rose-400 shadow-[0_0_6px_rgba(251,113,133,0.6)]',
    violet: 'bg-brand-400 shadow-[0_0_6px_rgba(129,140,248,0.6)]',
    outline: 'bg-slate-400',
  };

  const sizeStyles = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 font-medium rounded-md border tracking-wide transition-colors',
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
    >
      {dot && <span className={cn('w-1.5 h-1.5 rounded-full shrink-0', dotColors[variant])} />}
      {children}
    </span>
  );
};
