import { useState } from 'react';
import { Activity, Target, Layers } from 'lucide-react';
import { evaluationAPI } from '../services/api';

export default function AdvancedEvaluation() {
  const [query, setQuery] = useState('');
  const [annResult, setAnnResult] = useState(null);
  const [rangeResult, setRangeResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const runEvaluations = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const [annData, rangeData] = await Promise.all([
        evaluationAPI.compareAnnVsExact(query),
        evaluationAPI.compareRangeVsTopK(query)
      ]);
      setAnnResult(annData);
      setRangeResult(rangeData);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="comparison-container" style={{ marginTop: '2rem' }}>
      <h2><Activity size={24} /> Advanced Evaluation</h2>
      
      <div className="search-box">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter query for evaluation metrics..."
          className="search-input"
        />
        <button onClick={runEvaluations} disabled={loading} className="btn btn-primary">
          Run Analysis
        </button>
      </div>

      <div className="charts" style={{ gridTemplateColumns: '1fr 1fr' }}>
        {annResult && (
          <div className="chart">
            <h4><Target size={16} /> ANN Accuracy (HNSW vs Flat)</h4>
            <div style={{ marginTop: '1rem' }}>
              <div className="stat-row" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span>Recall Accuracy:</span>
                <strong>{(annResult.recall * 100).toFixed(1)}%</strong>
              </div>
              <div className="stat-row" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span>Speedup:</span>
                <strong style={{ color: 'var(--success-color)' }}>{annResult.speedup.toFixed(2)}x faster</strong>
              </div>
              <div className="stat-row" style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Exact Time:</span>
                <span>{annResult.exact_latency_ms.toFixed(2)}ms</span>
              </div>
              <div className="stat-row" style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>ANN Time:</span>
                <span>{annResult.ann_latency_ms.toFixed(2)}ms</span>
              </div>
            </div>
          </div>
        )}

        {rangeResult && (
          <div className="chart">
            <h4><Layers size={16} /> Range vs Top-K Trade-off</h4>
            <div style={{ marginTop: '1rem' }}>
              <div className="stat-row" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span>Range Results (sim &gt; 0.7):</span>
                <strong>{rangeResult.range.results}</strong>
              </div>
              <div className="stat-row" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span>Top-K Results (k=10):</span>
                <strong>{rangeResult.topk.results}</strong>
              </div>
              <div className="stat-row" style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Range Latency:</span>
                <span>{rangeResult.range.latency_ms.toFixed(2)}ms</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}