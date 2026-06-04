import React, { useState, useEffect, useRef } from 'react';
import { useApp } from '../context/AppContext';
import { Play, Terminal as TermIcon, FileCheck, AlertTriangle } from 'lucide-react';

export const Analyze = ({ setSelectedReportId }) => {
  const { triggerAnalysis, setActiveTab } = useApp();
  const [competitorName, setCompetitorName] = useState('');
  const [featureName, setFeatureName] = useState('');
  const [status, setStatus] = useState('idle'); // idle, running, completed, error
  const [logs, setLogs] = useState([]);
  const [currentAgent, setCurrentAgent] = useState('');
  const [activeReportId, setActiveReportId] = useState(null);
  
  // Pipeline node states
  const [nodes, setNodes] = useState({
    researcher: 'pending', // pending, active, completed
    analyzer: 'pending',
    comparer: 'pending',
    reporter: 'pending'
  });

  const terminalEndRef = useRef(null);

  // Check for preset values from Dashboard quick launch
  useEffect(() => {
    const presetComp = sessionStorage.getItem('preset_competitor');
    const presetFeat = sessionStorage.getItem('preset_feature');
    if (presetComp && presetFeat) {
      setCompetitorName(presetComp);
      setFeatureName(presetFeat);
      sessionStorage.removeItem('preset_competitor');
      sessionStorage.removeItem('preset_feature');
    }
  }, []);

  // Auto scroll logs
  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const addLog = (agent, text, type = 'default') => {
    setLogs((prev) => [...prev, {
      timestamp: new Date().toLocaleTimeString(),
      agent,
      text,
      type
    }]);
  };

  const handleStartAnalysis = async (e) => {
    e.preventDefault();
    if (!competitorName || !featureName) return;

    setStatus('running');
    setLogs([]);
    setCurrentAgent('Orchestrator');
    setNodes({
      researcher: 'pending',
      analyzer: 'pending',
      comparer: 'pending',
      reporter: 'pending'
    });
    addLog('Orchestrator', `Initializing Multi-Agent analysis pipeline for competitor: '${competitorName}', feature: '${featureName}'...`);

    const result = await triggerAnalysis(competitorName, featureName);
    if (!result || !result.success) {
      setStatus('error');
      addLog('Orchestrator', 'Failed to trigger background analysis pipeline. Check connection to backend.', 'error');
      return;
    }

    const reportId = result.reportId;
    setActiveReportId(reportId);
    connectToLogStream(reportId);
  };

  const connectToLogStream = (reportId) => {
    const streamUrl = `http://127.0.0.1:8000/api/reports/stream/${reportId}`;
    const eventSource = new EventSource(streamUrl);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        // Update logs
        const type = data.status === 'error' || data.status === 'failed' ? 'error' 
                   : data.status === 'success' || data.status === 'done' ? 'success'
                   : data.status === 'warning' ? 'warning' : 'default';
                   
        addLog(data.agent, data.message, type);
        setCurrentAgent(data.agent);

        // Update pipeline visual node statuses
        if (data.agent === 'Researcher') {
          setNodes(prev => ({ ...prev, researcher: data.status }));
        } else if (data.agent === 'Analyzer') {
          setNodes(prev => ({ 
            ...prev, 
            researcher: 'completed', 
            analyzer: data.status === 'success' ? 'completed' : data.status 
          }));
        } else if (data.agent === 'Comparer') {
          setNodes(prev => ({ 
            ...prev, 
            analyzer: 'completed', 
            comparer: data.status === 'success' ? 'completed' : data.status 
          }));
        } else if (data.agent === 'Reporter') {
          setNodes(prev => ({ 
            ...prev, 
            comparer: 'completed', 
            reporter: data.status === 'success' ? 'completed' : data.status 
          }));
        } else if (data.agent === 'Orchestrator' && data.status === 'done') {
          setNodes(prev => ({
            researcher: 'completed',
            analyzer: 'completed',
            comparer: 'completed',
            reporter: 'completed'
          }));
          setStatus('completed');
          eventSource.close();
        } else if (data.status === 'failed' || data.status === 'error') {
          setStatus('error');
          eventSource.close();
        }
      } catch (e) {
        console.error("Error reading SSE stream message:", e);
      }
    };

    eventSource.onerror = (err) => {
      console.error("SSE Connection error:", err);
      addLog('System', 'Connection to log stream interrupted. The pipeline may still run in the background.', 'warning');
      eventSource.close();
      // Polling fallback or timeout can be set here if necessary
    };
  };

  const handleViewReport = () => {
    if (activeReportId) {
      setSelectedReportId(activeReportId);
      setActiveTab('reports');
    }
  };

  const getProgressWidth = () => {
    if (nodes.reporter === 'completed') return '100%';
    if (nodes.comparer === 'completed' || nodes.reporter === 'active') return '75%';
    if (nodes.analyzer === 'completed' || nodes.comparer === 'active') return '50%';
    if (nodes.researcher === 'completed' || nodes.analyzer === 'active') return '25%';
    if (nodes.researcher === 'active') return '12%';
    return '0%';
  };

  return (
    <div>
      <div className="header-container">
        <div>
          <h1 className="page-title">Deploy Competitor Scan</h1>
          <p className="page-subtitle">Trigger live multi-agent RAG retrieval and threat indexing</p>
        </div>
      </div>

      <div style={{ maxWidth: '900px', margin: '0 auto' }}>
        {status === 'idle' && (
          <div className="glass-card">
            <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '20px' }}>Analysis Parameters</h2>
            <form onSubmit={handleStartAnalysis}>
              <div className="form-group">
                <label className="form-label">Competitor Platform</label>
                <input 
                  type="text" 
                  className="form-control" 
                  placeholder="e.g. Slack, Zoom, Jira, HubSpot"
                  value={competitorName}
                  onChange={(e) => setCompetitorName(e.target.value)}
                  required
                />
              </div>

              <div className="form-group" style={{ marginBottom: '28px' }}>
                <label className="form-label">Feature Launch / Update Name</label>
                <input 
                  type="text" 
                  className="form-control" 
                  placeholder="e.g. Canvas, AI Companion, Sprint Agents"
                  value={featureName}
                  onChange={(e) => setFeatureName(e.target.value)}
                  required
                />
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                  Tip: Common features like 'Slack Canvas' or 'Zoom AI Companion' trigger high-fidelity seeded files instantly.
                </span>
              </div>

              <button type="submit" className="btn-primary" style={{ padding: '12px 24px' }}>
                <Play size={16} />
                Deploy Agents
              </button>
            </form>
          </div>
        )}

        {(status === 'running' || status === 'completed' || status === 'error') && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {/* Visual Node Diagram */}
            <div className="glass-card" style={{ padding: '32px 24px' }}>
              <div className="pipeline-container">
                <div className="pipeline-line">
                  <div className="pipeline-line-progress" style={{ width: getProgressWidth() }}></div>
                </div>
                
                {/* Node: Researcher */}
                <div className={`pipeline-node ${nodes.researcher === 'active' ? 'active' : ''} ${nodes.researcher === 'completed' ? 'completed' : ''}`}>
                  <div className="pipeline-circle">01</div>
                  <span className="pipeline-node-name">Researcher</span>
                </div>
                
                {/* Node: Analyzer */}
                <div className={`pipeline-node ${nodes.analyzer === 'active' ? 'active' : ''} ${nodes.analyzer === 'completed' ? 'completed' : ''}`}>
                  <div className="pipeline-circle">02</div>
                  <span className="pipeline-node-name">Analyzer</span>
                </div>
                
                {/* Node: Comparer */}
                <div className={`pipeline-node ${nodes.comparer === 'active' ? 'active' : ''} ${nodes.comparer === 'completed' ? 'completed' : ''}`}>
                  <div className="pipeline-circle">03</div>
                  <span className="pipeline-node-name">Comparer (RAG)</span>
                </div>
                
                {/* Node: Reporter */}
                <div className={`pipeline-node ${nodes.reporter === 'active' ? 'active' : ''} ${nodes.reporter === 'completed' ? 'completed' : ''}`}>
                  <div className="pipeline-circle">04</div>
                  <span className="pipeline-node-name">Reporter</span>
                </div>
              </div>
              
              {status === 'running' && (
                <div style={{ textAlign: 'center', fontSize: '13px', color: 'var(--text-secondary)' }}>
                  Active Agent: <strong style={{ color: 'var(--color-primary)' }}>{currentAgent}</strong> is executing workflows...
                </div>
              )}
            </div>

            {/* Console Log Terminal */}
            <div className="glass-card" style={{ padding: '0px', overflow: 'hidden' }}>
              <div style={{ padding: '14px 20px', background: 'rgba(15, 23, 42, 0.9)', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', align: 'center' }}>
                <div style={{ display: 'flex', align: 'center', gap: '8px', fontSize: '13px', fontWeight: 600, color: 'var(--text-secondary)' }}>
                  <TermIcon size={16} />
                  <span>Agent Stream Logs</span>
                </div>
                <div style={{ display: 'flex', gap: '5px' }}>
                  <span className="terminal-dot dot-red"></span>
                  <span className="terminal-dot dot-yellow"></span>
                  <span className="terminal-dot dot-green"></span>
                </div>
              </div>
              <div className="terminal-card">
                {logs.map((log, idx) => (
                  <div className="terminal-row" key={idx}>
                    <span className="terminal-timestamp">[{log.timestamp}]</span>
                    <span className={`terminal-agent agent-${log.agent}`}>{log.agent}:</span>
                    <span className={`terminal-text ${log.type}`}>{log.text}</span>
                  </div>
                ))}
                {logs.length === 0 && (
                  <div style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>Awaiting logs from stream connection...</div>
                )}
                <div ref={terminalEndRef} />
              </div>
            </div>

            {/* Success Actions */}
            {status === 'completed' && (
              <div className="glass-card" style={{ border: '1px solid rgba(16, 185, 129, 0.3)', background: 'rgba(16, 185, 129, 0.02)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <div style={{ background: 'rgba(16, 185, 129, 0.1)', color: 'var(--color-success)', padding: '10px', borderRadius: '50%' }}>
                    <FileCheck size={24} />
                  </div>
                  <div>
                    <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#a7f3d0' }}>Intelligence Scan Successful</h3>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '2px' }}>
                      SWOT metrics, feature gap matrix, and strategic report have been compiled.
                    </p>
                  </div>
                </div>
                <button className="btn-primary" onClick={handleViewReport}>
                  Go to Report
                </button>
              </div>
            )}

            {/* Error Actions */}
            {status === 'error' && (
              <div className="glass-card" style={{ border: '1px solid rgba(239, 68, 68, 0.3)', background: 'rgba(239, 68, 68, 0.02)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <div style={{ background: 'rgba(239, 68, 68, 0.1)', color: 'var(--color-danger)', padding: '10px', borderRadius: '50%' }}>
                    <AlertTriangle size={24} />
                  </div>
                  <div>
                    <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#fca5a5' }}>Pipeline Execution Halted</h3>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '2px' }}>
                      An error occurred during agent collaboration. Review stream logs above.
                    </p>
                  </div>
                </div>
                <button className="btn-secondary" onClick={() => setStatus('idle')}>
                  Configure & Retry
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
