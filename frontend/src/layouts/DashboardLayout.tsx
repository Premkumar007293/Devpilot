import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from '../components/layout/Sidebar';
import { TopNav } from '../components/layout/TopNav';
import { SearchModal } from '../components/ui/SearchModal';
import { useApiHealth } from '../hooks/useApiHealth';

export const DashboardLayout: React.FC = () => {
  // Sync API health
  useApiHealth();

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-dark-950 text-slate-100">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
        <TopNav />

        <main className="flex-1 overflow-y-auto px-6 py-6 lg:px-8 space-y-6">
          <Outlet />
        </main>
      </div>

      {/* Global Search Modal */}
      <SearchModal />
    </div>
  );
};
