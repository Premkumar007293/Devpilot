import { create } from 'zustand';
import { BackendHealth, RepositoryItem, AnalysisActivity } from '../types';

interface AppState {
  sidebarOpen: boolean;
  searchModalOpen: boolean;
  backendHealth: BackendHealth;
  notificationsCount: number;
  repositories: RepositoryItem[];
  activities: AnalysisActivity[];
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setSearchModalOpen: (open: boolean) => void;
  setBackendHealth: (health: BackendHealth) => void;
}

// Realistic sample preview data (clearly identified as Phase 1 Preview Data)
const SAMPLE_REPOSITORIES: RepositoryItem[] = [
  {
    id: 'repo-1',
    name: 'devpilot-core',
    fullName: 'devpilot-ai/devpilot-core',
    description: 'High-performance AI engine and code graph static analysis orchestrator.',
    language: 'Python',
    languageColor: '#3572A5',
    stars: 342,
    branch: 'main',
    lastScanned: '12 mins ago',
    status: 'clean',
    issuesCount: 0,
    securityAlertsCount: 0,
    healthScore: 98,
  },
  {
    id: 'repo-2',
    name: 'nebula-gateway',
    fullName: 'devpilot-ai/nebula-gateway',
    description: 'Cloud microservices edge gateway with distributed rate-limiting.',
    language: 'TypeScript',
    languageColor: '#3178C6',
    stars: 128,
    branch: 'release/v2.1',
    lastScanned: '45 mins ago',
    status: 'warning',
    issuesCount: 4,
    securityAlertsCount: 1,
    healthScore: 84,
  },
  {
    id: 'repo-3',
    name: 'auth-vault-service',
    fullName: 'devpilot-ai/auth-vault-service',
    description: 'Zero-trust authentication service with encrypted session management.',
    language: 'Go',
    languageColor: '#00ADD8',
    stars: 56,
    branch: 'feat/pki-keys',
    lastScanned: '2 hours ago',
    status: 'alert',
    issuesCount: 7,
    securityAlertsCount: 2,
    healthScore: 71,
  },
  {
    id: 'repo-4',
    name: 'telemetry-stream',
    fullName: 'devpilot-ai/telemetry-stream',
    description: 'Real-time telemetry and OpenTelemetry metrics ingestion pipeline.',
    language: 'Rust',
    languageColor: '#DEA584',
    stars: 215,
    branch: 'main',
    lastScanned: '5 hours ago',
    status: 'clean',
    issuesCount: 1,
    securityAlertsCount: 0,
    healthScore: 95,
  },
];

const SAMPLE_ACTIVITIES: AnalysisActivity[] = [
  {
    id: 'act-1',
    repository: 'devpilot-core',
    branch: 'main',
    commitHash: '7f9c2a1',
    type: 'Security Audit',
    status: 'completed',
    duration: '18s',
    timestamp: '12 mins ago',
    findings: { critical: 0, warnings: 0, info: 3 },
  },
  {
    id: 'act-2',
    repository: 'nebula-gateway',
    branch: 'release/v2.1',
    commitHash: '3e41b9d',
    type: 'Static Analysis',
    status: 'completed',
    duration: '42s',
    timestamp: '45 mins ago',
    findings: { critical: 1, warnings: 3, info: 12 },
  },
  {
    id: 'act-3',
    repository: 'auth-vault-service',
    branch: 'feat/pki-keys',
    commitHash: '8b22a0f',
    type: 'Architecture Map',
    status: 'completed',
    duration: '1m 15s',
    timestamp: '2 hours ago',
    findings: { critical: 2, warnings: 5, info: 8 },
  },
  {
    id: 'act-4',
    repository: 'telemetry-stream',
    branch: 'main',
    commitHash: '1a90cc4',
    type: 'Complexity Scan',
    status: 'completed',
    duration: '35s',
    timestamp: '5 hours ago',
    findings: { critical: 0, warnings: 1, info: 4 },
  },
];

export const useAppStore = create<AppState>((set) => ({
  sidebarOpen: true,
  searchModalOpen: false,
  backendHealth: {
    status: 'checking',
    application: 'DevPilot',
    version: '0.1.0-beta',
  },
  notificationsCount: 3,
  repositories: SAMPLE_REPOSITORIES,
  activities: SAMPLE_ACTIVITIES,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setSearchModalOpen: (open) => set({ searchModalOpen: open }),
  setBackendHealth: (health) => set({ backendHealth: health }),
}));
