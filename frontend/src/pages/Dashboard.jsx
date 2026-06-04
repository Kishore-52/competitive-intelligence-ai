import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { 
  Building2, 
  FileText, 
  ShieldAlert, 
  CheckSquare, 
  ArrowRight,
  TrendingUp
} from 'lucide-react';

export const Dashboard = ({ setSelectedReportId }) => {
  const { reports, products, setActiveTab, triggerAnalysis } = useApp();
  const [quickCompetitor, setQuickCompetitor] = useState('');
  const [quickFeature, setQuickFeature] = useState('');

  // Statistics calculation
  const totalReports = reports.length;
  const totalProducts = products.length;
  
  const competitorsCount = new Set(reports.map(r => r.competitor_name.toLowerCase())).size;
  
  const highOrCriticalThreats = reports.filter(
    r => r.threat_level === 'High' || r.threat_level === 'Critical'
  ).length;

  const handleQuickSubmit = (e) => {
    e.preventDefault();
    if (!quickCompetitor || !quickFeature) return;
    
    // Redirect to Analyze page with preset inputs using session storage or URL parameters
    sessionStorage.setItem('preset_competitor', quickCompetitor);
    sessionStorage.setItem('preset_feature', quickFeature);
    setActiveTab('analyze');
  };

  const getThreatBadge = (level) => {
    switch (level) {
      case 'Critical':
        return <span className="badge badge-danger">Critical</span>;
      case 'High':
        return <span className="badge badge-warning" style={{ color: '#ef4444', backgroundColor: 'rgba(239, 68, 68, 0.1)', borderColor: 'rgba(239, 68, 68, 0.2)' }}>High</span>;
      case 'Medium':
        return <span className="badge badge-warning">Medium</span>;
      default:
        return <span className="badge badge-success">Low</span>;
    }
  };

  const handleViewReport = (id) => {
    setSelectedReportId(id);
    setActiveTab('reports');
  };

  return (
    <div>
      <div className="header-container">
        <div>
          <h1 className="page-title">Competitor Intelligence Hub</h1>
          <p className="page-subtitle">Multi-Agent competitive analysis and RAG gap mapping</p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="dashboard-grid">
        <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ padding: '12px', background: 'rgba(99, 102, 241, 0.1)', borderRadius: '12px', color: '#6366f1' }}>
            <Building2 size={24} />
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 500 }}>Competitors Tracked</div>
            <div style={{ fontSize: '28px', fontWeight: 700, marginTop: '4px' }}>{competitorsCount}</div>
          </div>
        </div>

        <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ padding: '12px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '12px', color: '#10b981' }}>
            <CheckSquare size={24} />
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 500 }}>Internal Products</div>
            <div style={{ fontSize: '28px', fontWeight: 700, marginTop: '4px' }}>{totalProducts}</div>
          </div>
        </div>

        <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ padding: '12px', background: 'rgba(14, 165, 233, 0.1)', borderRadius: '12px', color: '#0ea5e9' }}>
            <FileText size={24} />
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 500 }}>Intelligence Reports</div>
            <div style={{ fontSize: '28px', fontWeight: 700, marginTop: '4px' }}>{totalReports}</div>
          </div>
        </div>

        <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ padding: '12px', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '12px', color: '#ef4444' }}>
            <ShieldAlert size={24} />
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 500 }}>Critical/High Threats</div>
            <div style={{ fontSize: '28px', fontWeight: 700, marginTop: '4px', color: '#f87171' }}>{highOrCriticalThreats}</div>
          </div>
        </div>
      </div>

      <div className="detail-grid" style={{ gridTemplateColumns: '1.8fr 1.2fr' }}>
        {/* Recent Competitive Intelligence */}
        <div className="glass-card">
          <h2 style={{ fontSize: '18px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
            <TrendingUp size={18} className="text-primary" style={{ color: '#6366f1' }} />
            Recent Competitor Feature Launches
          </h2>
          
          {reports.length === 0 ? (
            <div style={{ padding: '40px 0', textAlign: 'center', color: 'var(--text-muted)' }}>
              No intelligence reports generated yet. Add your first competitor feature under "Analyze Feature".
            </div>
          ) : (
            <table className="premium-table">
              <thead>
                <tr>
                  <th>Competitor</th>
                  <th>Feature Launch</th>
                  <th>Threat Level</th>
                  <th>Date Tracked</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {reports.map((report) => (
                  <tr key={report.id}>
                    <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{report.competitor_name}</td>
                    <td>{report.feature_name}</td>
                    <td>{getThreatBadge(report.threat_level)}</td>
                    <td style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                      {new Date(report.created_at).toLocaleDateString()}
                    </td>
                    <td>
                      <button 
                        className="btn-secondary" 
                        style={{ padding: '6px 12px', fontSize: '12px' }}
                        onClick={() => handleViewReport(report.id)}
                      >
                        View Report
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Quick Launch Card */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>Launch Competitor Scan</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '24px', lineHeight: 1.4 }}>
              Enter a competitor and their new capability. Our multi-agent orchestrator will deploy research, comparative gap, and SWOT mapping.
            </p>
            
            <form onSubmit={handleQuickSubmit}>
              <div className="form-group">
                <label className="form-label">Competitor Name</label>
                <input 
                  type="text" 
                  className="form-control" 
                  placeholder="e.g. Zoom, HubSpot, Notion"
                  value={quickCompetitor}
                  onChange={(e) => setQuickCompetitor(e.target.value)}
                  required
                />
              </div>

              <div className="form-group" style={{ marginBottom: '24px' }}>
                <label className="form-label">Feature / Update Name</label>
                <input 
                  type="text" 
                  className="form-control" 
                  placeholder="e.g. AI Companion, Chat CRM"
                  value={quickFeature}
                  onChange={(e) => setQuickFeature(e.target.value)}
                  required
                />
              </div>

              <button type="submit" className="btn-primary" style={{ width: '100%', justifyContent: 'center' }}>
                Deploy Agents
                <ArrowRight size={16} />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};
