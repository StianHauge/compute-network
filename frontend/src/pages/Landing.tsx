import { Link } from 'react-router-dom';
import { Terminal, Zap } from 'lucide-react';
import '../index.css';
import logo from '../assets/logo.png';

export default function Landing() {
  return (
    <div className="landing-container fade-in" style={{ backgroundColor: 'var(--bg-base)', minHeight: '100vh', color: 'var(--text-primary)', display: 'flex', flexDirection: 'column' }}>
      
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
        <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', width: '600px', height: '600px', background: 'radial-gradient(circle, rgba(47, 230, 211, 0.05) 0%, rgba(10, 10, 10, 0) 70%)', zIndex: 0, pointerEvents: 'none' }}></div>

        <div style={{ zIndex: 1, maxWidth: '900px' }}>
          <h2 style={{ fontSize: '64px', fontWeight: 800, marginBottom: '24px', lineHeight: 1.1, letterSpacing: '-0.02em', marginTop: '64px' }}>
            High-Assurance <br />
            <span style={{ color: 'var(--accent-primary)', textShadow: '0 0 30px rgba(47,230,211,0.3)' }}>Zero-Trust AI Compute</span>
          </h2>
          
          <p style={{ fontSize: '20px', color: 'var(--text-secondary)', marginBottom: '48px', lineHeight: 1.6, maxWidth: '700px', margin: '0 auto 48px auto' }}>
            Run AI workloads across distributed GPU capacity with signed execution, attested nodes, and hardened runtime isolation. <br/>
            <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>Attested Hardware. Signed Policy. Absolute Isolation.</span>
          </p>

          {/* Value Prop Columns - 2x2 Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px', textAlign: 'left', marginBottom: '64px' }}>
            
            {/* Card 1 - Cryptographic Execution Contracts */}
            <div className="glass-panel" style={{ padding: '32px', position: 'relative' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
                <Terminal size={20} color="var(--accent-primary)" />
                <h3 style={{ fontSize: '18px', margin: 0 }}>Signed Execution Contracts</h3>
              </div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '24px' }}>
                Dispatch is no longer "best effort." Every workload is bound to an ed25519-signed policy enforcing strict memory, schema, and tier requirements. Sentinel nodes accept nothing else.
              </p>
              
              <div className="mono" style={{ backgroundColor: 'rgba(0,0,0,0.5)', padding: '16px', borderRadius: '8px', fontSize: '13px', color: '#a0a0a0', border: '1px solid var(--border-subtle)' }}>
                <div style={{ color: '#ff6b6b', marginBottom: '8px' }}>
                  contract = KMS.sign(payload)
                </div>
                <div style={{ color: 'var(--accent-primary)' }}>
                  node.verify_signature(contract)
                </div>
              </div>
            </div>

            {/* Card 2 - Hardware Rooted Attestation */}
            <div className="glass-panel" style={{ padding: '32px', borderColor: 'rgba(124, 108, 255, 0.2)', display: 'flex', flexDirection: 'column' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
                <Zap size={20} color="var(--accent-secondary)" />
                <h3 style={{ fontSize: '18px', margin: 0 }}>Hardware-Rooted Attestation</h3>
              </div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '24px', flex: 1 }}>
                The Scheduler only signs policy. The active Key Management Service (KMS) exclusively releases workload secrets when a node mathematically proves its TPM/TDX state via short-lived tokens.
              </p>
              
              <div className="mono" style={{ backgroundColor: 'rgba(0,0,0,0.5)', padding: '16px', borderRadius: '8px', fontSize: '13px', color: '#e0e0e0', border: '1px solid rgba(124, 108, 255, 0.2)' }}>
                <span style={{ color: 'var(--accent-secondary)' }}>Status: </span>
                Awaiting Attestation Token...
              </div>
            </div>

            {/* Card 3 - VSOCK Firewall */}
            <div className="glass-panel" style={{ padding: '32px', borderColor: 'rgba(124, 108, 255, 0.2)', display: 'flex', flexDirection: 'column' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
                <Terminal size={20} color="var(--accent-secondary)" />
                <h3 style={{ fontSize: '18px', margin: 0 }}>Hostile-Resistant Sandboxing</h3>
              </div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '24px', flex: 1 }}>
                Workloads run in ephemeral microVMs guarded by a strictly-typed VSOCK proxy. A single schema mismatch, oversize frame, or sequence anomaly instantly terminates the execution.
              </p>
            </div>

            {/* Card 4 - Rust Sentinel Node Agent */}
            <div className="glass-panel" style={{ padding: '32px', borderColor: 'rgba(124, 108, 255, 0.2)', display: 'flex', flexDirection: 'column' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
                <Zap size={20} color="var(--accent-secondary)" />
                <h3 style={{ fontSize: '18px', margin: 0 }}>The Rust Sentinel</h3>
              </div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '24px', flex: 1 }}>
                Provide capacity to the mesh natively. Sentinel is fully fail-closed, supporting Tiered Isolation limits from casual Open Inference up to secured PCIe passthrough with strict VRAM resets.
              </p>
              
              <div style={{ display: 'flex', gap: '12px' }}>
                  <a href="/downloads/Averra-Node-v2.0.0.dmg" className="cta-button" style={{ flex: 1, backgroundColor: 'rgba(255,255,255,0.05)', borderColor: 'var(--border-subtle)', color: 'var(--text-primary)', padding: '10px', fontSize: '13px', justifyContent: 'center', textDecoration: 'none', display: 'flex', textAlign: 'center' }}>
                     macOS (.dmg)
                  </a>
                  <a href="/downloads/Averra-Node-v2.0.0.exe" className="cta-button" style={{ flex: 1, backgroundColor: 'rgba(255,255,255,0.05)', borderColor: 'var(--border-subtle)', color: 'var(--text-primary)', padding: '10px', fontSize: '13px', justifyContent: 'center', textDecoration: 'none', display: 'flex', textAlign: 'center' }}>
                     Windows (.exe)
                  </a>
              </div>
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
              "Averra turns untrusted global GPU capacity into a cryptographically verified execution mesh."
          </div>
          <div className="footer-copyright">
              © 2026 Averra Network. Built for the decentralized future.
          </div>
      </footer>
    </div>
  );
}
