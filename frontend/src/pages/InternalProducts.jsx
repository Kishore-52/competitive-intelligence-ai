import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { Plus, Trash2, ShieldAlert, Sparkles, PlusCircle } from 'lucide-react';

export const InternalProducts = () => {
  const { products, createProduct, removeProduct } = useApp();
  
  // Form State
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [pricing, setPricing] = useState('');
  const [newFeatureText, setNewFeatureText] = useState('');
  const [features, setFeatures] = useState([]);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  
  const [showAddForm, setShowAddForm] = useState(false);

  const handleAddFeature = (e) => {
    e.preventDefault();
    if (!newFeatureText.trim()) return;
    setFeatures([...features, newFeatureText.trim()]);
    setNewFeatureText('');
  };

  const handleRemoveFeature = (idx) => {
    setFeatures(features.filter((_, i) => i !== idx));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setSuccessMsg('');

    if (!name || !description) {
      setErrorMsg('Product name and description are required.');
      return;
    }

    const payload = {
      name: name.trim(),
      description: description.trim(),
      pricing: pricing.trim(),
      features
    };

    const res = await createProduct(payload);
    if (res.success) {
      setSuccessMsg(`Product '${name}' registered successfully and vectorized in RAG store.`);
      setName('');
      setDescription('');
      setPricing('');
      setFeatures([]);
      setShowAddForm(false);
    } else {
      setErrorMsg(res.error || 'Failed to register product.');
    }
  };

  const handleDeleteProduct = async (id, pName) => {
    if (window.confirm(`Are you sure you want to delete ${pName}? This will remove it from the RAG matching registry.`)) {
      await removeProduct(id);
    }
  };

  return (
    <div>
      <div className="header-container">
        <div>
          <h1 className="page-title">Internal Products registry</h1>
          <p className="page-subtitle">Manage company products acting as RAG targets for competitive gap analysis</p>
        </div>
        <button 
          className="btn-primary" 
          onClick={() => setShowAddForm(!showAddForm)}
        >
          {showAddForm ? 'View Registry' : 'Register Product'}
        </button>
      </div>

      {successMsg && (
        <div style={{ padding: '12px 18px', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.2)', color: 'var(--color-success)', borderRadius: '8px', marginBottom: '24px', fontSize: '14px' }}>
          {successMsg}
        </div>
      )}

      {showAddForm ? (
        <div className="glass-card" style={{ maxWidth: '800px', margin: '0 auto' }}>
          <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '20px', display: 'flex', align: 'center', gap: '8px' }}>
            <Sparkles size={18} style={{ color: 'var(--color-primary)' }} />
            New Product Profile
          </h2>
          {errorMsg && (
            <div style={{ padding: '10px 14px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', color: 'var(--color-danger)', borderRadius: '6px', marginBottom: '16px', fontSize: '13px' }}>
              {errorMsg}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Product Name</label>
              <input 
                type="text" 
                className="form-control" 
                placeholder="e.g. Antigravity Docs"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Product Description</label>
              <textarea 
                className="form-control" 
                rows="3"
                placeholder="Describe the product's core utility, main workflows, and target use cases..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Pricing details</label>
              <input 
                type="text" 
                className="form-control" 
                placeholder="e.g. Included in Suite, or Standalone $5/user/month"
                value={pricing}
                onChange={(e) => setPricing(e.target.value)}
              />
            </div>

            {/* Feature Add Sub-Form */}
            <div className="form-group" style={{ marginBottom: '24px' }}>
              <label className="form-label">Core Capabilities / Features</label>
              <div style={{ display: 'flex', gap: '8px' }}>
                <input 
                  type="text" 
                  className="form-control" 
                  placeholder="e.g. Real-time co-authoring with cursor tracking"
                  value={newFeatureText}
                  onChange={(e) => setNewFeatureText(e.target.value)}
                />
                <button 
                  type="button" 
                  className="btn-secondary" 
                  style={{ display: 'flex', align: 'center', justifyContent: 'center' }}
                  onClick={handleAddFeature}
                >
                  <Plus size={16} />
                </button>
              </div>

              {features.length > 0 && (
                <div className="features-input-list">
                  {features.map((feat, idx) => (
                    <div className="feature-tag" key={idx}>
                      <span>{feat}</span>
                      <Trash2 
                        size={14} 
                        className="feature-tag-delete"
                        onClick={() => handleRemoveFeature(idx)}
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>

            <button type="submit" className="btn-primary" style={{ padding: '12px 24px' }}>
              Save Product & Index
            </button>
          </form>
        </div>
      ) : (
        <div>
          {products.length === 0 ? (
            <div className="glass-card" style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-muted)' }}>
              <ShieldAlert size={40} style={{ margin: '0 auto 16px', display: 'block', color: 'var(--text-muted)' }} />
              <h3>No internal products registered</h3>
              <p style={{ fontSize: '14px', marginTop: '6px', marginBottom: '20px' }}>
                You must register at least one product before running comparative intelligence tasks.
              </p>
              <button className="btn-primary" onClick={() => setShowAddForm(true)}>
                <PlusCircle size={16} />
                Add Product Now
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              {products.map((p) => {
                let parsedFeatures = [];
                try {
                  parsedFeatures = JSON.parse(p.features);
                } catch(e) {}
                
                return (
                  <div className="glass-card" key={p.id} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div>
                        <h2 style={{ fontSize: '20px', color: 'var(--text-primary)', fontWeight: 600 }}>{p.name}</h2>
                        <div style={{ fontSize: '12px', color: '#a5b4fc', marginTop: '4px', fontStyle: 'italic' }}>
                          Pricing: {p.pricing || 'Not specified'}
                        </div>
                      </div>
                      
                      <button 
                        className="btn-danger" 
                        onClick={() => handleDeleteProduct(p.id, p.name)}
                      >
                        <Trash2 size={14} />
                        Delete Product
                      </button>
                    </div>

                    <p style={{ color: 'var(--text-secondary)', fontSize: '14px', lineHeight: 1.5 }}>
                      {p.description}
                    </p>

                    {parsedFeatures.length > 0 && (
                      <div>
                        <h4 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '8px', letterSpacing: '0.05em' }}>
                          Indexed Capabilities
                        </h4>
                        <ul style={{ listStyle: 'none', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px', paddingLeft: '4px' }}>
                          {parsedFeatures.map((feat, idx) => (
                            <li key={idx} style={{ fontSize: '13px', color: '#e2e8f0', display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
                              <span style={{ color: 'var(--color-primary)', fontWeight: 'bold' }}>•</span>
                              <span>{feat}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
