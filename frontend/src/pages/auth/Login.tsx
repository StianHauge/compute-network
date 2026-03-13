import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Zap, LogIn, Loader2 } from 'lucide-react';
import '../../index.css';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await fetch('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Login failed');
      }

      localStorage.setItem('averra_token', data.api_key);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'An error occurred during login');
    } finally {
      setIsLoading(false);
    }
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
        {error && (
          <div style={{ padding: '12px', borderRadius: '6px', background: 'rgba(255,50,50,0.1)', border: '1px solid rgba(255,50,50,0.3)', color: '#ff6b6b', fontSize: '14px', textAlign: 'center' }}>
            {error}
          </div>
        )}

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

          <button type="submit" disabled={isLoading} className="cta-button" style={{ marginTop: '8px', padding: '14px', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', width: '100%', opacity: isLoading ? 0.7 : 1, cursor: isLoading ? 'not-allowed' : 'pointer' }}>
            {isLoading ? <Loader2 size={18} className="animate-spin" /> : <LogIn size={18} />}
            {isLoading ? 'Initializing...' : 'Initialize Session'}
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
