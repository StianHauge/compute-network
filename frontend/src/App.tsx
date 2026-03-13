import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Landing from './pages/Landing';
import NetworkExplorer from './pages/NetworkExplorer';
import Login from './pages/auth/Login';
import Signup from './pages/auth/Signup';
import Dashboard from './pages/Dashboard';

import './index.css';

function App() {
  // A simple placeholder for auth state. You might use context or a store here later.
  const isAuthenticated = false; // Replace with actual auth check later

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/network" element={<NetworkExplorer />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        
        {/* Protected Dashboard Route */}
        <Route 
          path="/dashboard" 
          element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" replace />} 
        />
      </Routes>
    </Router>
  );
}

export default App;
