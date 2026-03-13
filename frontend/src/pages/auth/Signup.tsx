import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Zap, UserPlus } from 'lucide-react';
import '../../index.css';

export default function Signup() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSignup = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement actual signup logic with backend
    console.log("Mock signup attempt for:", email);
    // On success, redirect to login or dashboard:
    // navigate('/login');
  };

  return (
    <div className="landing-container" style={{ backgroundColor: 'var(--bg-main)', minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', position: 'relative', overflow: 'hidden' }}>
      
      {/* Background flare */}
      <div style={{ position: 'absolute', top: '0', right: '0', width: '500px', height: '500px', background: 'radial-gradient(circle, rgba(180, 0, 255, 0.05) 0%, rgba(10, 10, 10, 0) 70%)', zIndex: 0, pointerEvents: 'none' }}></div>

      <Link to="/" style={{ position: 'absolute', top: '24px', left: '48px', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '8px', zIndex: 1 }}>
        <Zap size={24} color="var(--brand-cyan)" />
        <span style={{ fontSize: '18px', color: 'var(--text-primary)', fontWeight: '600' }}>Averra</span>
      </Link>

      <div className="glass-panel" style={{ padding: '48px', width: '100%', maxWidth: '400px', display: 'flex', flexDirection: 'column', gap: '24px', zIndex: 1, borderColor: 'rgba(0, 255, 204, 0.15)' }}>
        <div style={{ textAlign: 'center', marginBottom: '12px' }}>
          <h2 style={{ fontSize: '24px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '8px' }}>Deploy to Averra</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>Get your API key and claim your 50k free credits.</p>
        </div>

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

          <button type="submit" className="cta-button" style={{ marginTop: '8px', padding: '14px', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', width: '100%', background: 'linear-gradient(90deg, rgba(0,255,204,0.1) 0%, rgba(180,0,255,0.1) 100%)', borderColor: 'var(--brand-purple)' }}>
            <UserPlus size={18} color="var(--brand-cyan)"/>
            Generate API Key
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
