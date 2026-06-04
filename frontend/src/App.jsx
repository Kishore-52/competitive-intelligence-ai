import React, { useState } from 'react';
import { AppProvider, useApp } from './context/AppContext';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { Analyze } from './pages/Analyze';
import { InternalProducts } from './pages/InternalProducts';
import { Reports } from './pages/Reports';
import { Settings } from './pages/Settings';

function AppContent() {
  const { activeTab } = useApp();
  const [selectedReportId, setSelectedReportId] = useState(null);

  const renderPage = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard setSelectedReportId={setSelectedReportId} />;
      case 'analyze':
        return <Analyze setSelectedReportId={setSelectedReportId} />;
      case 'products':
        return <InternalProducts />;
      case 'reports':
        return <Reports selectedReportId={selectedReportId} setSelectedReportId={setSelectedReportId} />;
      case 'settings':
        return <Settings />;
      default:
        return <Dashboard setSelectedReportId={setSelectedReportId} />;
    }
  };

  return (
    <Layout>
      {renderPage()}
    </Layout>
  );
}

function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}

export default App;
