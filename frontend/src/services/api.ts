import { BackendHealth } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

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
};
