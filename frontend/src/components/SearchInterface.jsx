import { useState } from 'react';
import { Search, Filter } from 'lucide-react';
import { searchAPI } from '../services/api';
import SearchResults from './SearchResults';

export default function SearchInterface() {
  const [query, setQuery] = useState('');
  const [strategy, setStrategy] = useState('semantic');
  const [k, setK] = useState(5);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const data = await searchAPI.search(query, k, strategy);
      setResults(data);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="search-container">
      <h2> Semantic Search</h2>

      <div className="search-box">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Enter your search query..."
          className="search-input"
        />
        <button onClick={handleSearch} disabled={loading} className="btn btn-primary">
          <Search size={20} />
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      <div className="search-options">
        <div className="option-group">
          <label>
            <Filter size={16} />
            Strategy:
          </label>
          <select value={strategy} onChange={(e) => setStrategy(e.target.value)}>
            <option value="semantic">Semantic (FAISS)</option>
            <option value="keyword">Keyword (BM25)</option>
            <option value="hybrid">Hybrid (Combined)</option>
            <option value="range">Range Search</option>
          </select>
        </div>

        <div className="option-group">
          <label>Results:</label>
          <input
            type="number"
            value={k}
            onChange={(e) => setK(parseInt(e.target.value))}
            min="1"
            max="20"
          />
        </div>
      </div>

      {results && <SearchResults results={results} />}
    </div>
  );
}
