import { useEffect } from 'react';
import { useAppStore } from '../store/useAppStore';
import { apiService } from '../services/api';

export function useApiHealth() {
  const { backendHealth, setBackendHealth } = useAppStore();

  useEffect(() => {
    let mounted = true;

    async function checkHealth() {
      const result = await apiService.getHealth();
      if (mounted) {
        setBackendHealth(result);
      }
    }

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // 30s heartbeat

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [setBackendHealth]);

  return backendHealth;
}
