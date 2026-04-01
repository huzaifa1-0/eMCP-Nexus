import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import MarketplacePage from './pages/MarketplacePage'
import SellerDashboardPage from './pages/SellerDashboardPage'
import CreateMCPPage from './pages/CreateMCPPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/marketplace" element={<MarketplacePage />} />
      <Route path="/dashboard" element={<SellerDashboardPage />} />
      <Route path="/seller_dashboard.html" element={<SellerDashboardPage />} />
      <Route path="/create" element={<CreateMCPPage />} />
      <Route path="/newmcp.html" element={<CreateMCPPage />} />
    </Routes>
  )
}

export default App
