import { Link } from 'react-router-dom';
import { Server, Zap, CreditCard, ShieldAlert, LogOut, TerminalSquare, Copy, BarChart3 } from 'lucide-react';
import '../index.css';
import logo from '../assets/logo.png';

// --- Mock Data ---
const MOCK_CREDITS = 49250.5;
const MOCK_API_KEY = "AVR-************************3f9a";
const MOCK_NODES = [
  { id: "NODE-8F2A", model: "RTX 4090", location: "Oslo, NO", status: "ACTIVE", vram: 24.0, temp: 68.5, pcie: 28.4, earned: 14.250 },
  { id: "NODE-3B91", model: "A100", location: "Frankfurt, DE", status: "SUPERPOSITION", vram: 80.0, temp: 72.1, pcie: 56.2, earned: 105.400 },
  { id: "NODE-C744", model: "RTX 3090", location: "Austin, TX", status: "THERMAL", vram: 24.0, temp: 88.0, pcie: 14.1, earned: 8.920 }
];

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<'developer' | 'infrastructure' | 'vault'>('developer');
  const [stakedAvr, setStakedAvr] = useState(15000);

  return (
    <div className="dashboard-container" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      
      {/* Top Header */}
      <header className="header" style={{ padding: '16px 32px', borderBottom: '1px solid var(--border-subtle)' }}>
        <div className="header-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <img src={logo} alt="Averra Logo" style={{ width: '24px', height: '24px' }} />
          <h1 style={{ fontSize: '18px', margin: 0 }}>Averra <span className="mono" style={{ color: 'var(--text-secondary)' }}>// Command Center</span></h1>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
          <div className="mono" style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>SESSION_ID: 8a4b-9f2c</div>
          <Link to="/" style={{ color: 'var(--text-secondary)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '8px' }} className="hover-red">
            <LogOut size={16} /> Disconnect
          </Link>
        </div>
      </header>

      {/* Main Content Area */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        
        {/* Sidebar Navigation */}
        <aside style={{ width: '250px', borderRight: '1px solid var(--border-subtle)', padding: '24px 0', display: 'flex', flexDirection: 'column', gap: '8px', backgroundColor: 'rgba(10,10,10,0.5)' }}>
          <button 
            onClick={() => setActiveTab('developer')}
            style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 24px', background: activeTab === 'developer' ? 'rgba(0, 255, 204, 0.1)' : 'transparent', borderLeft: activeTab === 'developer' ? '3px solid var(--brand-cyan)' : '3px solid transparent', color: activeTab === 'developer' ? 'var(--text-primary)' : 'var(--text-secondary)', transition: 'all 0.2s', width: '100%', textAlign: 'left', borderTop: 'none', borderRight: 'none', borderBottom: 'none', cursor: 'pointer' }}
          >
            <TerminalSquare size={18} color={activeTab === 'developer' ? 'var(--brand-cyan)' : 'var(--text-secondary)'} />
            The Developer Nexus
          </button>
          
          <button 
            onClick={() => setActiveTab('infrastructure')}
            style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 24px', background: activeTab === 'infrastructure' ? 'rgba(0, 255, 204, 0.1)' : 'transparent', borderLeft: activeTab === 'infrastructure' ? '3px solid var(--brand-cyan)' : '3px solid transparent', color: activeTab === 'infrastructure' ? 'var(--text-primary)' : 'var(--text-secondary)', transition: 'all 0.2s', width: '100%', textAlign: 'left', borderTop: 'none', borderRight: 'none', borderBottom: 'none', cursor: 'pointer' }}
          >
            <Server size={18} color={activeTab === 'infrastructure' ? 'var(--brand-cyan)' : 'var(--text-secondary)'} />
            Infrastructure Grid
          </button>
          
          <button 
            onClick={() => setActiveTab('vault')}
            style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 24px', background: activeTab === 'vault' ? 'rgba(180, 0, 255, 0.1)' : 'transparent', borderLeft: activeTab === 'vault' ? '3px solid var(--brand-purple)' : '3px solid transparent', color: activeTab === 'vault' ? 'var(--text-primary)' : 'var(--text-secondary)', transition: 'all 0.2s', width: '100%', textAlign: 'left', borderTop: 'none', borderRight: 'none', borderBottom: 'none', cursor: 'pointer' }}
          >
            <ShieldAlert size={18} color={activeTab === 'vault' ? 'var(--brand-purple)' : 'var(--text-secondary)'} />
            The Staking Vault
          </button>
        </aside>

        {/* Tab Content */}
        <main style={{ flex: 1, padding: '48px', overflowY: 'auto' }}>
          
          {/* TAB 1: DEVELOPER NEXUS */}
          {activeTab === 'developer' && (
            <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '32px', maxWidth: '1000px', margin: '0 auto' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <h2 style={{ fontSize: '24px', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '12px' }}><TerminalSquare size={24} color="var(--brand-cyan)"/> Developer Nexus</h2>
                  <p style={{ color: 'var(--text-secondary)' }}>Manage your compute consumption and API credentials.</p>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
                <div className="glass-panel" style={{ padding: '24px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', color: 'var(--text-secondary)' }}>
                    <CreditCard size={16} /> Compute Credits
                  </div>
                  <div style={{ fontSize: '36px', fontWeight: 'bold', color: 'var(--text-primary)', marginBottom: '24px' }}>
                    {MOCK_CREDITS.toLocaleString()} <span style={{ fontSize: '16px', color: 'var(--text-secondary)', fontWeight: 'normal' }}>CRD</span>
                  </div>
                  <button className="cta-button" style={{ width: '100%', display: 'flex', justifyContent: 'center' }}>Top Up via Stripe</button>
                </div>

                <div className="glass-panel" style={{ padding: '24px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', color: 'var(--text-secondary)' }}>
                    <Zap size={16} /> Universal Remote (API / Node Key)
                  </div>
                  <div className="mono" style={{ backgroundColor: 'rgba(0,0,0,0.5)', padding: '16px', borderRadius: '6px', fontSize: '14px', border: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <span>{MOCK_API_KEY}</span>
                    <Copy size={16} style={{ cursor: 'pointer', color: 'var(--text-secondary)' }} />
                  </div>
                  <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Use this key for both OpenAI-compatible API requests and authenticating your Sentinel nodes.</p>
                </div>
              </div>

              <div className="glass-panel" style={{ padding: '24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '24px', color: 'var(--text-secondary)' }}>
                  <BarChart3 size={16} /> Usage Analytics (Last 30 Days)
                </div>
                <div style={{ height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px dashed var(--border-subtle)', borderRadius: '8px', color: 'var(--text-secondary)' }}>
                  [ Token Consumption Chart Placeholder ] <br/> Llama-3: 65% | Mistral: 35%
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: INFRASTRUCTURE GRID */}
          {activeTab === 'infrastructure' && (
            <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '32px', maxWidth: '1000px', margin: '0 auto' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <h2 style={{ fontSize: '24px', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '12px' }}><Server size={24} color="var(--brand-cyan)"/> Infrastructure Grid</h2>
                  <p style={{ color: 'var(--text-secondary)' }}>Monitor your active hardware fleet and earnings.</p>
                </div>
                <div className="glass-panel" style={{ padding: '12px 24px', display: 'flex', alignItems: 'center', gap: '16px' }}>
                   <div style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>TOTAL EARNED</div>
                   <div style={{ color: 'var(--brand-gold)', fontSize: '24px', fontWeight: 'bold' }}>128.570 <span style={{fontSize: '14px'}}>$AVR</span></div>
                </div>
              </div>

              <div className="glass-panel" style={{ padding: '2px', overflow: 'hidden', position: 'relative', height: '300px' }}>
                {/* Mock Map Background */}
                <div style={{ width: '100%', height: '100%', background: 'radial-gradient(circle at center, rgba(0, 255, 204, 0.05) 0%, rgba(0, 0, 0, 1) 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--border-subtle)', fontSize: '12px', letterSpacing: '4px' }}>
                  GLOBAL ROUTING MAP
                </div>
                {/* Mock Pips */}
                <div style={{ position: 'absolute', top: '40%', left: '55%', width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--brand-cyan)', boxShadow: '0 0 10px var(--brand-cyan)' }}></div>
                <div style={{ position: 'absolute', top: '35%', left: '48%', width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--brand-purple)', boxShadow: '0 0 10px var(--brand-purple)' }}></div>
                <div style={{ position: 'absolute', top: '50%', left: '20%', width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#ff4444', boxShadow: '0 0 10px #ff4444' }}></div>
              </div>

              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Node ID</th>
                      <th>Hardware</th>
                      <th>Location</th>
                      <th>Status</th>
                      <th>Telemetry</th>
                      <th style={{textAlign: 'right'}}>Earned</th>
                    </tr>
                  </thead>
                  <tbody>
                    {MOCK_NODES.map(n => (
                      <tr key={n.id}>
                        <td className="mono">{n.id}</td>
                        <td className="mono">{n.model}</td>
                        <td>{n.location}</td>
                        <td>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <span className={`status-dot ${n.status === 'ACTIVE' ? 'online' : n.status === 'SUPERPOSITION' ? 'superposition' : 'thermal'}`} style={{ backgroundColor: n.status === 'SUPERPOSITION' ? 'var(--brand-purple)' : n.status === 'THERMAL' ? '#ff4444' : ''}}></span>
                            <span style={{ fontSize: '10px', letterSpacing: '0.05em', color: n.status === 'THERMAL' ? '#ff4444' : 'var(--text-secondary)'}}>{n.status}</span>
                          </div>
                        </td>
                        <td>
                           <div style={{ display: 'flex', gap: '12px', fontSize: '12px', color: 'var(--text-secondary)' }} className="mono">
                              <span>VRAM: {n.vram}G</span>
                              <span style={{ color: n.temp > 80 ? '#ff4444' : 'inherit' }}>{n.temp}°C</span>
                              <span>{n.pcie}GB/s</span>
                           </div>
                        </td>
                        <td className="mono" style={{ textAlign: 'right', color: 'var(--brand-gold)' }}>+{n.earned.toFixed(3)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 3: THE STAKING VAULT */}
          {activeTab === 'vault' && (
            <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '32px', maxWidth: '800px', margin: '0 auto' }}>
               <div style={{ textAlign: 'center', marginBottom: '24px' }}>
                  <ShieldAlert size={48} color="var(--brand-purple)" style={{ marginBottom: '16px' }} />
                  <h2 style={{ fontSize: '32px', marginBottom: '8px' }}>The Staking Vault</h2>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '16px' }}>Lock $AVR to increase your TPL $S_bonus$ multiplier and secure the network.</p>
               </div>

               <div className="glass-panel" style={{ padding: '48px', borderColor: 'rgba(180, 0, 255, 0.2)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>Currently Staked</span>
                    <span className="mono" style={{ fontSize: '24px', color: 'var(--brand-gold)', fontWeight: 'bold' }}>{stakedAvr.toLocaleString()} $AVR</span>
                  </div>

                  <input 
                    type="range" 
                    min="0" 
                    max="100000" 
                    step="1000" 
                    value={stakedAvr} 
                    onChange={(e) => setStakedAvr(Number(e.target.value))}
                    style={{ width: '100%', marginBottom: '32px', accentColor: 'var(--brand-purple)' }}
                  />

                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '16px', backgroundColor: 'rgba(0,0,0,0.5)', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                    <div>
                      <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Current Routing Tier</div>
                      <div style={{ color: stakedAvr >= 50000 ? 'var(--brand-cyan)' : 'var(--text-primary)', fontWeight: 'bold' }}>
                        {stakedAvr >= 50000 ? 'Enterprise Routing (Tier 1)' : 'Standard Routing (Tier 2)'}
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>TPL Multiplier</div>
                      <div className="mono" style={{ color: 'var(--brand-purple)', fontWeight: 'bold' }}>
                        x{(1.0 + (stakedAvr / 100000)).toFixed(2)}
                      </div>
                    </div>
                  </div>

                  <button className="cta-button" style={{ width: '100%', marginTop: '24px', background: 'linear-gradient(90deg, rgba(180,0,255,0.2) 0%, transparent 100%)', borderColor: 'var(--brand-purple)' }}>
                    Commit Stake
                  </button>
               </div>
            </div>
          )}

        </main>
      </div>
    </div>
  );
}
