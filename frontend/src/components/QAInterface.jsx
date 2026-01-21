import { useState } from 'react';
import { MessageSquare, Bot, FileText, Zap } from 'lucide-react';
import { llmAPI } from '../services/api';

export default function QAInterface() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [useRetrieval, setUseRetrieval] = useState(true);

  const handleAsk = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setResponse(null);
    try {
      const data = await llmAPI.answer(query, useRetrieval);
      setResponse(data);
    } catch (error) {
      setResponse({ 
        answer: "An error occurred while processing your request.", 
        sources_used: 0 
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="search-container">
      <h2><Bot size={24} /> Ask AI</h2>

      <div className="search-box">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleAsk()}
          placeholder="Ask a question about your documents..."
          className="search-input"
        />
        <button onClick={handleAsk} disabled={loading} className="btn btn-primary">
          <MessageSquare size={20} />
          {loading ? 'Processing...' : 'Ask'}
        </button>
      </div>

      <div className="search-options">
        <div className="option-group">
          <label>
            <input 
              type="checkbox" 
              checked={useRetrieval}
              onChange={(e) => setUseRetrieval(e.target.checked)}
            />
            Use Document Context
          </label>
        </div>
      </div>

      {response && (
        <div className="results-container">
          <div className="result-card" style={{ borderLeft: '4px solid var(--primary-color)' }}>
            <div className="result-header">
              <h3>Answer</h3>
            </div>
            
            <p className="result-text" style={{ fontSize: '1.1rem', marginBottom: '1.5rem', whiteSpace: 'pre-wrap' }}>
              {response.answer}
            </p>

            <div className="result-meta" style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1rem' }}>
              {response.generation_time_ms && (
                <div className="meta-item">
                  <Zap size={16} />
                  <span>Time: {response.generation_time_ms.toFixed(0)}ms</span>
                </div>
              )}
              <div className="meta-item">
                <FileText size={16} />
                <span>Sources: {response.sources_used}</span>
              </div>
            </div>
          </div>

          {response.context_chunks && response.context_chunks.length > 0 && (
            <div style={{ marginTop: '2rem' }}>
              <h4>Context Sources</h4>
              <div className="results-list" style={{ marginTop: '1rem' }}>
                {response.context_chunks.map((ctx, idx) => (
                  <div key={idx} className="result-card" style={{ padding: '1rem', opacity: 0.8 }}>
                    <div className="result-header" style={{ marginBottom: '0.5rem' }}>
                      <span className="result-rank">#{idx + 1}</span>
                      <small>{ctx.filename}</small>
                    </div>
                    <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                      {ctx.text.substring(0, 150)}...
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}