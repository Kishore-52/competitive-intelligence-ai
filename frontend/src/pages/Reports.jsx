import React, { useState, useEffect, useRef } from 'react';
import { useApp } from '../context/AppContext';
import { 
  FileText, 
  TrendingUp, 
  ListTodo, 
  Send, 
  Bot, 
  User, 
  ChevronRight,
  Shield,
  Loader2,
  Calendar,
  AlertOctagon
} from 'lucide-react';

// Custom lightweight Markdown-to-HTML parser component
const MarkdownRenderer = ({ content }) => {
  if (!content) return null;

  const lines = content.split('\n');
  const elements = [];
  let currentList = [];
  let currentTable = null;
  let inList = false;
  let inTable = false;

  const parseInlineStyles = (text) => {
    // Basic bold replacement: **text** -> <strong>text</strong>
    const parts = text.split('**');
    return parts.map((part, idx) => {
      if (idx % 2 === 1) {
        return <strong key={idx}>{part}</strong>;
      }
      return part;
    });
  };

  const flushList = (key) => {
    if (currentList.length > 0) {
      elements.push(<ul key={`list-${key}`}>{currentList}</ul>);
      currentList = [];
      inList = false;
    }
  };

  const flushTable = (key) => {
    if (currentTable) {
      elements.push(
        <table key={`table-${key}`} className="report-table">
          <thead>
            <tr>
              {currentTable.headers.map((h, i) => (
                <th key={i}>{h.trim()}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {currentTable.rows.map((row, rIdx) => (
              <tr key={rIdx}>
                {row.map((cell, cIdx) => (
                  <td key={cIdx}>{parseInlineStyles(cell.trim())}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      );
      currentTable = null;
      inTable = false;
    }
  };

  for (let idx = 0; idx < lines.length; idx++) {
    const line = lines[idx];
    const trimmed = line.trim();

    // 1. Tables detection: starts with | and ends with |
    if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
      flushList(idx);
      
      const cells = trimmed.split('|').slice(1, -1);
      
      // Check if it is a header spacer: e.g. | :--- | :--- |
      if (trimmed.includes(':---') || trimmed.includes('---')) {
        continue; // skip the separator row
      }

      if (!inTable) {
        inTable = true;
        currentTable = {
          headers: cells,
          rows: []
        };
      } else {
        currentTable.rows.push(cells);
      }
      continue;
    } else {
      flushTable(idx);
    }

    // 2. Headings
    if (trimmed.startsWith('# ')) {
      flushList(idx);
      elements.push(<h1 key={idx}>{parseInlineStyles(trimmed.slice(2))}</h1>);
    } else if (trimmed.startsWith('## ')) {
      flushList(idx);
      elements.push(<h2 key={idx}>{parseInlineStyles(trimmed.slice(3))}</h2>);
    } else if (trimmed.startsWith('### ')) {
      flushList(idx);
      elements.push(<h3 key={idx}>{parseInlineStyles(trimmed.slice(4))}</h3>);
    } 
    // 3. Horizontal Rule
    else if (trimmed === '---') {
      flushList(idx);
      elements.push(<hr key={idx} style={{ border: 'none', borderBottom: '1px solid var(--border-color)', margin: '24px 0' }} />);
    }
    // 4. Bullet Lists
    else if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
      inList = true;
      currentList.push(
        <li key={idx}>
          {parseInlineStyles(trimmed.slice(2))}
        </li>
      );
    }
    // 5. Standard Paragraphs
    else if (trimmed !== '') {
      if (inList) {
        // If list is interrupted but line is not empty, keep list going or flush
        flushList(idx);
      }
      elements.push(<p key={idx}>{parseInlineStyles(trimmed)}</p>);
    } else {
      // Empty line
      flushList(idx);
    }
  }

  // Flush remaining elements
  flushList(lines.length);
  flushTable(lines.length);

  return <div className="report-markdown">{elements}</div>;
};

export const Reports = ({ selectedReportId, setSelectedReportId }) => {
  const { reports } = useApp();
  const [report, setReport] = useState(null);
  const [activeTab, setActiveTab] = useState('markdown'); // markdown, swot, gaps
  const [chatMessages, setChatMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [reportLoading, setReportLoading] = useState(false);

  const messagesEndRef = useRef(null);

  // Fetch report details when ID changes
  useEffect(() => {
    if (selectedReportId) {
      fetchReportDetails(selectedReportId);
    } else if (reports.length > 0) {
      // Select the first completed report by default if none selected
      const firstCompleted = reports.find(r => r.status === 'Completed');
      if (firstCompleted) {
        setSelectedReportId(firstCompleted.id);
      }
    }
  }, [selectedReportId, reports]);

  // Auto-scroll chat to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const fetchReportDetails = async (id) => {
    setReportLoading(true);
    try {
      // 1. Fetch main report metadata and content
      const res = await fetch(`http://127.0.0.1:8000/api/reports/${id}`);
      if (res.ok) {
        const data = await res.json();
        setReport(data);
      }
      
      // 2. Fetch associated chat history
      const chatRes = await fetch(`http://127.0.0.1:8000/api/reports/${id}/chat`);
      if (chatRes.ok) {
        const chatData = await chatRes.json();
        setChatMessages(chatData);
      }
    } catch (e) {
      console.error("Error loading report details:", e);
    } finally {
      setReportLoading(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || !report) return;

    const userText = inputMessage.trim();
    setInputMessage('');
    
    // Optimistic User Bubble
    setChatMessages(prev => [...prev, { sender: 'user', message: userText }]);
    setChatLoading(true);

    try {
      const res = await fetch(`http://127.0.0.1:8000/api/reports/${report.id}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userText })
      });
      if (res.ok) {
        const data = await res.json();
        setChatMessages(prev => [...prev, data]);
      }
    } catch (err) {
      console.error("Failed to send chat message:", err);
      setChatMessages(prev => [...prev, { sender: 'assistant', message: '**Error:** Failed to connect to backend server. Chat unavailable.' }]);
    } finally {
      setChatLoading(false);
    }
  };

  const getThreatColor = (level) => {
    switch (level) {
      case 'Critical': return '#ef4444';
      case 'High': return '#f59e0b';
      case 'Medium': return '#3b82f6';
      default: return '#10b981';
    }
  };

  return (
    <div>
      <div className="header-container">
        <div>
          <h1 className="page-title">Competitive Intelligence Registry</h1>
          <p className="page-subtitle">Inspect structured intelligence reports and interact with RAG chatbot</p>
        </div>
      </div>

      <div className="detail-grid" style={{ gridTemplateColumns: '260px 1fr 340px', gap: '24px' }}>
        
        {/* Left Side: Reports List Drawer */}
        <div className="glass-card" style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px', height: 'fit-content' }}>
          <h3 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', paddingLeft: '8px', letterSpacing: '0.05em' }}>
            Archived Scans
          </h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {reports.filter(r => r.status === 'Completed').map((r) => (
              <button
                key={r.id}
                onClick={() => setSelectedReportId(r.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  width: '100%',
                  padding: '12px 14px',
                  background: selectedReportId === r.id ? 'rgba(99, 102, 241, 0.1)' : 'transparent',
                  border: '1px solid',
                  borderColor: selectedReportId === r.id ? 'rgba(99, 102, 241, 0.25)' : 'transparent',
                  borderRadius: 'var(--border-radius-md)',
                  color: selectedReportId === r.id ? '#a5b4fc' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  textAlign: 'left',
                  fontSize: '13.5px',
                  fontWeight: 500,
                  transition: 'var(--transition-smooth)'
                }}
              >
                <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
                  <strong>{r.competitor_name}</strong>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{r.feature_name}</span>
                </div>
                <ChevronRight size={14} style={{ color: selectedReportId === r.id ? 'var(--color-primary)' : 'var(--text-muted)' }} />
              </button>
            ))}
            {reports.filter(r => r.status === 'Completed').length === 0 && (
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', padding: '12px 8px', fontStyle: 'italic' }}>
                No completed reports yet.
              </div>
            )}
          </div>
        </div>

        {/* Center: Report detail panel */}
        <div className="glass-card" style={{ minHeight: '650px', display: 'flex', flexDirection: 'column' }}>
          {reportLoading ? (
            <div style={{ display: 'flex', flexDirection: 'column', flexGrow: 1, alignItems: 'center', justifyContent: 'center', gap: '16px', color: 'var(--text-secondary)' }}>
              <Loader2 className="animate-spin" size={32} style={{ color: 'var(--color-primary)' }} />
              <span>Decoding report context...</span>
            </div>
          ) : report ? (
            <div>
              {/* Report Header */}
              <div style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '20px', marginBottom: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <h2 style={{ fontSize: '22px', fontWeight: 700, color: 'var(--text-primary)' }}>
                    {report.competitor_name} - {report.feature_name} Analysis
                  </h2>
                  <div style={{ display: 'flex', align: 'center', gap: '8px', padding: '6px 12px', borderRadius: '50px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-color)' }}>
                    <AlertOctagon size={14} style={{ color: getThreatColor(report.threat_level) }} />
                    <span style={{ fontSize: '12px', fontWeight: 600 }}>Threat: <strong style={{ color: getThreatColor(report.threat_level) }}>{report.threat_level.toUpperCase()}</strong></span>
                  </div>
                </div>
                
                <div style={{ display: 'flex', gap: '16px', marginTop: '10px', fontSize: '13px', color: 'var(--text-muted)' }}>
                  <span style={{ display: 'flex', align: 'center', gap: '6px' }}><Calendar size={14} /> {new Date(report.created_at).toLocaleDateString()}</span>
                  <span>•</span>
                  <span>Sources analyzed: {report.sources?.length || 0} pages</span>
                </div>
              </div>

              {/* Tabs Navbar */}
              <div style={{ display: 'flex', gap: '12px', borderBottom: '1px solid var(--border-color)', paddingBottom: '10px', marginBottom: '24px' }}>
                <button
                  className={`btn-secondary ${activeTab === 'markdown' ? 'active' : ''}`}
                  onClick={() => setActiveTab('markdown')}
                  style={{
                    padding: '8px 16px',
                    fontSize: '13px',
                    background: activeTab === 'markdown' ? 'var(--color-primary-glow)' : 'transparent',
                    borderColor: activeTab === 'markdown' ? 'rgba(99, 102, 241, 0.4)' : 'transparent',
                    color: activeTab === 'markdown' ? '#a5b4fc' : 'var(--text-secondary)'
                  }}
                >
                  <FileText size={14} />
                  Executive Report
                </button>
                
                <button
                  className={`btn-secondary ${activeTab === 'swot' ? 'active' : ''}`}
                  onClick={() => setActiveTab('swot')}
                  style={{
                    padding: '8px 16px',
                    fontSize: '13px',
                    background: activeTab === 'swot' ? 'var(--color-primary-glow)' : 'transparent',
                    borderColor: activeTab === 'swot' ? 'rgba(99, 102, 241, 0.4)' : 'transparent',
                    color: activeTab === 'swot' ? '#a5b4fc' : 'var(--text-secondary)'
                  }}
                >
                  <TrendingUp size={14} />
                  SWOT Matrix
                </button>

                <button
                  className={`btn-secondary ${activeTab === 'gaps' ? 'active' : ''}`}
                  onClick={() => setActiveTab('gaps')}
                  style={{
                    padding: '8px 16px',
                    fontSize: '13px',
                    background: activeTab === 'gaps' ? 'var(--color-primary-glow)' : 'transparent',
                    borderColor: activeTab === 'gaps' ? 'rgba(99, 102, 241, 0.4)' : 'transparent',
                    color: activeTab === 'gaps' ? '#a5b4fc' : 'var(--text-secondary)'
                  }}
                >
                  <ListTodo size={14} />
                  Identified Gaps
                </button>
              </div>

              {/* Tab: Markdown Report */}
              {activeTab === 'markdown' && (
                <MarkdownRenderer content={report.markdown_report} />
              )}

              {/* Tab: SWOT Matrix */}
              {activeTab === 'swot' && (
                <div>
                  <h3 style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '8px', letterSpacing: '0.05em' }}>
                    Competitive Forces Map
                  </h3>
                  
                  <div className="swot-grid">
                    <div className="swot-box swot-s">
                      <div className="swot-title" style={{ color: 'var(--color-success)' }}>Strengths</div>
                      <ul className="swot-list">
                        {report.swot?.strengths?.map((s, idx) => (
                          <li className="swot-item" key={idx}>{s}</li>
                        ))}
                      </ul>
                    </div>

                    <div className="swot-box swot-w">
                      <div className="swot-title" style={{ color: 'var(--color-danger)' }}>Weaknesses</div>
                      <ul className="swot-list">
                        {report.swot?.weaknesses?.map((w, idx) => (
                          <li className="swot-item" key={idx}>{w}</li>
                        ))}
                      </ul>
                    </div>

                    <div className="swot-box swot-o">
                      <div className="swot-title" style={{ color: 'var(--color-secondary)' }}>Opportunities</div>
                      <ul className="swot-list">
                        {report.swot?.opportunities?.map((o, idx) => (
                          <li className="swot-item" key={idx}>{o}</li>
                        ))}
                      </ul>
                    </div>

                    <div className="swot-box swot-t">
                      <div className="swot-title" style={{ color: 'var(--color-warning)' }}>Threats</div>
                      <ul className="swot-list">
                        {report.swot?.threats?.map((t, idx) => (
                          <li className="swot-item" key={idx}>{t}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab: Gap Checklist */}
              {activeTab === 'gaps' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {report.gaps?.map((gap, idx) => (
                    <div key={idx} style={{ padding: '20px', border: '1px solid var(--border-color)', borderRadius: 'var(--border-radius-md)', background: 'rgba(255,255,255,0.01)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                        <h3 style={{ fontSize: '15px', color: '#e2e8f0', fontWeight: 600 }}>{gap.category}</h3>
                        <span 
                          className="badge" 
                          style={{
                            background: gap.severity === 'Critical' || gap.severity === 'High' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(245, 158, 11, 0.1)',
                            color: gap.severity === 'Critical' || gap.severity === 'High' ? '#ef4444' : '#f59e0b',
                            border: '1px solid',
                            borderColor: gap.severity === 'Critical' || gap.severity === 'High' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                          }}
                        >
                          {gap.severity} Severity
                        </span>
                      </div>
                      
                      <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '12px' }}>
                        <strong>Detected Gap:</strong> {gap.gap_description}
                      </p>

                      <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '12px', marginTop: '12px', fontSize: '13.5px', color: '#a5b4fc' }}>
                        <strong>Strategic Recommendation:</strong> {gap.recommendation}
                      </div>
                    </div>
                  ))}
                  {(!report.gaps || report.gaps.length === 0) && (
                    <div style={{ padding: '40px 0', textAlign: 'center', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                      No feature gaps documented in this analysis.
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div style={{ display: 'flex', flexGrow: 1, alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontStyle: 'italic' }}>
              Select a completed report from the left sidebar panel.
            </div>
          )}
        </div>

        {/* Right Side: RAG Chat Sidebar drawer */}
        <div className="chat-container">
          <div className="chat-header">
            <Bot size={18} style={{ color: 'var(--color-primary)' }} />
            <span className="chat-title">Intelligence RAG Chat</span>
          </div>

          <div className="chat-messages">
            {chatMessages.length === 0 && (
              <div style={{ padding: '20px 0', textAlign: 'center', color: 'var(--text-muted)', fontSize: '12px', fontStyle: 'italic', lineHeight: 1.4 }}>
                Ask questions about this competitor launch (pricing, comparison models, swot quadrants, feature gaps).
              </div>
            )}
            
            {chatMessages.map((msg, idx) => (
              <div key={idx} className={`chat-bubble ${msg.sender}`}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '10px', color: 'var(--text-muted)', marginBottom: '4px', textTransform: 'uppercase', fontWeight: 600 }}>
                  {msg.sender === 'user' ? <User size={10} /> : <Bot size={10} />}
                  <span>{msg.sender}</span>
                </div>
                <div style={{ whiteSpace: 'pre-wrap' }}>{msg.message}</div>
              </div>
            ))}
            
            {chatLoading && (
              <div className="chat-bubble assistant" style={{ display: 'flex', align: 'center', gap: '8px', color: 'var(--text-secondary)' }}>
                <Loader2 className="animate-spin" size={14} />
                <span>Interrogating document database...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSendMessage} className="chat-input-area">
            <input
              type="text"
              className="chat-input"
              placeholder={report ? "Ask a question..." : "Select report to chat..."}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              disabled={!report || chatLoading}
            />
            <button 
              type="submit" 
              className="chat-btn"
              disabled={!report || chatLoading || !inputMessage.trim()}
            >
              <Send size={14} />
            </button>
          </form>
        </div>

      </div>
    </div>
  );
};
