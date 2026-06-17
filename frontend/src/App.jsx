import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  AlertTriangle,
  Ambulance,
  Bot,
  Database,
  GitBranch,
  Hospital,
  Map,
  Radio,
  RefreshCw,
  Route,
  Send,
  Shield,
  Users,
  Warehouse
} from "lucide-react";
import "./style.css";

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8010";

const agents = [
  "Disaster Intelligence",
  "Priority Scoring",
  "Damage Assessment",
  "Shelter Coordination",
  "Route Optimization",
  "Resource Allocation",
  "Medical Triage",
  "Volunteer Coordination",
  "Public Alert",
  "Mission Planner"
];

function JsonBlock({ data }) {
  return <pre className="json-block">{JSON.stringify(data || {}, null, 2)}</pre>;
}

function StatCard({ icon: Icon, label, value, accent }) {
  return (
    <div className="stat-card">
      <div className={`stat-icon ${accent || ""}`}>
        <Icon size={22} />
      </div>
      <div>
        <div className="stat-label">{label}</div>
        <div className="stat-value">{value}</div>
      </div>
    </div>
  );
}

function StatusPill({ status }) {
  const value = String(status || "unknown").toLowerCase();
  return <span className={`pill ${value}`}>{status || "unknown"}</span>;
}

function App() {
  const [location, setLocation] = useState("Hyderabad");
  const [disasterType, setDisasterType] = useState("flood");
  const [severity, setSeverity] = useState("high");
  const [query, setQuery] = useState(
    "Flood alert near river zone. People are trapped and injured. Evacuation is needed."
  );

  const [health, setHealth] = useState(null);
  const [snapshot, setSnapshot] = useState(null);
  const [mcpServer, setMcpServer] = useState(null);
  const [mcpContext, setMcpContext] = useState(null);
  const [mcpEvents, setMcpEvents] = useState(null);
  const [a2aMessages, setA2aMessages] = useState(null);
  const [rescueResult, setRescueResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [systemError, setSystemError] = useState("");

  const risk = rescueResult?.risk_level || mcpContext?.weather?.risk || "pending";

  async function getJson(path) {
    const res = await fetch(`${API_BASE}${path}`);
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`${path} failed: ${res.status} ${text}`);
    }
    return res.json();
  }

  async function postJson(path, payload) {
    const res = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`${path} failed: ${res.status} ${text}`);
    }
    return res.json();
  }

  async function refreshSystem() {
    setSystemError("");
    try {
      const [root, snap, server, context, events, a2a] = await Promise.all([
        getJson("/health").catch(() => getJson("/")),
        getJson(`/api/data/snapshot?location=${encodeURIComponent(location)}`),
        getJson("/api/mcp/server"),
        getJson(`/api/mcp/context?location=${encodeURIComponent(location)}&risk_level=${encodeURIComponent(severity)}`),
        getJson("/api/mcp/events"),
        getJson("/api/a2a/messages")
      ]);

      setHealth(root);
      setSnapshot(snap);
      setMcpServer(server);
      setMcpContext(context);
      setMcpEvents(events);
      setA2aMessages(a2a);
    } catch (err) {
      setSystemError(err.message);
    }
  }

  async function runRescueMission() {
    setLoading(true);
    setSystemError("");
    try {
      const result = await postJson("/api/rescue", {
        query,
        location,
        disaster_type: disasterType,
        severity,
        context: {
          operator: "Emergency Command Center",
          source: "RescueNet AI Console"
        }
      });
      setRescueResult(result);
      await refreshSystem();
    } catch (err) {
      setSystemError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refreshSystem();
  }, []);

  const operational = useMemo(() => {
    const inv = snapshot?.resource_inventory || mcpContext?.resource_inventory?.inventory || {};
    const shelters = snapshot?.shelters || mcpContext?.shelter_capacity?.shelters || [];
    const hospitals = snapshot?.hospitals || mcpContext?.hospital_capacity?.hospitals || [];
    const volunteers = snapshot?.volunteer_units || {};
    return { inv, shelters, hospitals, volunteers };
  }, [snapshot, mcpContext]);

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon"><Shield size={28} /></div>
          <div>
            <h1>RescueNet AI</h1>
            <p>Autonomous Disaster Response Command System</p>
          </div>
        </div>

        <div className="side-section">
          <h3>Agent Network</h3>
          {agents.map((agent, idx) => (
            <div className="agent-row" key={agent}>
              <span className="agent-index">{idx + 1}</span>
              <span>{agent}</span>
            </div>
          ))}
        </div>

        <div className="side-section">
          <h3>Backend</h3>
          <div className="backend-url">{API_BASE}</div>
          <StatusPill status={health?.status || "checking"} />
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <h2>Emergency Operations Console</h2>
            <p>FastAPI + LangGraph StateGraph + MCP tools + A2A protocol + operational data layer</p>
          </div>
          <button className="secondary-btn" onClick={refreshSystem}>
            <RefreshCw size={17} /> Refresh System
          </button>
        </header>

        {systemError && (
          <div className="error-box">
            <AlertTriangle size={18} />
            <span>{systemError}</span>
          </div>
        )}

        <section className="stats-grid">
          <StatCard icon={Activity} label="System Status" value={health?.status || "checking"} accent="green" />
          <StatCard icon={AlertTriangle} label="Current Risk" value={risk} accent={risk === "high" ? "red" : "amber"} />
          <StatCard icon={Bot} label="Agents" value="10" accent="blue" />
          <StatCard icon={Database} label="MCP Tools" value={mcpServer?.count || mcpServer?.tools?.count || 8} accent="purple" />
        </section>

        <section className="grid-two">
          <div className="panel mission-panel">
            <div className="panel-title">
              <Radio size={20} />
              <h3>Launch Rescue Mission</h3>
            </div>

            <div className="form-grid">
              <label>
                Location
                <select value={location} onChange={(e) => setLocation(e.target.value)}>
                  <option>Hyderabad</option>
                  <option>Vijayawada</option>
                  <option>Chennai</option>
                </select>
              </label>

              <label>
                Disaster Type
                <select value={disasterType} onChange={(e) => setDisasterType(e.target.value)}>
                  <option value="flood">Flood</option>
                  <option value="cyclone">Cyclone</option>
                  <option value="earthquake">Earthquake</option>
                  <option value="fire">Fire</option>
                  <option value="landslide">Landslide</option>
                </select>
              </label>

              <label>
                Severity
                <select value={severity} onChange={(e) => setSeverity(e.target.value)}>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </label>
            </div>

            <label className="textarea-label">
              Incident Query
              <textarea value={query} onChange={(e) => setQuery(e.target.value)} />
            </label>

            <button className="primary-btn" onClick={runRescueMission} disabled={loading}>
              <Send size={17} /> {loading ? "Coordinating Agents..." : "Run Multi-Agent Rescue Plan"}
            </button>
          </div>

          <div className="panel">
            <div className="panel-title">
              <GitBranch size={20} />
              <h3>Mission Output</h3>
            </div>

            {rescueResult ? (
              <>
                <div className="mission-summary">
                  <StatusPill status={rescueResult.risk_level} />
                  <p>{rescueResult.summary}</p>
                </div>

                <h4>Recommended Actions</h4>
                <ul className="action-list">
                  {(rescueResult.recommended_actions || []).map((a, i) => <li key={i}>{a}</li>)}
                </ul>
              </>
            ) : (
              <div className="empty-state">Run a mission to generate an agent-coordinated response plan.</div>
            )}
          </div>
        </section>

        <section className="grid-four">
          <div className="panel mini">
            <div className="mini-head"><Warehouse size={18} /> Resource Inventory</div>
            <JsonBlock data={operational.inv} />
          </div>

          <div className="panel mini">
            <div className="mini-head"><Hospital size={18} /> Hospitals</div>
            <JsonBlock data={operational.hospitals} />
          </div>

          <div className="panel mini">
            <div className="mini-head"><Map size={18} /> Routes</div>
            <JsonBlock data={snapshot?.routes || mcpContext?.route_intelligence} />
          </div>

          <div className="panel mini">
            <div className="mini-head"><Users size={18} /> Volunteer Units</div>
            <JsonBlock data={operational.volunteers} />
          </div>
        </section>

        <section className="grid-two">
          <div className="panel">
            <div className="panel-title">
              <Route size={20} />
              <h3>A2A Agent Communication</h3>
            </div>
            <JsonBlock data={rescueResult?.a2a_messages?.length ? rescueResult.a2a_messages : a2aMessages} />
          </div>

          <div className="panel">
            <div className="panel-title">
              <Database size={20} />
              <h3>MCP Operational Context</h3>
            </div>
            <JsonBlock data={mcpContext} />
          </div>
        </section>

        <section className="panel">
          <div className="panel-title">
            <Ambulance size={20} />
            <h3>Full Rescue Response Payload</h3>
          </div>
          <JsonBlock data={rescueResult || { message: "No mission executed yet." }} />
        </section>
      </main>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
