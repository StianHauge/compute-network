import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Zap, LogIn } from 'lucide-react';
import '../../index.css';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement actual login logic with backend
    console.log("Mock login attempt for:", email);
    // On success, redirect to dashboard:
    // navigate('/dashboard');
  };

  return (
    <div className="landing-container" style={{ backgroundColor: 'var(--bg-main)', minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      
      <Link to="/" style={{ position: 'absolute', top: '24px', left: '48px', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Zap size={24} color="var(--brand-cyan)" />
        <span style={{ fontSize: '18px', color: 'var(--text-primary)', fontWeight: '600' }}>Averra</span>
      </Link>

      <div className="glass-panel" style={{ padding: '48px', width: '100%', maxWidth: '400px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
        <div style={{ textAlign: 'center', marginBottom: '12px' }}>
          <h2 style={{ fontSize: '24px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '8px' }}>Sign in to Averra</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>Welcome back to the Command Center.</p>
        </div>

        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: '500', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Email</label>
            <input 
              type="email" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="glass-input"
              style={{ padding: '12px 16px', borderRadius: '6px', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border-subtle)', color: 'white', fontSize: '14px', outline: 'none' }}
              placeholder="developer@example.com"
              required
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: '500', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Password</label>
            <input 
              type="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="glass-input"
              style={{ padding: '12px 16px', borderRadius: '6px', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border-subtle)', color: 'white', fontSize: '14px', outline: 'none' }}
              placeholder="••••••••"
              required
            />
          </div>

          <button type="submit" className="cta-button" style={{ marginTop: '8px', padding: '14px', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', width: '100%' }}>
            <LogIn size={18} />
            Initialize Session
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '8px' }}>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
            Don't have an account? <Link to="/signup" style={{ color: 'var(--brand-cyan)', textDecoration: 'none' }}>Get an API Key</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
