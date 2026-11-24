import { BackendHealth } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const AUTH_TOKEN_KEY = 'devpilot_access_token';

export const getStoredAuthToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  return window.localStorage.getItem(AUTH_TOKEN_KEY) || null;
};

export const setStoredAuthToken = (token: string | null): void => {
  if (typeof window === 'undefined') return;
  if (token) {
    window.localStorage.setItem(AUTH_TOKEN_KEY, token);
  } else {
    window.localStorage.removeItem(AUTH_TOKEN_KEY);
  }
};

export const buildAuthHeaders = (includeJson = true): Record<string, string> => {
  const headers: Record<string, string> = {};
  if (includeJson) {
    headers['Content-Type'] = 'application/json';
  }

  const token = getStoredAuthToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  return headers;
};

/**
 * Initiates the real GitHub OAuth connect flow.
 * Passes the current browser origin so the backend callback redirects back
 * to the exact frontend port regardless of Vite dev server port configuration.
 */
export const openGitHubConnectFlow = async (login?: string): Promise<void> => {
  const origin = typeof window !== 'undefined' ? window.location.origin : '';

  // First try the GitHub connect endpoint (works for authenticated user or new visitor)
  const connectUrl = new URL(`${API_BASE_URL}/api/v1/github/connect`);
  if (origin) {
    connectUrl.searchParams.set('redirect_origin', origin);
  }
  if (login) {
    connectUrl.searchParams.set('login', login);
  }

  try {
    const response = await fetch(connectUrl.toString(), {
      headers: buildAuthHeaders(false),
    });

    if (response.ok) {
      const data = await response.json();
      if (data.authorization_url) {
        window.location.assign(data.authorization_url);
        return;
      }
    }
  } catch {
    // If connect endpoint fails network-wise, attempt fallback below
  }

  // Fallback to /api/v1/auth/github if connect was rejected
  const authUrl = new URL(`${API_BASE_URL}/api/v1/auth/github`);
  if (origin) {
    authUrl.searchParams.set('redirect_origin', origin);
  }
  if (login) {
    authUrl.searchParams.set('login', login);
  }

  const fallbackResponse = await fetch(authUrl.toString());
  if (!fallbackResponse.ok) {
    const errData = await fallbackResponse.json().catch(() => ({}));
    throw new Error(errData.detail || 'GitHub authorization could not be started.');
  }

  const fallbackData = await fallbackResponse.json();
  if (!fallbackData.authorization_url) {
    throw new Error('GitHub authorization URL was not returned.');
  }

  window.location.assign(fallbackData.authorization_url);
};

export interface GitHubUser {
  login: string;
  name: string;
  avatar_url: string;
  html_url: string;
}

export interface GitHubStatus {
  connected: boolean;
  user: GitHubUser | null;
  repository_count: number;
  github_id?: number;
}

export interface GitHubAccessibleRepo {
  id: number;
  name: string;
  full_name: string;
  description: string | null;
  private: boolean;
  html_url: string;
  default_branch: string;
  is_connected: boolean;
  language: string | null;
  stargazers_count: number;
}

export interface ConnectedRepository {
  id: string;
  organization_id: string;
  owner_user_id?: string | null;
  name: string;
  full_name: string;
  description?: string | null;
  provider: string;
  external_id?: string | null;
  html_url?: string | null;
  default_branch: string;
  is_private: boolean;
  is_active: boolean;
  language?: string | null;
  stars_count?: number;
  last_scanned_at?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface NotificationItem {
  id: string;
  user_id: string;
  title: string;
  message: string;
  notification_type: string;
  severity: string;
  is_read: boolean;
  created_at: string;
  updated_at: string;
  repository_id?: string | null;
  organization_id?: string | null;
}

export interface GlobalSearchResult {
  repositories: Array<{
    id: string;
    name: string;
    full_name: string;
    language: string;
    repository_id?: string;
    kind: string;
  }>;
  files: Array<{
    id: string;
    name: string;
    path: string;
    repository_id: string;
    kind: string;
  }>;
  total: number;
}

export interface FeedbackItem {
  id: string;
  user_id: string;
  category: string;
  description: string;
  repository_id?: string | null;
  related_resource_type?: string | null;
  related_resource_id?: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ArchitectureSnapshot {
  summary: {
    repository_id: string;
    node_count: number;
    file_count: number;
    dependency_count: number;
    cycle_count: number;
    layer_count: number;
    entrypoint_count: number;
    analysis_version: string;
  };
  nodes: Array<{ node_id: string; name: string; path: string; node_type: string; language: string; parent_node_id?: string | null; metadata?: Record<string, unknown> }>;
  edges: Array<{ edge_id: string; source_node: string; target_node: string; relationship_type: string; source_file: string; source_line?: number | null; confidence: number; detection_method: string; metadata?: Record<string, unknown> }>;
  cycles: Array<{ cycle_id: string; participants: string[]; chain: string[]; cycle_length: number; severity: string; remediation: string }>;
  layers: Array<{ file_path: string; layer_name: string; confidence: number; evidence: string[] }>;
  entrypoints: Array<{ file_path: string; symbol_name?: string | null; entry_type: string; detection_evidence: string[] }>;
  impact_analysis?: Record<string, { target: string; direct_dependents: string[]; transitive_dependents: string[]; confidence: number; risk_level: string; evidence: string[] }>;
}

export const apiService = {
  /**
   * Fetch standard health check from backend API.
   */
  async getHealth(): Promise<BackendHealth> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/health`, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return {
        status: data.status,
        application: data.application,
        version: data.version,
      };
    } catch {
      return {
        status: 'offline',
        application: 'DevPilot',
        version: '1.0.0',
      };
    }
  },

  /**
   * Fetch deep system diagnostics if available.
   */
  async getDiagnostics(): Promise<BackendHealth> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/health/diagnostics`, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch {
      return {
        status: 'offline',
        application: 'DevPilot',
        version: '1.0.0',
      };
    }
  },

