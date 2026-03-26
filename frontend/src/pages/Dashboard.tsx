import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Server, Zap, CreditCard, ShieldAlert, LogOut, TerminalSquare, Copy, BarChart3, HardDrive } from 'lucide-react';
import '../index.css';
import logo from '../assets/logo.png';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<'developer' | 'infrastructure' | 'vault'>('developer');
  const [stakedAvr, setStakedAvr] = useState(15000);
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem("averra_token");
      if (!token) {
        navigate("/login");
        return;
      }
      try {
        const response = await fetch("/api/developer/dashboard", {
          headers: { "Authorization": `Bearer ${token}` }
        });
        if (!response.ok) throw new Error("Auth failed");
        setDashboardData(await response.json());
      } catch (e) {
        localStorage.removeItem("averra_token");
        navigate("/login");
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
    const intervalId = setInterval(fetchData, 3000);
    return () => clearInterval(intervalId);
  }, [navigate]);

  if (isLoading) return <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'var(--bg-base)', color: 'white' }}><div className="animate-spin"><Server /></div></div>;

  const totalEarned = dashboardData?.nodes?.reduce((acc: number, n: any) => acc + n.earned, 0) || 0;

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
          <button onClick={() => { localStorage.removeItem("averra_token"); navigate("/login"); }} style={{ color: 'var(--text-secondary)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '8px', background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'inherit', fontSize: '16px' }} className="hover-red">
            <LogOut size={16} /> Disconnect
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        
        {/* Sidebar Navigation */}
        <aside style={{ width: '250px', borderRight: '1px solid var(--border-subtle)', padding: '24px 0', display: 'flex', flexDirection: 'column', gap: '8px', backgroundColor: 'var(--bg-surface)' }}>
          <button 
            onClick={() => setActiveTab('developer')}
            style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 24px', background: activeTab === 'developer' ? 'rgba(47, 230, 211, 0.05)' : 'transparent', borderLeft: activeTab === 'developer' ? '3px solid var(--accent-primary)' : '3px solid transparent', color: activeTab === 'developer' ? 'var(--text-primary)' : 'var(--text-secondary)', transition: 'all 0.2s', width: '100%', textAlign: 'left', borderTop: 'none', borderRight: 'none', borderBottom: 'none', cursor: 'pointer' }}
          >
            <TerminalSquare size={18} color={activeTab === 'developer' ? 'var(--accent-primary)' : 'var(--text-secondary)'} />
            The Developer Nexus
          </button>
          
          <button 
            onClick={() => setActiveTab('infrastructure')}
            style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 24px', background: activeTab === 'infrastructure' ? 'rgba(47, 230, 211, 0.05)' : 'transparent', borderLeft: activeTab === 'infrastructure' ? '3px solid var(--accent-primary)' : '3px solid transparent', color: activeTab === 'infrastructure' ? 'var(--text-primary)' : 'var(--text-secondary)', transition: 'all 0.2s', width: '100%', textAlign: 'left', borderTop: 'none', borderRight: 'none', borderBottom: 'none', cursor: 'pointer' }}
          >
            <Server size={18} color={activeTab === 'infrastructure' ? 'var(--accent-primary)' : 'var(--text-secondary)'} />
            Infrastructure Grid
          </button>
          
          <button 
            onClick={() => setActiveTab('vault')}
            style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 24px', background: activeTab === 'vault' ? 'rgba(124, 108, 255, 0.08)' : 'transparent', borderLeft: activeTab === 'vault' ? '3px solid var(--accent-secondary)' : '3px solid transparent', color: activeTab === 'vault' ? 'var(--text-primary)' : 'var(--text-secondary)', transition: 'all 0.2s', width: '100%', textAlign: 'left', borderTop: 'none', borderRight: 'none', borderBottom: 'none', cursor: 'pointer' }}
          >
            <ShieldAlert size={18} color={activeTab === 'vault' ? 'var(--accent-secondary)' : 'var(--text-secondary)'} />
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
                    {dashboardData?.compute_credits?.toLocaleString()} <span style={{ fontSize: '16px', color: 'var(--text-secondary)', fontWeight: 'normal' }}>CRD</span>
                  </div>
                  <button className="cta-button" style={{ width: '100%', display: 'flex', justifyContent: 'center' }}>Top Up via Stripe</button>
                </div>

                <div className="glass-panel" style={{ padding: '24px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', color: 'var(--text-secondary)' }}>
                    <Zap size={16} /> Developer API Key
                  </div>
                  <div className="mono" style={{ backgroundColor: 'rgba(0,0,0,0.5)', padding: '16px', borderRadius: '6px', fontSize: '14px', border: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <span>{dashboardData?.api_key}</span>
                    <Copy size={16} style={{ cursor: 'pointer', color: 'var(--text-secondary)' }} onClick={() => navigator.clipboard.writeText(dashboardData?.api_key)} />
                  </div>
                  <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Use this key in Authorization Headers to pay for API inferences.</p>
                </div>
                
                <div className="glass-panel" style={{ padding: '24px', gridColumn: 'span 2' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', color: 'var(--accent-secondary)' }}>
                    <HardDrive size={16} /> Node Link Key
                  </div>
                  <div className="mono" style={{ backgroundColor: 'rgba(124, 108, 255, 0.1)', padding: '16px', borderRadius: '6px', fontSize: '14px', border: '1px solid rgba(124, 108, 255, 0.3)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', color: 'white' }}>
                    <span>{dashboardData?.node_link_key}</span>
                    <Copy size={16} style={{ cursor: 'pointer', color: 'white' }} onClick={() => navigator.clipboard.writeText(dashboardData?.node_link_key)} />
                  </div>
                  <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Paste this Node Link Key directly into your local Averra Node App settings to link your hardware. Do not share this key.</p>
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
                  <h2 style={{ fontSize: '24px', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '12px' }}><Server size={24} color="var(--accent-primary)"/> Infrastructure Grid</h2>
                  <p style={{ color: 'var(--text-secondary)' }}>Monitor your active hardware fleet and earnings.</p>
                </div>
                <div className="glass-panel" style={{ padding: '12px 24px', display: 'flex', alignItems: 'center', gap: '16px' }}>
                   <div style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>TOTAL EARNED</div>
                   <div style={{ color: 'var(--status-warning)', fontSize: '24px', fontWeight: 'bold' }}>{totalEarned.toFixed(3)} <span style={{fontSize: '14px'}}>$AVR</span></div>
                </div>
              </div>

              <div className="glass-panel" style={{ padding: '2px', overflow: 'hidden', position: 'relative', height: '300px' }}>
                {/* Mock Map Background */}
                <div style={{ width: '100%', height: '100%', background: 'radial-gradient(circle at center, rgba(47, 230, 211, 0.05) 0%, rgba(11, 16, 32, 1) 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--border-subtle)', fontSize: '12px', letterSpacing: '4px' }}>
                  GLOBAL ROUTING MAP
                </div>
                {/* Mock Pips */}
                <div style={{ position: 'absolute', top: '40%', left: '55%', width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--accent-primary)', boxShadow: '0 0 10px var(--accent-primary)' }}></div>
                <div style={{ position: 'absolute', top: '35%', left: '48%', width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--accent-secondary)', boxShadow: '0 0 10px var(--accent-secondary)' }}></div>
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
                    {dashboardData?.nodes?.length === 0 ? (
                      <tr>
                        <td colSpan={6} style={{ textAlign: 'center', padding: '48px', color: 'var(--text-secondary)' }}>
                          No Nodes Linked. Enter your <strong style={{color:'var(--brand-purple)'}}>Node Link Key</strong> into the Desktop App to connect hardware.
                        </td>
                      </tr>
                    ) : dashboardData?.nodes?.map((n: any) => (
                      <tr key={n.id}>
                        <td className="mono" style={{ fontSize: '12px' }}>{n.id.substring(0,8)}</td>
                        <td className="mono">{n.model}</td>
                        <td>{n.location}</td>
                        <td>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <span className={`status-dot ${n.status === 'ONLINE' ? 'online' : n.status === 'SUPERPOSITION' ? 'superposition' : 'thermal'}`} style={{ backgroundColor: n.status === 'SUPERPOSITION' ? 'var(--brand-purple)' : n.status === 'THERMAL' ? '#ff4444' : ''}}></span>
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
          {activeTab === 'vault' && (             <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '32px', maxWidth: '800px', margin: '0 auto' }}>
               <div style={{ textAlign: 'center', marginBottom: '24px' }}>
                  <ShieldAlert size={48} color="var(--accent-secondary)" style={{ marginBottom: '16px' }} />
                  <h2 style={{ fontSize: '32px', marginBottom: '8px' }}>The Staking Vault</h2>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '16px' }}>Lock $AVR to increase your TPL multiplier and secure the network.</p>
               </div>

               <div className="glass-panel" style={{ padding: '48px', borderColor: 'rgba(124, 108, 255, 0.2)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>Currently Staked</span>
                    <span className="mono" style={{ fontSize: '24px', color: 'var(--status-warning)', fontWeight: 'bold' }}>{stakedAvr.toLocaleString()} $AVR</span>
                  </div>

                  <input 
                    type="range" 
                    min="0" 
                    max="100000" 
                    step="1000" 
                    value={stakedAvr} 
                    onChange={(e) => setStakedAvr(Number(e.target.value))}
                    style={{ width: '100%', marginBottom: '32px', accentColor: 'var(--accent-secondary)' }}
                  />

                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '16px', backgroundColor: 'var(--bg-panel)', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                    <div>
                      <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Current Routing Tier</div>
                      <div style={{ color: stakedAvr >= 50000 ? 'var(--accent-primary)' : 'var(--text-primary)', fontWeight: 'bold' }}>
                        {stakedAvr >= 50000 ? 'Enterprise Routing (Tier 1)' : 'Standard Routing (Tier 2)'}
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>TPL Multiplier</div>
                      <div className="mono" style={{ color: 'var(--accent-secondary)', fontWeight: 'bold' }}>
                        x{(1.0 + (stakedAvr / 100000)).toFixed(2)}
                      </div>
                    </div>
                  </div>

                  <button className="cta-button" style={{ width: '100%', marginTop: '24px', background: 'linear-gradient(90deg, rgba(124,108,255,0.1) 0%, transparent 100%)', borderColor: 'var(--accent-secondary)' }}>
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
