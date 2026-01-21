import { Clock, FileText, Hash } from 'lucide-react';

export default function SearchResults({ results }) {
  if (!results || results.total_results === 0) {
    return (
      <div className="no-results">
        <p>No results found</p>
      </div>
    );
  }

  return (
    <div className="results-container">
      <div className="results-header">
        <h3>
          Found {results.total_results} results in {results.latency_ms.toFixed(2)}ms
        </h3>
        <span className="strategy-badge">{results.strategy}</span>
      </div>

      <div className="results-list">
        {results.results.map((result, index) => (
          <div key={index} className="result-card">
            <div className="result-header">
              <span className="result-score">
                Score: {result.score.toFixed(4)}
              </span>
              <span className="result-rank">#{index + 1}</span>
            </div>

            <div className="result-meta">
              <div className="meta-item">
                <FileText size={16} />
                <span>{result.filename}</span>
              </div>
              <div className="meta-item">
                <Hash size={16} />
                <span>
                  Chunk {result.chunk_index + 1} of {result.total_chunks}
                </span>
              </div>
            </div>

            <div className="result-text">
              {result.text}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
