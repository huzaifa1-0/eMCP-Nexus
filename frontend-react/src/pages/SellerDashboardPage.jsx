import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import AlertToast, { showToast } from '../components/AlertToast';
import MetricCard from '../components/MetricCard';
import { API_BASE_URL } from '../api/config';
import { useAuth } from '../hooks/useAuth';

export default function SellerDashboardPage() {
  const { token, isLoggedIn, userEmail } = useAuth();
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

          <div className="welcome-section">
            <div className="welcome-text">
              <span className="greeting">Welcome back,</span>
              <span className="user-name">{userEmail?.split('@')[0] || 'Seller'}</span>
            </div>
            <div className="status-badge">
              <span className="pulse-dot"></span> Active Session
            </div>
          </div>

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

          {performanceData.length === 0 ? (
            <div className="no-data">
              <i className="fas fa-inbox"></i>
              <div className="no-data-title">No metrics data available</div>
              <p style={{ fontSize: '14px', color: '#444' }}>Metrics will appear here once your eMCPs start getting installs.</p>
            </div>
          ) : (
            <>
              {/* Desktop View */}
              <div className="table-responsive desktop-only">
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
                    {performanceData.map((item, i) => (
                      <tr key={i}>
                        <td><strong>{item.name}</strong></td>
                        <td>{item.installs}</td>
                        <td>{item.runs}</td>
                        <td>{item.tokens?.toLocaleString()}</td>
                        <td style={{ color: '#4cc9f0' }}>${item.revenue?.toFixed(2)}</td>
                        <td>{item.date}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Mobile View */}
              <div className="mobile-only performance-list">
                {performanceData.map((item, i) => (
                  <div key={i} className="performance-item-card">
                    <div className="performance-item-header">
                      <strong>{item.name}</strong>
                      <span className="performance-item-date">{item.date}</span>
                    </div>
                    <div className="performance-item-stats">
                      <div className="p-stat">
                        <span>Installs</span>
                        <strong>{item.installs}</strong>
                      </div>
                      <div className="p-stat">
                        <span>Runs</span>
                        <strong>{item.runs}</strong>
                      </div>
                      <div className="p-stat">
                        <span>Tokens</span>
                        <strong>{item.tokens?.toLocaleString()}</strong>
                      </div>
                      <div className="p-stat revenue">
                        <span>Revenue</span>
                        <strong>${item.revenue?.toFixed(2)}</strong>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>

      <Footer />
      <style>{`
        .welcome-section {
          margin: 25px 0;
          padding: 20px;
          background: rgba(255, 255, 255, 0.03);
          border-left: 4px solid #4cc9f0;
          border-radius: 0 16px 16px 0;
          display: flex;
          justify-content: space-between;
          align-items: center;
          animation: slideIn 0.5s ease-out;
        }
        .welcome-text {
          display: flex;
          flex-direction: column;
          gap: 5px;
        }
        .greeting {
          font-size: 14px;
          color: #888;
          text-transform: uppercase;
          letter-spacing: 1.5px;
        }
        .user-name {
          font-size: 28px;
          font-weight: 800;
          background: linear-gradient(90deg, #fff, #4cc9f0);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }
        .status-badge {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 8px 16px;
          background: rgba(76, 201, 240, 0.1);
          border: 1px solid rgba(76, 201, 240, 0.2);
          border-radius: 30px;
          color: #4cc9f0;
          font-size: 12px;
          font-weight: 600;
          letter-spacing: 0.5px;
        }
        .pulse-dot {
          width: 8px;
          height: 8px;
          background: #4cc9f0;
          border-radius: 50%;
          box-shadow: 0 0 10px #4cc9f0;
          animation: pulse 2s infinite;
        }
        @keyframes pulse {
          0% { transform: scale(1); opacity: 1; }
          50% { transform: scale(1.5); opacity: 0.5; }
          100% { transform: scale(1); opacity: 1; }
        }
        @keyframes slideIn {
          from { opacity: 0; transform: translateX(-20px); }
          to { opacity: 1; transform: translateX(0); }
        }
      `}</style>
    </>
  );
}
