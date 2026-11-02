export interface NavItem {
  id: string;
  label: string;
  path: string;
  icon: string;
  badge?: string;
}

export interface MetricCardData {
  id: string;
  label: string;
  value: string | number;
  change: string;
  changeType: 'positive' | 'negative' | 'neutral';
  description: string;
  icon: string;
}

export interface RepositoryItem {
  id: string;
  name: string;
  fullName: string;
  description: string;
  language: string;
  languageColor: string;
  stars: number;
  branch: string;
  lastScanned: string;
  status: 'clean' | 'warning' | 'alert' | 'scanning';
  issuesCount: number;
  securityAlertsCount: number;
  healthScore: number;
}

export interface AnalysisActivity {
  id: string;
  repository: string;
  branch: string;
  commitHash: string;
  type: 'Security Audit' | 'Static Analysis' | 'Architecture Map' | 'Complexity Scan';
  status: 'completed' | 'in_progress' | 'failed';
  duration: string;
  timestamp: string;
  findings: {
    critical: number;
    warnings: number;
    info: number;
  };
}

export interface BackendHealth {
  status: 'healthy' | 'degraded' | 'offline' | 'checking';
  application: string;
  version: string;
  environment?: string;
  database?: {
    connected: boolean;
    error?: string | null;
  };
  redis?: {
    connected: boolean;
    error?: string | null;
  };
}
