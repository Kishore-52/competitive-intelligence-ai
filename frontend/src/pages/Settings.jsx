import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { Settings as SettingsIcon, Save, KeyRound, Lightbulb, ToggleLeft, ToggleRight } from 'lucide-react';

export const Settings = () => {
  const { config, updateConfig } = useApp();
  
  // Settings Form State
  const [mockMode, setMockMode] = useState(true);
  const [provider, setProvider] = useState('gemini');
  const [geminiKey, setGeminiKey] = useState('');
  const [openaiKey, setOpenaiKey] = useState('');
  const [geminiModel, setGeminiModel] = useState('gemini-1.5-flash');
  const [openaiModel, setOpenaiModel] = useState('gpt-4o-mini');
  
  const [success, setSuccess] = useState(false);

  // Sync state with global context config
  useEffect(() => {
    if (config) {
      setMockMode(config.MOCK_MODE);
      setProvider(config.PROVIDER);
      setGeminiKey(config.GEMINI_API_KEY || '');
      setOpenaiKey(config.OPENAI_API_KEY || '');
      setGeminiModel(config.GEMINI_MODEL || 'gemini-1.5-flash');
      setOpenaiModel(config.OPENAI_MODEL || 'gpt-4o-mini');
    }
  }, [config]);

  const handleSave = async (e) => {
    e.preventDefault();
    setSuccess(false);

    const newSettings = {
      MOCK_MODE: mockMode,
      PROVIDER: provider,
      GEMINI_API_KEY: geminiKey.trim(),
      OPENAI_API_KEY: openaiKey.trim(),
      GEMINI_MODEL: geminiModel,
      OPENAI_MODEL: openaiModel
    };

    const ok = await updateConfig(newSettings);
    if (ok) {
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    }
  };

  return (
    <div style={{ maxWidth: '850px', margin: '0 auto' }}>
      <div className="header-container">
        <div>
          <h1 className="page-title">System Settings</h1>
          <p className="page-subtitle">Configure agent providers, runtime simulation rules, and API keys</p>
        </div>
      </div>

      {success && (
        <div style={{ padding: '12px 18px', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.2)', color: 'var(--color-success)', borderRadius: '8px', marginBottom: '24px', fontSize: '14px' }}>
          Configuration updated successfully!
        </div>
      )}

      <div className="glass-card">
        <h2 style={{ fontSize: '18px', fontWeight: 600, display: 'flex', align: 'center', gap: '8px', marginBottom: '24px' }}>
          <SettingsIcon size={18} className="text-primary" style={{ color: '#6366f1' }} />
          Credentials & Provider Configuration
        </h2>

        <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Mock Mode Control Row */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px', background: 'rgba(255,255,255,0.01)', border: '1px solid var(--border-color)', borderRadius: 'var(--border-radius-md)' }}>
            <div>
              <strong style={{ fontSize: '15px', color: '#f8fafc', display: 'block' }}>Run in Mock Simulation Mode</strong>
              <span style={{ fontSize: '12.5px', color: 'var(--text-secondary)', marginTop: '4px', display: 'block' }}>
                Simulate competitor searches and report drafts using internal knowledge bases. (No API Keys required).
              </span>
            </div>
            
            <button
              type="button"
              onClick={() => setMockMode(!mockMode)}
              style={{
                background: 'transparent',
                border: 'none',
                cursor: 'pointer',
                color: mockMode ? 'var(--color-warning)' : 'var(--text-muted)',
                display: 'flex',
                alignItems: 'center',
                transition: 'var(--transition-smooth)'
              }}
            >
              {mockMode ? <ToggleRight size={44} /> : <ToggleLeft size={44} />}
            </button>
          </div>

          <div className="form-group">
            <label className="form-label">Default LLM Provider</label>
            <select
              className="form-control"
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              disabled={mockMode}
            >
              <option value="gemini">Gemini API (Google GenAI)</option>
              <option value="openai">OpenAI (GPT Models)</option>
            </select>
          </div>

          {/* Conditional Forms for providers */}
          {provider === 'gemini' ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', padding: '16px', background: 'rgba(99,102,241,0.02)', border: '1px solid rgba(99,102,241,0.1)', borderRadius: 'var(--border-radius-md)' }}>
              <div className="form-group">
                <label className="form-label" style={{ display: 'flex', align: 'center', gap: '6px' }}>
                  <KeyRound size={14} />
                  Gemini API Key
                </label>
                <input
                  type="password"
                  className="form-control"
                  placeholder="Enter your GEMINI_API_KEY..."
                  value={geminiKey}
                  onChange={(e) => setGeminiKey(e.target.value)}
                  disabled={mockMode}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Gemini Model selection</label>
                <select
                  className="form-control"
                  value={geminiModel}
                  onChange={(e) => setGeminiModel(e.target.value)}
                  disabled={mockMode}
                >
                  <option value="gemini-1.5-flash">gemini-1.5-flash (Fast & Recommended)</option>
                  <option value="gemini-1.5-pro">gemini-1.5-pro (High intelligence)</option>
                </select>
              </div>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', padding: '16px', background: 'rgba(14,165,233,0.02)', border: '1px solid rgba(14,165,233,0.1)', borderRadius: 'var(--border-radius-md)' }}>
              <div className="form-group">
                <label className="form-label" style={{ display: 'flex', align: 'center', gap: '6px' }}>
                  <KeyRound size={14} />
                  OpenAI API Key
                </label>
                <input
                  type="password"
                  className="form-control"
                  placeholder="Enter your OPENAI_API_KEY..."
                  value={openaiKey}
                  onChange={(e) => setOpenaiKey(e.target.value)}
                  disabled={mockMode}
                />
              </div>

              <div className="form-group">
                <label className="form-label">OpenAI Model selection</label>
                <select
                  className="form-control"
                  value={openaiModel}
                  onChange={(e) => setOpenaiModel(e.target.value)}
                  disabled={mockMode}
                >
                  <option value="gpt-4o-mini">gpt-4o-mini (Cost-effective & Recommended)</option>
                  <option value="gpt-4o">gpt-4o (High precision)</option>
                </select>
              </div>
            </div>
          )}

          {mockMode && (
            <div style={{ display: 'flex', gap: '10px', alignItems: 'flex-start', padding: '12px 16px', background: 'rgba(245,158,11,0.04)', border: '1px solid rgba(245,158,11,0.15)', borderRadius: 'var(--border-radius-sm)', color: '#fcd34d', fontSize: '13px', lineHeight: 1.4 }}>
              <Lightbulb size={18} style={{ flexShrink: 0, marginTop: '2px', color: 'var(--color-warning)' }} />
              <div>
                <strong>Simulation Mode Active:</strong> You do not need to provide API keys or credentials. The application will use simulated search indexing and LLM reporting layers. Turn off Simulation Mode to configure live APIs.
              </div>
            </div>
          )}

          <button type="submit" className="btn-primary" style={{ alignSelf: 'flex-start', padding: '12px 24px' }}>
            <Save size={16} />
            Save Configuration
          </button>

        </form>
      </div>
    </div>
  );
};
