import { useState } from 'react';
import { GitCompare, TrendingUp } from 'lucide-react';
import { searchAPI } from '../services/api';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

export default function StrategyComparison() {
  const [query, setQuery] = useState('');
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCompare = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const data = await searchAPI.compare(query, 5);
      setComparison(data);
    } catch (error) {
      console.error('Comparison error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getChartData = () => {
    if (!comparison) return [];

    return Object.entries(comparison.comparisons).map(([strategy, data]) => ({
      strategy: strategy.charAt(0).toUpperCase() + strategy.slice(1),
      latency: parseFloat(data.latency_ms.toFixed(2)),
      results: data.total_results,
      avgScore:
        data.results.length > 0
          ? parseFloat(
              (
                data.results.reduce((sum, r) => sum + r.score, 0) /
                data.results.length
              ).toFixed(4)
            )
          : 0,
    }));
  };

  return (
    <div className="comparison-container">
      <h2>
        <GitCompare size={24} />
        Strategy Comparison
      </h2>

      <div className="search-box">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleCompare()}
          placeholder="Enter query to compare strategies..."
          className="search-input"
        />
        <button onClick={handleCompare} disabled={loading} className="btn btn-primary">
          <TrendingUp size={20} />
          {loading ? 'Comparing...' : 'Compare'}
        </button>
      </div>

      {comparison && (
        <div className="comparison-results">
          <h3>Comparison Results for: "{comparison.query}"</h3>

          <div className="charts">
            <div className="chart">
              <h4>Latency (ms)</h4>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={getChartData()}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="strategy" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="latency" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="chart">
              <h4>Average Score</h4>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={getChartData()}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="strategy" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="avgScore" fill="#82ca9d" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="comparison-table">
            <table>
              <thead>
                <tr>
                  <th>Strategy</th>
                  <th>Latency (ms)</th>
                  <th>Results</th>
                  <th>Avg Score</th>
                </tr>
              </thead>
              <tbody>
                {getChartData().map((row) => (
                  <tr key={row.strategy}>
                    <td>{row.strategy}</td>
                    <td>{row.latency}</td>
                    <td>{row.results}</td>
                    <td>{row.avgScore}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
