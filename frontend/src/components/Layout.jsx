import React from 'react';
import { useApp } from '../context/AppContext';
import { 
  LayoutDashboard, 
  SearchCode, 
  Database, 
  FilePieChart, 
  Settings as SettingsIcon, 
  Cpu, 
  FlameKindling,
  Terminal
} from 'lucide-react';

export const Layout = ({ children }) => {
  const { activeTab, setActiveTab, config } = useApp();

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'analyze', label: 'Analyze Feature', icon: SearchCode },
    { id: 'products', label: 'Internal Products', icon: Database },
    { id: 'reports', label: 'Intelligence Reports', icon: FilePieChart },
    { id: 'settings', label: 'System Settings', icon: SettingsIcon },
  ];

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <Cpu className="text-primary" size={24} style={{ color: '#6366f1' }} />
          <span>Antigravity Intel</span>
        </div>
        
        <nav style={{ flexGrow: 1 }}>
          <ul className="sidebar-menu">
            {menuItems.map((item) => {
              const Icon = item.icon;
              return (
                <li key={item.id}>
                  <a
                    className={`sidebar-item ${activeTab === item.id ? 'active' : ''}`}
                    onClick={() => setActiveTab(item.id)}
                  >
                    <Icon size={18} />
                    <span>{item.label}</span>
                  </a>
                </li>
              );
            })}
          </ul>
        </nav>
        
        <div className="sidebar-footer">
          {config.MOCK_MODE ? (
            <div className="mode-badge">
              <Terminal size={14} />
              <span>Mock Engine Active</span>
            </div>
          ) : (
            <div className="mode-badge live">
              <FlameKindling size={14} />
              <span>Live AI Agents Active</span>
            </div>
          )}
        </div>
      </aside>

      {/* Main Panel */}
      <main className="main-content">
        {children}
      </main>
    </div>
  );
};
