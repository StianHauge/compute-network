import { useEffect, useState } from 'react';
import { Activity, Server, Cpu, Zap, CreditCard, Coins, ShieldAlert } from 'lucide-react';
import '../index.css';
import logo from '../assets/logo.png';

// --- Types ---
interface NetworkStats {
  nodes_online: number;
  nodes_superposition: number;
  total_vram_gb: number;
  global_avg_ping_ms: number;
  timestamp: string;
}

interface NodeLive {
  id_short: string;
  status: string;
  vram_free: number;
  temperature_c: number;
  pcie_bw: number;
  earned_avr: number;
  location: string;
}

interface MockLedger {
  consumers: { email: string; credits: number }[];
  providers: { id: string; earned_avr: number; staked: number }[];
}

function NetworkExplorer() {
  const [stats, setStats] = useState<NetworkStats | null>(null);
  const [nodes, setNodes] = useState<NodeLive[]>([]);
  const [ledger, setLedger] = useState<MockLedger | null>(null);

  // --- Real-time Polling Engine ---
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, nodesRes, ledgerRes] = await Promise.all([
          fetch('/api/network/stats'),
          fetch('/api/nodes/live'),
          fetch('/api/economy/mock-ledger')
        ]);
        
        if (statsRes.ok) setStats(await statsRes.json());
        if (nodesRes.ok) setNodes(await nodesRes.json());
        if (ledgerRes.ok) setLedger(await ledgerRes.json());
      } catch (err) {
        console.error("Dashboard Polling Error", err);
      }
    };

    fetchData(); // Initial load
    const interval = setInterval(fetchData, 2000); // 2-second heartbeat
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="header">
        <div className="header-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <img src={logo} alt="Averra Logo" style={{ width: '32px', height: '32px' }} />
          <h1>Averra <span>// Control Plane</span></h1>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)', cursor: 'help' }} title="Phase 4.4: Centralized Beta">
            <span className="status-dot online"></span>
            <span className="mono" style={{ fontSize: '12px' }}>V2.1 GLOBALLY ROUTED</span>
          </div>
          <button className="cta-button">
            <Server size={16} /> 
            Connect Node
          </button>
        </div>
      </header>

      {/* Global Mission Control KPI Grid */}
      <section className="glass-panel kpi-grid">
        <div className="kpi-card">
          <div className="kpi-title" style={{display: 'flex', gap:'8px', alignItems:'center'}}>
            <Server size={16} /> Nodes Online
          </div>
          <div className="kpi-value cyan">{stats?.nodes_online || 0}</div>
        </div>
        
        <div className="kpi-card">
          <div className="kpi-title" style={{display: 'flex', gap:'8px', alignItems:'center'}}>
            <Zap size={16} /> Warm-Swap Ready
          </div>
          <div className="kpi-value purple">{stats?.nodes_superposition || 0}</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-title" style={{display: 'flex', gap:'8px', alignItems:'center'}}>
            <Cpu size={16} /> Global VRAM Pool
          </div>
          <div className="kpi-value" style={{color: '#fff'}}>
            {stats?.total_vram_gb.toLocaleString() || 0} <span style={{fontSize: '16px', color: 'var(--text-secondary)'}}>GB</span>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-title" style={{display: 'flex', gap:'8px', alignItems:'center'}}>
            <Activity size={16} /> TPL Latency (Ping + Jitter)
          </div>
          <div className="kpi-value" style={{color: '#fff'}}>
            {stats?.global_avg_ping_ms.toFixed(1) || 0} <span style={{fontSize: '16px', color: 'var(--text-secondary)'}}>ms</span>
          </div>
        </div>
      </section>

      {/* The Economy Ledger */}
      <section className="ledger-grid">
        <div className="glass-panel">
          <div className="header-title" style={{marginBottom: '16px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '12px'}}>
            <CreditCard size={20} color="var(--text-primary)" />
            <h2 style={{fontSize: '16px', color: 'var(--text-primary)'}}>Enterprise Fiat (Compute Credits)</h2>
          </div>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Developer / Enterprise</th>
                  <th style={{textAlign: 'right'}}>Live Balance</th>
                </tr>
              </thead>
              <tbody>
                {ledger?.consumers.map((c, i) => (
                  <tr key={i}>
                    <td className="mono">{c.email}</td>
                    <td className="mono" style={{textAlign: 'right', color: '#fff'}}>{c.credits.toLocaleString(undefined, {minimumFractionDigits: 1, maximumFractionDigits:1})}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="glass-panel">
          <div className="header-title" style={{marginBottom: '16px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '12px', justifyContent: 'space-between'}}>
             <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                 <Coins size={20} color="var(--brand-gold)" />
                 <h2 style={{fontSize: '16px', color: 'var(--text-primary)'}}>Provider Node Incomes ($AVR)</h2>
             </div>
             <div title="Protected by Automated Quality Control">
                <ShieldAlert size={16} color="var(--text-secondary)" />
             </div>
          </div>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Node ID</th>
                  <th style={{textAlign: 'right'}}>Staked Collateral</th>
                  <th style={{textAlign: 'right'}}>Pending Payout</th>
                </tr>
              </thead>
              <tbody>
                {ledger?.providers.map((p, i) => (
                  <tr key={i}>
                    <td className="mono" style={{color: 'var(--text-secondary)'}}>{p.id}</td>
                    <td className="mono" style={{textAlign: 'right', color: 'var(--text-secondary)'}}>{p.staked.toLocaleString()}</td>
                    <td className="mono" style={{textAlign: 'right', color: 'var(--brand-gold)', fontWeight: 700}}>
                        +{p.earned_avr.toFixed(4)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* The Node Grid */}
      <section className="glass-panel">
          <div className="header-title" style={{marginBottom: '20px'}}>
             <Server size={20} color="var(--text-primary)" />
             <h2 style={{fontSize: '18px', color: 'var(--text-primary)'}}>Live Node Roster (Redis State Grid)</h2>
          </div>
          <div className="table-container" style={{maxHeight: '400px', overflowY: 'auto'}}>
              <table>
                  <thead style={{position: 'sticky', top: 0, backgroundColor: 'var(--bg-panel)', zIndex: 1}}>
                      <tr>
                          <th>Node ID</th>
                          <th>Location</th>
                          <th>Status</th>
                          <th>VRAM Free</th>
                          <th>Temp</th>
                          <th>Earned $AVR</th>
                      </tr>
                  </thead>
                  <tbody>
                      {nodes.sort((a,b) => b.earned_avr - a.earned_avr).map((n) => (
                          <tr key={n.id_short}>
                              <td className="mono" style={{color: 'var(--text-secondary)'}}>{n.id_short}</td>
                              <td className="mono">{n.location}</td>
                              <td>
                                  <div style={{display: 'flex', alignItems: 'center', gap: '6px', cursor: 'help'}} title="Phase 4.4: Centralized Beta">
                                      <span className={`status-dot ${n.status.toLowerCase()}`}></span>
                                      <span className={`badge ${n.status.toLowerCase()}`}>
                                          {n.status === 'SUPERPOSITION' ? 'PRE-LOADED' : n.status}
                                      </span>
                                  </div>
                              </td>
                              <td className="mono">{n.vram_free.toFixed(1)} GB</td>
                              <td className="mono">{n.temperature_c.toFixed(1)} °C</td>
                              <td className="mono" style={{color: 'var(--brand-gold)'}}>{n.earned_avr.toFixed(4)}</td>
                          </tr>
                      ))}
                  </tbody>
              </table>
          </div>
      </section>

      {/* The Founder's Footer */}
      <footer className="founder-footer">
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

export default NetworkExplorer;
