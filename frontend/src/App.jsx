import { useState, useEffect } from 'react';
import { Database, Activity, MessageSquare, BarChart2, Upload as UploadIcon, Search as SearchIcon } from 'lucide-react';
import DocumentUpload from './components/DocumentUpload';
import SearchInterface from './components/SearchInterface';
import StrategyComparison from './components/StrategyComparison';
import QAInterface from './components/QAInterface';
import AdvancedEvaluation from './components/AdvancedEvaluation';
import { documentsAPI, healthAPI } from './services/api';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('search');
  const [stats, setStats] = useState(null);
  const [health, setHealth] = useState(null);

  const loadStats = async () => {
    try {
      const data = await documentsAPI.stats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const loadHealth = async () => {
    try {
      const data = await healthAPI.check();
      setHealth(data);
    } catch (error) {
      console.error('Failed to load health:', error);
    }
  };

  useEffect(() => {
    loadStats();
    loadHealth();
    
    const interval = setInterval(() => {
      loadStats();
      loadHealth();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <Database size={32} />
            <h1>Semantic Search System</h1>
          </div>
          
          {stats && (
            <div className="stats-bar">
              <div className="stat">
                <span className="stat-label">Documents</span>
                <span className="stat-value">{stats.total_documents}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Vectors</span>
                <span className="stat-value">{stats.total_vectors}</span>
              </div>
              {health && (
                <div className="stat status">
                  <Activity size={16} />
                  <span className={`status-${health.status}`}>
                    {health.status.toUpperCase()}
                  </span>
                </div>
              )}
            </div>
          )}
        </div>

        <nav className="nav-tabs">
          <button
            className={activeTab === 'search' ? 'active' : ''}
            onClick={() => setActiveTab('search')}
          >
            <SearchIcon size={18} style={{marginRight: '8px'}}/> Search
          </button>
          
          <button
            className={activeTab === 'chat' ? 'active' : ''}
            onClick={() => setActiveTab('chat')}
          >
            <MessageSquare size={18} style={{marginRight: '8px'}}/> Ask AI
          </button>

          <button
            className={activeTab === 'upload' ? 'active' : ''}
            onClick={() => setActiveTab('upload')}
          >
            <UploadIcon size={18} style={{marginRight: '8px'}}/> Upload
          </button>
          
          <button
            className={activeTab === 'compare' ? 'active' : ''}
            onClick={() => setActiveTab('compare')}
          >
             <BarChart2 size={18} style={{marginRight: '8px'}}/> Compare
          </button>
        </nav>
      </header>

      <main className="app-main">
        {activeTab === 'search' && <SearchInterface />}
        
        {activeTab === 'chat' && <QAInterface />}
        
        {activeTab === 'upload' && (
          <DocumentUpload onUploadSuccess={loadStats} />
        )}
        
        {activeTab === 'compare' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            <StrategyComparison />
            <AdvancedEvaluation />
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>
          Semantic Search System using FAISS, BM25, and Hybrid Strategies
        </p>
        <p className="footer-tech">
          React + FastAPI + FAISS + SentenceTransformers
        </p>
      </footer>
    </div>
  );
}

export default App;