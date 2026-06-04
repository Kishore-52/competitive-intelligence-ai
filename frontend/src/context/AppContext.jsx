import React, { createContext, useState, useEffect, useContext } from 'react';

const AppContext = createContext();

const API_BASE = 'http://127.0.0.1:8000/api';

export const AppProvider = ({ children }) => {
  const [config, setConfig] = useState({
    MOCK_MODE: true,
    GEMINI_API_KEY: '',
    OPENAI_API_KEY: '',
    PROVIDER: 'gemini',
    GEMINI_MODEL: 'gemini-1.5-flash',
    OPENAI_MODEL: 'gpt-4o-mini'
  });
  const [products, setProducts] = useState([]);
  const [reports, setReports] = useState([]);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(false);

  // Fetch configuration on load
  const fetchConfig = async () => {
    try {
      const res = await fetch(`${API_BASE}/config`);
      if (res.ok) {
        const data = await res.json();
        setConfig(data);
      }
    } catch (err) {
      console.error("Failed to fetch configuration:", err);
    }
  };

  // Update configuration
  const updateConfig = async (newSettings) => {
    try {
      const res = await fetch(`${API_BASE}/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newSettings)
      });
      if (res.ok) {
        const data = await res.json();
        setConfig(data);
        return true;
      }
    } catch (err) {
      console.error("Failed to update config:", err);
    }
    return false;
  };

  // Fetch internal products
  const fetchProducts = async () => {
    try {
      const res = await fetch(`${API_BASE}/products`);
      if (res.ok) {
        const data = await res.json();
        setProducts(data);
      }
    } catch (err) {
      console.error("Failed to fetch products:", err);
    }
  };

  // Create product
  const createProduct = async (productData) => {
    try {
      const res = await fetch(`${API_BASE}/products`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(productData)
      });
      if (res.ok) {
        await fetchProducts();
        return { success: true };
      } else {
        const errData = await res.json();
        return { success: false, error: errData.detail || 'Failed to create product' };
      }
    } catch (err) {
      console.error("Failed to create product:", err);
      return { success: false, error: 'Network error occurred' };
    }
  };

  // Delete product
  const removeProduct = async (id) => {
    try {
      const res = await fetch(`${API_BASE}/products/${id}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        await fetchProducts();
        return true;
      }
    } catch (err) {
      console.error("Failed to delete product:", err);
    }
    return false;
  };

  // Fetch competitive reports
  const fetchReports = async () => {
    try {
      const res = await fetch(`${API_BASE}/reports`);
      if (res.ok) {
        const data = await res.json();
        setReports(data);
      }
    } catch (err) {
      console.error("Failed to fetch reports:", err);
    }
  };

  // Trigger competitor feature analysis pipeline
  const triggerAnalysis = async (competitorName, featureName) => {
    try {
      const res = await fetch(`${API_BASE}/reports/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ competitor_name: competitorName, feature_name: featureName })
      });
      if (res.ok) {
        const data = await res.json();
        await fetchReports();
        return { success: true, reportId: data.report_id };
      }
    } catch (err) {
      console.error("Failed to trigger feature analysis:", err);
    }
    return { success: false };
  };

  // Load baseline on mount
  useEffect(() => {
    fetchConfig();
    fetchProducts();
    fetchReports();
  }, []);

  return (
    <AppContext.Provider value={{
      config,
      updateConfig,
      products,
      fetchProducts,
      createProduct,
      removeProduct,
      reports,
      fetchReports,
      triggerAnalysis,
      activeTab,
      setActiveTab,
      loading,
      setLoading
    }}>
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => useContext(AppContext);
