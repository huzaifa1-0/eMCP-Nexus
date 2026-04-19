import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import MarketplacePage from './pages/MarketplacePage'
import SellerDashboardPage from './pages/SellerDashboardPage'
import CreateMCPPage from './pages/CreateMCPPage'
import AuthCallback from './pages/AuthCallback'
import ProfilePage from './pages/ProfilePage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/marketplace" element={<MarketplacePage />} />
      <Route path="/dashboard" element={<SellerDashboardPage />} />
      <Route path="/seller_dashboard.html" element={<SellerDashboardPage />} />
      <Route path="/create" element={<CreateMCPPage />} />
      <Route path="/newmcp.html" element={<CreateMCPPage />} />
      <Route path="/auth-callback" element={<AuthCallback />} />
      <Route path="/profile" element={<ProfilePage />} />
    </Routes>
  )
}

export default App
