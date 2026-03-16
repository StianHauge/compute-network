import { Link } from 'react-router-dom';
import { Terminal, Zap } from 'lucide-react';
import '../index.css';
import logo from '../assets/logo.png';

export default function Landing() {
  return (
    <div className="landing-container" style={{ backgroundColor: 'var(--bg-main)', minHeight: '100vh', color: 'var(--text-primary)', display: 'flex', flexDirection: 'column' }}>
      
      {/* Top Navigation */}
      <nav style={{ display: 'flex', justifyContent: 'space-between', padding: '24px 48px', alignItems: 'center', borderBottom: '1px solid var(--border-subtle)' }}>
        <div className="header-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <img src={logo} alt="Averra Logo" style={{ width: '28px', height: '28px' }} />
          <h1 style={{ fontSize: '20px', margin: 0 }}>Averra</h1>
        </div>
        <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
          <Link to="/network" style={{ color: 'var(--text-secondary)', textDecoration: 'none', transition: 'color 0.2s' }} className="hover-cyan">Network Explorer</Link>
          <Link to="/login" style={{ color: 'var(--text-primary)', textDecoration: 'none' }} className="hover-cyan">Log in</Link>
          <Link to="/signup" className="cta-button" style={{ textDecoration: 'none' }}>Get API Key</Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '0 24px', textAlign: 'center', position: 'relative', overflow: 'hidden' }}>
        
        {/* Subtle background pulse effect */}
        <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', width: '600px', height: '600px', background: 'radial-gradient(circle, rgba(0, 255, 204, 0.05) 0%, rgba(10, 10, 10, 0) 70%)', zIndex: 0, pointerEvents: 'none' }}></div>

        <div style={{ zIndex: 1, maxWidth: '800px' }}>
          <h2 style={{ fontSize: '64px', fontWeight: 800, marginBottom: '24px', lineHeight: 1.1, letterSpacing: '-0.02em' }}>
            Switch from centralized <br />
            <span style={{ color: 'var(--brand-cyan)', textShadow: '0 0 30px rgba(0,255,204,0.3)' }}>AI inference</span> in two lines of code
          </h2>
          
          <p style={{ fontSize: '20px', color: 'var(--text-secondary)', marginBottom: '48px', lineHeight: 1.6, maxWidth: '600px', margin: '0 auto 48px auto' }}>
            Averra brings state-aware orchestration to fragmented GPU supply, turning it into one reliable API for open-source model inference. <br/>
            <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>Lower cost. Tiered Reliability. OpenAI-compatible.</span>
          </p>

          {/* Value Prop Columns - 2x2 Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px', textAlign: 'left', marginBottom: '64px' }}>
            
            {/* Developer Card - Top Left */}
            <div className="glass-panel" style={{ padding: '32px', position: 'relative' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
                <Terminal size={20} color="var(--brand-cyan)" />
                <h3 style={{ fontSize: '18px', margin: 0 }}>State-Aware Orchestration</h3>
              </div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '24px' }}>
                Low-latency inference routed across a fault-tolerant global GPU mesh. Background model warm-swapping eliminates cold starts.
              </p>
              
              <div className="mono" style={{ backgroundColor: 'rgba(0,0,0,0.5)', padding: '16px', borderRadius: '8px', fontSize: '13px', color: '#a0a0a0', border: '1px solid var(--border-subtle)' }}>
                <div style={{ color: '#ff6b6b', textDecoration: 'line-through', marginBottom: '8px' }}>
                  base_url = "https://api.openai.com/v1"
                </div>
                <div style={{ color: 'var(--brand-cyan)' }}>
                  base_url = "https://api.averra.network/v1"
                </div>
              </div>
            </div>

            {/* Provider Card: Linux - Top Right */}
            <div className="glass-panel" style={{ padding: '32px', borderColor: 'rgba(180, 0, 255, 0.2)', display: 'flex', flexDirection: 'column' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
                <Zap size={20} color="var(--brand-purple)" />
                <h3 style={{ fontSize: '18px', margin: 0 }}>Tiered Reliability Routing</h3>
              </div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '24px', flex: 1 }}>
                Choose "Best Effort" for cost-savings or "Consensus Routing" with 3x redundancy for enterprise SLAs. OpenAI-compatible drop-in replacement.
              </p>
              
              <div className="mono" style={{ backgroundColor: 'rgba(0,0,0,0.5)', padding: '16px', borderRadius: '8px', fontSize: '13px', color: '#e0e0e0', border: '1px solid rgba(180, 0, 255, 0.2)' }}>
                <span style={{ color: 'var(--brand-purple)' }}>~ </span>
                curl -sSL https://install.averra.network | sh -s -- --token YOUR_KEY
              </div>
            </div>

            {/* Provider Card: macOS - Bottom Left */}
            <div className="glass-panel" style={{ padding: '32px', borderColor: 'rgba(180, 0, 255, 0.2)', display: 'flex', flexDirection: 'column' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
                <Zap size={20} color="var(--brand-purple)" />
                <h3 style={{ fontSize: '18px', margin: 0 }}>Node Operator: macOS & Linux</h3>
              </div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '24px', flex: 1 }}>
                Provide unified memory inference capacity to the mesh for SLMs/MLMs. Automated payouts and background settlement require zero configuration.
              </p>
              
              <a href="/downloads/Averra-Node-Installer-v1.0.1.dmg" download className="cta-button" style={{ width: '100%', backgroundColor: 'rgba(255,255,255,0.05)', borderColor: 'var(--brand-purple)', color: 'var(--text-primary)', padding: '14px 16px', fontSize: '14px', justifyContent: 'center', textDecoration: 'none', display: 'flex' }}>
                 Download for macOS (.dmg)
              </a>
            </div>

            {/* Provider Card: Windows - Bottom Right */}
            <div className="glass-panel" style={{ padding: '32px', borderColor: 'rgba(180, 0, 255, 0.2)', display: 'flex', flexDirection: 'column' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
                <Zap size={20} color="var(--brand-purple)" />
                <h3 style={{ fontSize: '18px', margin: 0 }}>Node Operator: Windows PC</h3>
              </div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '24px', flex: 1 }}>
                Connect your NVIDIA GPU with sufficient VRAM headroom. Our scheduler continuously scores node reliability, uptime, and execution quality.
              </p>
              
              <a href="/downloads/Averra-Node-Installer.exe" download className="cta-button" style={{ width: '100%', backgroundColor: 'rgba(255,255,255,0.05)', borderColor: 'var(--brand-purple)', color: 'var(--text-primary)', padding: '14px 16px', fontSize: '14px', justifyContent: 'center', textDecoration: 'none', display: 'flex' }}>
                 Download for Windows (.exe)
              </a>
            </div>

          </div>
        </div>
      </main>

      {/* The Founder's Footer */}
      <footer className="founder-footer" style={{ borderTop: '1px solid var(--border-subtle)' }}>
          <div className="footer-company">
              Averra Network is developed by Stian Hauge and Transisto AS.
          </div>
          <div className="footer-vision">
              "Averra is an inference orchestration layer that turns unreliable, distributed GPU capacity into a predictable API for developers."
          </div>
          <div className="footer-copyright">
              © 2026 Averra Network. Built for the decentralized future.
          </div>
      </footer>
    </div>
  );
}
