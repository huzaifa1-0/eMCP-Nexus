import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import AlertToast, { showToast } from '../components/AlertToast';
import MetricCard from '../components/MetricCard';
import { API_BASE_URL } from '../api/config';
import { useAuth } from '../hooks/useAuth';

export default function SellerDashboardPage() {
  const { token, isLoggedIn } = useAuth();
  const navigate = useNavigate();

  const [metrics, setMetrics] = useState({
    totalInstalls: 0,
    totalRuns: 0,
    tokensUsed: 0,
    totalRevenue: 0,
  });
  const [performanceData, setPerformanceData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  useEffect(() => {
    if (!isLoggedIn) {
      showToast('Please log in to view your dashboard', 'error');
      setTimeout(() => navigate('/'), 2000);
      return;
    }

    // Set default dates
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - 30);
    setStartDate(start.toISOString().split('T')[0]);
    setEndDate(end.toISOString().split('T')[0]);

    fetchDashboardData();
  }, [isLoggedIn]);

  async function fetchDashboardData() {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/seller_dashboard/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      if (!res.ok) throw new Error('Failed to load stats');
      const data = await res.json();

      setMetrics({
        totalInstalls: data.totalInstalls || 0,
        totalRuns: data.totalRuns || 0,
        tokensUsed: data.tokensUsed || 0,
        totalRevenue: data.totalRevenue || 0,
      });
      setPerformanceData(data.performanceData || []);
    } catch {
      showToast('Could not load dashboard data. Is the server running?', 'error');
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <Navbar />
      <AlertToast />

      <div className="page-container">
        <div className="alert">
          <i className="fas fa-info-circle"></i>
          Your dashboard metrics are updated in real-time.
        </div>

        <div className="card">
          <div className="card-header-actions">
            <h2 className="card-title" style={{ marginBottom: 0 }}>
              <i className="fas fa-chart-line"></i> Seller Dashboard
            </h2>
            <button className="btn btn-primary" onClick={() => navigate('/create')}>
              <i className="fas fa-plus"></i> Create eMCP
            </button>
          </div>

          <div className="welcome">Welcome back, Client!</div>

          <div className="form-group">
            <label><i className="fas fa-filter"></i> Date Filter</label>
            <div className="date-filter">
              <input type="date" className="form-control" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
              <span>to</span>
              <input type="date" className="form-control" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
              <button className="btn btn-primary" onClick={() => {
                fetchDashboardData();
                showToast('Refreshed data from database', 'success');
              }}>
                <i className="fas fa-check"></i> Apply Filter
              </button>
            </div>
          </div>
        </div>

        <div className="metrics-grid">
          <MetricCard
            icon="download"
            title="Total Installs"
            value={loading ? '...' : metrics.totalInstalls}
          />
          <MetricCard
            icon="play-circle"
            title="Total Runs"
            value={loading ? '...' : metrics.totalRuns}
          />
          <MetricCard
            icon="coins"
            title="Tokens Used"
            value={loading ? '...' : metrics.tokensUsed.toLocaleString()}
          />
          <MetricCard
            icon="dollar-sign"
            title="Total Revenue"
            value={loading ? '...' : `$${metrics.totalRevenue.toFixed(2)}`}
            isRevenue
          />
        </div>

        <div className="card">
          <h2 className="card-title">
            <i className="fas fa-chart-bar"></i> eMCP Nexus Performance Metrics
          </h2>

          <div className="table-responsive">
            <table className="metrics-table">
              <thead>
                <tr>
                  <th>eMCP Name</th>
                  <th>Installs</th>
                  <th>Runs</th>
                  <th>Tokens</th>
                  <th>Revenue</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {performanceData.length === 0 ? (
                  <tr>
                    <td colSpan="6">
                      <div className="no-data">
                        <i className="fas fa-inbox"></i>
                        <div className="no-data-title">No metrics data available</div>
                      </div>
                    </td>
                  </tr>
                ) : (
                  performanceData.map((item, i) => (
                    <tr key={i}>
                      <td><strong>{item.name}</strong></td>
                      <td>{item.installs}</td>
                      <td>{item.runs}</td>
                      <td>{item.tokens?.toLocaleString()}</td>
                      <td style={{ color: '#4cc9f0' }}>${item.revenue?.toFixed(2)}</td>
                      <td>{item.date}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <Footer />
    </>
  );
}
