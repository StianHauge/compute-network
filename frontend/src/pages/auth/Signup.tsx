import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { UserPlus, Loader2 } from 'lucide-react';
import '../../index.css';
import logo from '../../assets/logo.png';

export default function Signup() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await fetch('/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Signup failed');
      }

      localStorage.setItem('averra_token', data.api_key);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'An error occurred during signup');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="landing-container" style={{ backgroundColor: 'var(--bg-main)', minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', position: 'relative', overflow: 'hidden' }}>
      
      {/* Background flare */}
      <div style={{ position: 'absolute', top: '0', right: '0', width: '500px', height: '500px', background: 'radial-gradient(circle, rgba(180, 0, 255, 0.05) 0%, rgba(10, 10, 10, 0) 70%)', zIndex: 0, pointerEvents: 'none' }}></div>

      <Link to="/" style={{ position: 'absolute', top: '24px', left: '48px', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '8px', zIndex: 1 }}>
        <img src={logo} alt="Averra Logo" style={{ width: '24px', height: '24px' }} />
        <span style={{ fontSize: '18px', color: 'var(--text-primary)', fontWeight: '600' }}>Averra</span>
      </Link>

      <div className="glass-panel" style={{ padding: '48px', width: '100%', maxWidth: '400px', display: 'flex', flexDirection: 'column', gap: '24px', zIndex: 1, borderColor: 'rgba(0, 255, 204, 0.15)' }}>
        <div style={{ textAlign: 'center', marginBottom: '12px' }}>
          <h2 style={{ fontSize: '24px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '8px' }}>Deploy to Averra</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>Get your API key and claim your 50k free credits.</p>
        </div>
        {error && (
          <div style={{ padding: '12px', borderRadius: '6px', background: 'rgba(255,50,50,0.1)', border: '1px solid rgba(255,50,50,0.3)', color: '#ff6b6b', fontSize: '14px', textAlign: 'center' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSignup} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
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

          <button type="submit" disabled={isLoading} className="cta-button" style={{ marginTop: '8px', padding: '14px', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', width: '100%', background: 'linear-gradient(90deg, rgba(0,255,204,0.1) 0%, rgba(180,0,255,0.1) 100%)', borderColor: 'var(--brand-purple)', opacity: isLoading ? 0.7 : 1, cursor: isLoading ? 'not-allowed' : 'pointer' }}>
            {isLoading ? <Loader2 size={18} className="animate-spin" color="var(--brand-cyan)"/> : <UserPlus size={18} color="var(--brand-cyan)"/>}
            {isLoading ? 'Generating Key...' : 'Generate API Key'}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '8px' }}>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
            Already have a key? <Link to="/login" style={{ color: 'var(--brand-cyan)', textDecoration: 'none' }}>Initialize Session</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
