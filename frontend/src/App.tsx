import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { DashboardLayout } from './layouts/DashboardLayout';
import { DashboardOverview } from './pages/DashboardOverview';
import { RepositoriesPage } from './pages/RepositoriesPage';
import { CodeAnalysisPage } from './pages/CodeAnalysisPage';
import { SecurityPage } from './pages/SecurityPage';
import { ArchitecturePage } from './pages/ArchitecturePage';
import { AIAssistantPage } from './pages/AIAssistantPage';
import { SettingsPage } from './pages/SettingsPage';
import { OnboardingPage } from './pages/OnboardingPage';
import { AuthCallbackPage } from './pages/AuthCallbackPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Routes>
        <Route path="/auth/callback" element={<AuthCallbackPage />} />
        <Route path="/" element={<DashboardLayout />}>
          <Route index element={<DashboardOverview />} />
          <Route path="onboarding" element={<OnboardingPage />} />
          <Route path="repositories" element={<RepositoriesPage />} />
          <Route path="analysis" element={<CodeAnalysisPage />} />
          <Route path="security" element={<SecurityPage />} />
          <Route path="architecture" element={<ArchitecturePage />} />
          <Route path="assistant" element={<AIAssistantPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