  /**
   * Get GitHub connection status for the current session.
   */
  async getGitHubStatus(): Promise<GitHubStatus> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/github/status`, {
        headers: buildAuthHeaders(),
      });

      if (!response.ok) {
        return { connected: false, user: null, repository_count: 0 };
      }

      return await response.json();
    } catch {
      return { connected: false, user: null, repository_count: 0 };
    }
  },

  /**
   * List accessible GitHub repositories from the user's connected account.
   */
  async getAccessibleGitHubRepositories(): Promise<GitHubAccessibleRepo[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/github/repositories`, {
        headers: buildAuthHeaders(),
      });

      if (!response.ok) {
        return [];
      }

      return await response.json();
    } catch {
      return [];
    }
  },

  /**
   * List repositories connected to DevPilot.
   */
  async getConnectedRepositories(): Promise<ConnectedRepository[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/github/repositories/connected`, {
        headers: buildAuthHeaders(),
      });

      if (!response.ok) {
        return [];
      }

      return await response.json();
    } catch {
      return [];
    }
  },

  /**
   * Connect an accessible GitHub repository to DevPilot.
   */
  async connectRepository(githubRepoId: number, organizationId?: string): Promise<ConnectedRepository> {
    const response = await fetch(`${API_BASE_URL}/api/v1/github/repositories/connect`, {
      method: 'POST',
      headers: buildAuthHeaders(true),
      body: JSON.stringify({
        github_repo_id: githubRepoId,
        organization_id: organizationId || null,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to connect repository.');
    }

    return await response.json();
  },

  /**
   * Disconnect GitHub account from DevPilot.
   */
  async disconnectGitHub(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/github/disconnect`, {
        method: 'DELETE',
        headers: buildAuthHeaders(false),
      });

      return response.ok;
    } catch {
      return false;
    }
  },

  /**
   * Fetch repository architecture graph from backend when available.
   */
  async getRepositoryArchitecture(repoId: string): Promise<ArchitectureSnapshot | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/repositories/${repoId}/architecture`, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch {
      return null;
    }
  },

  /**
   * Search repositories and files across the user's authorized workspace.
   */
  async searchGlobal(query: string, limit = 10): Promise<GlobalSearchResult> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/search?q=${encodeURIComponent(query)}&limit=${limit}`, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch {
      return { repositories: [], files: [], total: 0 };
    }
  },

  /**
   * Fetch notifications for the current user.
   */
  async getNotifications(unreadOnly = false, limit = 20): Promise<NotificationItem[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/notifications?unread_only=${String(unreadOnly)}&limit=${limit}`, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch {
      return [];
    }
  },

  /**
   * Submit beta user feedback.
   */
  async submitFeedback(payload: { category: string; description: string; repository_id?: string | null; related_resource_type?: string | null; related_resource_id?: string | null }): Promise<FeedbackItem | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch {
      return null;
    }
  },

  /**
   * Fetch the current user's feedback submissions.
   */
  async getFeedback(limit = 20): Promise<FeedbackItem[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/feedback?limit=${limit}`, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch {
      return [];
    }
  },
};
