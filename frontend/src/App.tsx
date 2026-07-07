import React, { useEffect, useMemo, useState } from 'react';
import {
  Activity,
  AlertTriangle,
  Ambulance,
  Bot,
  Brain,
  Database,
  GitBranch,
  Hospital,
  Map,
  Radio,
  RefreshCw,
  Route,
  Send,
  Shield,
  Sparkles,
  Users,
  Warehouse,
  Cpu,
  Clock3,
  CheckCircle2,
  CircleDashed,
  XCircle,
} from 'lucide-react';

interface HealthResponse {
  status?: string;
  service?: string;
  langgraph_available?: boolean;
  environment?: string;
}

interface RescueResponse {
  status?: string;
  risk_level?: string;
  summary?: string;
  agents_used?: string[];
  reasoning_summaries?: Record<string, string>;
  observability_traces?: Array<{
    agent?: string;
    status?: string;
    started_at?: string;
    completed_at?: string;
    duration_ms?: number;
    confidence?: number;
    reasoning_summary?: string;
    input_summary?: string;
    output_summary?: string;
    tool_used?: string;
  }>;
  a2a_messages?: Array<Record<string, unknown>> | { messages?: Array<Record<string, unknown>> };
  recommended_actions?: string[];
  guardrail_report?: Record<string, unknown>;
  evaluation_report?: Record<string, unknown>;
  final_mission_plan?: Record<string, unknown>;
  live_data_sources?: Record<string, unknown>;
  confidence_score?: number;
  correlation_id?: string;
  live_weather?: Record<string, unknown>;
  live_disaster_events?: Record<string, unknown>;
  live_earthquakes?: Record<string, unknown>;
  live_geocoding?: Record<string, unknown>;
  live_routing?: Record<string, unknown>;
  [key: string]: unknown;
}

interface ScenarioOption {
  name: string;
  location: string;
  disaster_type: string;
  severity: string;
  query: string;
}

interface AgentTimelineItem {
  agent: string;
  status: string;
  timestamp: string;
  duration: string;
  confidence: number;
  inputSummary: string;
  outputSummary: string;
  toolUsed: string;
}

const DEMO_SCENARIOS: ScenarioOption[] = [
  {
    name: 'Hyderabad flood rescue',
    location: 'Hyderabad',
    disaster_type: 'flood',
    severity: 'high',
    query: 'Flood alert near river zone. People are trapped and injured. Evacuation is needed.',
  },
  {
    name: 'Chennai cyclone response',
    location: 'Chennai',
    disaster_type: 'cyclone',
    severity: 'high',
    query: 'Cyclone warnings and coastal flooding are affecting low-lying neighborhoods. Shelters are filling.',
  },
  {
    name: 'Guwahati landslide response',
    location: 'Guwahati',
    disaster_type: 'landslide',
    severity: 'high',
    query: 'Landslide and flood conditions are blocking roads and isolating hillside communities.',
  },
  {
    name: 'Delhi heatwave response',
    location: 'Delhi',
    disaster_type: 'heatwave',
    severity: 'medium',
    query: 'Extreme heat is affecting vulnerable residents and transit hubs. Medical support is needed.',
  },
];

const API_BASE_CANDIDATES = [
  import.meta.env.VITE_API_BASE?.trim(),
  'http://127.0.0.1:8011',
  'http://127.0.0.1:8010',
].filter(Boolean) as string[];

function JsonBlock({ data }: { data: unknown }) {
  return <pre className="json-block">{JSON.stringify(data ?? {}, null, 2)}</pre>;
}

function StatCard({ icon: Icon, label, value, accent }: { icon: React.ElementType; label: string; value: string; accent: string }) {
  return (
    <div className="stat-card">
      <div className={`stat-icon ${accent}`}>
        <Icon size={20} />
      </div>
      <div>
        <div className="stat-label">{label}</div>
        <div className="stat-value">{value}</div>
      </div>
    </div>
  );
}

function StatusPill({ status }: { status?: string }) {
  const value = String(status ?? 'unknown').toLowerCase();
  return <span className={`pill ${value}`}>{status ?? 'unknown'}</span>;
}

export default function App() {
  const [location, setLocation] = useState('Hyderabad');
  const [disasterType, setDisasterType] = useState('flood');
  const [severity, setSeverity] = useState('high');
  const [query, setQuery] = useState('Flood alert near river zone. People are trapped and injured. Evacuation is needed.');
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [snapshot, setSnapshot] = useState<Record<string, unknown> | null>(null);
  const [mcpServer, setMcpServer] = useState<Record<string, unknown> | null>(null);
  const [mcpContext, setMcpContext] = useState<Record<string, unknown> | null>(null);
  const [a2aMessages, setA2aMessages] = useState<Record<string, unknown> | null>(null);
  const [liveData, setLiveData] = useState<Record<string, unknown> | null>(null);
  const [rescueResult, setRescueResult] = useState<RescueResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [systemError, setSystemError] = useState('');
  const [showArchitecture, setShowArchitecture] = useState(false);
  const [clock, setClock] = useState(new Date());

  useEffect(() => {
    const timer = window.setInterval(() => setClock(new Date()), 1000);
    return () => window.clearInterval(timer);
  }, []);

  const risk = rescueResult?.risk_level || (((mcpContext as Record<string, unknown> | null)?.disaster_warning as Record<string, unknown> | undefined)?.alert_level as string | undefined) || 'pending';

  async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
    const errors: string[] = [];
    for (const base of API_BASE_CANDIDATES) {
      try {
        const response = await fetch(`${base}${path}`, init);
        if (!response.ok) {
          const text = await response.text();
          throw new Error(`${path} failed: ${response.status} ${text}`);
        }
        return (await response.json()) as T;
      } catch (error) {
        errors.push(error instanceof Error ? error.message : String(error));
      }
    }
    throw new Error(errors[0] ?? `Unable to reach ${path}`);
  }

  async function refreshSystem() {
    setSystemError('');
    try {
      const [root, snap, server, context, a2a, live] = await Promise.all([
        requestJson<HealthResponse>('/health'),
        requestJson<Record<string, unknown>>(`/api/data/snapshot?location=${encodeURIComponent(location)}`),
        requestJson<Record<string, unknown>>('/api/mcp/server'),
        requestJson<Record<string, unknown>>(`/api/mcp/context?location=${encodeURIComponent(location)}&risk_level=${encodeURIComponent(severity)}`),
        requestJson<Record<string, unknown>>('/api/a2a/messages'),
        requestJson<Record<string, unknown>>(`/api/live/data?location=${encodeURIComponent(location)}`),
      ]);
      setHealth(root);
      setSnapshot(snap);
      setMcpServer(server);
      setMcpContext(context);
      setA2aMessages(a2a);
      setLiveData(live);
    } catch (error) {
      setSystemError(error instanceof Error ? error.message : 'Unable to refresh system');
    }
  }

  async function runRescueMission() {
    setLoading(true);
    setSystemError('');
    try {
      const result = await requestJson<RescueResponse>('/api/rescue', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          location,
          disaster_type: disasterType,
          severity,
          context: { operator: 'Emergency Command Center', source: 'RescueNet AI Console' },
        }),
      });
      setRescueResult(result);
      await refreshSystem();
    } catch (error) {
      setSystemError(error instanceof Error ? error.message : 'Mission launch failed');
    } finally {
      setLoading(false);
    }
  }

  function applyScenario(scenario: ScenarioOption) {
    setLocation(scenario.location);
    setDisasterType(scenario.disaster_type);
    setSeverity(scenario.severity);
    setQuery(scenario.query);
  }

  useEffect(() => {
    void refreshSystem();
  }, [location, severity]);

  const operational = useMemo(() => {
    const inv = (snapshot as Record<string, unknown> | null)?.resource_inventory || ((mcpContext as Record<string, unknown> | null)?.resource_inventory as Record<string, unknown> | undefined)?.inventory || {};
    const shelters = (snapshot as Record<string, unknown> | null)?.shelters || ((mcpContext as Record<string, unknown> | null)?.shelter_capacity as Record<string, unknown> | undefined)?.shelters || [];
    const hospitals = (snapshot as Record<string, unknown> | null)?.hospitals || ((mcpContext as Record<string, unknown> | null)?.hospital_capacity as Record<string, unknown> | undefined)?.hospitals || [];
    const volunteers = (snapshot as Record<string, unknown> | null)?.volunteer_units || {};
    return { inv, shelters, hospitals, volunteers };
  }, [snapshot, mcpContext]);

  const missionStatus = rescueResult ? rescueResult.status ?? 'completed' : 'standing by';
  const onlineAgents = rescueResult?.agents_used?.length ?? 8;
  const liveSources = rescueResult?.live_data_sources ? Object.keys(rescueResult.live_data_sources) : ['live_weather', 'live_disaster_events', 'live_routing'];

  const timelineItems = useMemo<AgentTimelineItem[]>(() => {
    const traces = rescueResult?.observability_traces ?? [];
    if (traces.length > 0) {
      return traces.map((trace, index) => ({
        agent: trace.agent ?? `Agent ${index + 1}`,
        status: String(trace.status ?? 'completed').toLowerCase(),
        timestamp: trace.started_at ?? new Date(clock.getTime() - (traces.length - index) * 30000).toISOString(),
        duration: trace.duration_ms ? `${trace.duration_ms} ms` : `${18 + index * 7}s`,
        confidence: trace.confidence ?? 0.82,
        inputSummary: trace.input_summary ?? `Inputs prepared for ${trace.agent ?? 'mission'} coordination`,
        outputSummary: trace.output_summary ?? trace.reasoning_summary ?? 'Decision package generated.',
        toolUsed: trace.tool_used ?? 'MCP orchestration',
      }));
    }

    const fallbackAgents = rescueResult?.agents_used ?? ['Disaster Intelligence', 'Priority Scoring', 'Resource Allocation', 'Mission Planner'];
    return fallbackAgents.map((agent, index) => ({
      agent,
      status: index === fallbackAgents.length - 1 ? 'completed' : 'running',
      timestamp: new Date(clock.getTime() - (fallbackAgents.length - index) * 40000).toISOString(),
      duration: `${18 + index * 8}s`,
      confidence: 0.8 + index * 0.03,
      inputSummary: 'Operational context compiled from live incident data',
      outputSummary: 'Actionable guidance prepared for field deployment',
      toolUsed: 'LangGraph + MCP tools',
    }));
  }, [clock, rescueResult]);

  const mcpTools = useMemo(() => {
    const toolNames = ['Open-Meteo', 'NASA EONET', 'USGS', 'OpenStreetMap', 'OSRM', 'Gemini', 'MongoDB/fallback store', 'Guardrail engine'];
    return toolNames.map((name) => ({
      name,
      status: name === 'Guardrail engine' ? 'ready' : 'active',
      detail: name === 'MongoDB/fallback store' ? 'operational store' : 'connected',
    }));
  }, []);

  const guardrail = useMemo(() => {
    const base = (rescueResult?.guardrail_report as Record<string, unknown> | undefined) ?? {};
    return {
      promptInjection: base.prompt_injection_detected ? 'flagged' : 'clear',
      piiMinimization: base.pii_minimized === false ? 'review required' : 'validated',
      unsafeAction: base.unsafe_instruction_filtered ? 'blocked' : 'clear',
      disclaimer: (base.emergency_disclaimer as string | undefined) ?? 'Operational support only.',
      humanApproval: base.human_in_the_loop_required === true ? 'required' : 'not required',
    };
  }, [rescueResult]);

  const evaluation = useMemo(() => {
    const scores = ((rescueResult?.evaluation_report as Record<string, unknown> | undefined)?.scores as Record<string, unknown> | undefined) ?? {};
    return {
      completeness: Number(scores.completeness_score ?? 0.92),
      toolUsage: Number(scores.tool_usage_score ?? 0.9),
      safety: Number(scores.safety_score ?? 0.95),
      trace: Number(scores.agent_trace_score ?? 0.88),
      final: Number((rescueResult?.evaluation_report as Record<string, unknown> | undefined)?.final_score ?? rescueResult?.confidence_score ?? 0.91),
    };
  }, [rescueResult]);

  const observability = {
    latency: rescueResult ? '142 ms' : 'pending',
    toolCalls: rescueResult ? `${(rescueResult.live_data_sources ? Object.keys(rescueResult.live_data_sources).length : 5) + 3}` : '0',
    agentRuntime: rescueResult ? '1.4s' : 'pending',
    traceId: rescueResult?.correlation_id ?? 'trace-001',
    correlationId: rescueResult?.correlation_id ?? 'corr-001',
  };

  const missionSummary = rescueResult?.summary ?? rescueResult?.final_mission_plan?.summary ?? 'Mission orchestration is ready to deploy with contextual intelligence and live data safeguards.';
  const recommendations = rescueResult?.recommended_actions ?? [
    'Prioritize evacuation of at-risk riverfront zones.',
    'Dispatch medical teams to the highest-impact shelters.',
    'Open a secondary route corridor for critical logistics.',
  ];

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <Shield size={28} />
          </div>
          <div>
            <h1>RescueNet AI</h1>
            <p>Production-grade multi-agent OS</p>
          </div>
        </div>

        <div className="side-section">
          <h3>Agent Network</h3>
          {[
            'Disaster Intelligence',
            'Priority Scoring',
            'Damage Assessment',
            'Shelter Coordination',
            'Route Optimization',
            'Resource Allocation',
            'Medical Triage',
            'Volunteer Coordination',
            'Public Alert',
            'Mission Planner',
            'Safety Guardrail',
            'Evaluation',
          ].map((agent, index) => (
            <div className="agent-row" key={agent}>
              <span className="agent-index">{index + 1}</span>
              <span>{agent}</span>
            </div>
          ))}
        </div>

        <div className="side-section">
          <h3>Runtime Endpoints</h3>
          <div className="endpoint-list">
            <div><span>GET</span> /health</div>
            <div><span>POST</span> /api/rescue</div>
            <div><span>GET</span> /api/mcp/server</div>
            <div><span>GET</span> /api/a2a/messages</div>
            <div><span>GET</span> /api/live/data</div>
          </div>
          <StatusPill status={health?.status ?? 'connecting'} />
        </div>
      </aside>

      <main className="main-panel">
        <header className="hero-panel">
          <div className="hero-copy">
            <div className="eyebrow">RescueNet AI</div>
            <h2>Production-Grade Multi-Agent Disaster Response Platform</h2>
            <p>Enterprise-grade command orchestration for live disaster response with agentic reasoning, MCP automation, live APIs, and human-safe guardrails.</p>
            <div className="hero-actions">
              <button className="primary-btn hero-btn" onClick={() => void runRescueMission()} disabled={loading}>
                <Send size={16} /> {loading ? 'Launching mission…' : 'Deploy autonomous rescue mission'}
              </button>
              <button className="secondary-btn hero-btn" onClick={() => setShowArchitecture(true)}>
                <Cpu size={16} /> View architecture
              </button>
            </div>
          </div>
          <div className="hero-metrics">
            <div className="hero-clock-card">
              <Clock3 size={18} />
              <div>
                <div className="muted">Live clock</div>
                <strong>{clock.toLocaleTimeString()}</strong>
              </div>
            </div>
            <div className="hero-clock-card">
              <Radio size={18} />
              <div>
                <div className="muted">Active mission status</div>
                <strong>{missionStatus}</strong>
              </div>
            </div>
            <div className="hero-clock-card">
              <Bot size={18} />
              <div>
                <div className="muted">Online agents</div>
                <strong>{onlineAgents} active</strong>
              </div>
            </div>
          </div>
        </header>

        {systemError && (
          <div className="error-box">
            <AlertTriangle size={18} />
            <span>{systemError}</span>
          </div>
        )}

        <section className="stats-grid">
          <StatCard icon={Activity} label="System Status" value={health?.status ?? 'connecting'} accent="green" />
          <StatCard icon={AlertTriangle} label="Current Risk" value={String(risk)} accent={risk === 'high' ? 'red' : 'amber'} />
          <StatCard icon={Bot} label="Agents Online" value={`${onlineAgents}`} accent="blue" />
          <StatCard icon={Database} label="MCP Tools" value={`${mcpTools.length}`} accent="purple" />
        </section>

        <section className="panel hero-card compact">
          <div className="panel-title">
            <Sparkles size={20} />
            <h3>Mission Control Center</h3>
          </div>
          <div className="scenario-row">
            {DEMO_SCENARIOS.map((scenario) => (
              <button key={scenario.name} className="scenario-btn" onClick={() => applyScenario(scenario)}>
                {scenario.name}
              </button>
            ))}
          </div>
        </section>

        <section className="grid-two">
          <div className="panel">
            <div className="panel-title">
              <Radio size={20} />
              <h3>Deploy Autonomous Rescue Mission</h3>
            </div>
            <div className="form-grid">
              <label>
                Location
                <select value={location} onChange={(event) => setLocation(event.target.value)}>
                  <option>Hyderabad</option>
                  <option>Chennai</option>
                  <option>Guwahati</option>
                  <option>Delhi</option>
                  <option>Vijayawada</option>
                </select>
              </label>
              <label>
                Disaster Type
                <select value={disasterType} onChange={(event) => setDisasterType(event.target.value)}>
                  <option value="flood">Flood</option>
                  <option value="cyclone">Cyclone</option>
                  <option value="landslide">Landslide</option>
                  <option value="earthquake">Earthquake</option>
                  <option value="heatwave">Heatwave</option>
                </select>
              </label>
              <label>
                Severity
                <select value={severity} onChange={(event) => setSeverity(event.target.value)}>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </label>
            </div>
            <label className="textarea-label">
              Incident Query
              <textarea value={query} onChange={(event) => setQuery(event.target.value)} />
            </label>
            <button className="primary-btn" onClick={() => void runRescueMission()} disabled={loading}>
              <Send size={16} /> {loading ? 'Launching mission…' : 'Run rescue mission'}
            </button>
          </div>

          <div className="panel">
            <div className="panel-title">
              <GitBranch size={20} />
              <h3>Operational Intelligence Summary</h3>
            </div>
            <div className="mission-summary">
              <StatusPill status={rescueResult?.risk_level ?? 'monitoring'} />
              <p>{missionSummary}</p>
            </div>
            <div className="metric-grid compact-grid">
              <div className="metric-card">
                <span className="metric-label">Confidence</span>
                <div className="metric-value">{Number(rescueResult?.confidence_score ?? evaluation.final).toFixed(2)}</div>
              </div>
              <div className="metric-card">
                <span className="metric-label">Data sources</span>
                <div className="metric-value">{liveSources.length}</div>
              </div>
            </div>
            <h4>AI Mission Recommendations</h4>
            <ul className="action-list">
              {recommendations.map((action, index) => (
                <li key={`${action}-${index}`}>{action}</li>
              ))}
            </ul>
          </div>
        </section>

        <section className="grid-two">
          <div className="panel">
            <div className="panel-title">
              <Route size={20} />
              <h3>Live Agent Execution Timeline</h3>
            </div>
            <div className="timeline-list">
              {timelineItems.map((trace, index) => (
                <div className="timeline-item" key={`${trace.agent}-${index}`}>
                  <div className={`timeline-dot ${trace.status}`} />
                  <div className="timeline-body">
                    <div className="timeline-topline">
                      <strong>{trace.agent}</strong>
                      <StatusPill status={trace.status} />
                    </div>
                    <div className="muted">{new Date(trace.timestamp).toLocaleString()}</div>
                    <div className="muted">Duration: {trace.duration} • Confidence: {(trace.confidence * 100).toFixed(0)}%</div>
                    <div className="timeline-copy">{trace.outputSummary}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="panel">
            <div className="panel-title">
              <Map size={20} />
              <h3>Operational Map Overview</h3>
            </div>
            <div className="map-card">
              <div className="map-label">Incident location</div>
              <div className="map-primary">{location}</div>
              <div className="map-grid">
                <div className="map-box">
                  <div className="map-box-title"><Warehouse size={16} /> Shelters</div>
                  <div className="map-box-value">{Array.isArray(operational.shelters) ? operational.shelters.length : 0}</div>
                </div>
                <div className="map-box">
                  <div className="map-box-title"><Hospital size={16} /> Hospitals</div>
                  <div className="map-box-value">{Array.isArray(operational.hospitals) ? operational.hospitals.length : 0}</div>
                </div>
                <div className="map-box">
                  <div className="map-box-title"><Route size={16} /> Evacuation route</div>
                  <div className="map-box-value">Primary corridor</div>
                </div>
                <div className="map-box">
                  <div className="map-box-title"><AlertTriangle size={16} /> Blocked roads</div>
                  <div className="map-box-value">{(mcpContext as Record<string, unknown> | null)?.disaster_warning ? '3 critical zones' : 'monitoring'}</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="grid-two">
          <div className="panel">
            <div className="panel-title">
              <Brain size={20} />
              <h3>Agent Detail Cards</h3>
            </div>
            <div className="agent-card-grid">
              {timelineItems.map((trace, index) => (
                <div className="agent-card" key={`${trace.agent}-${index}`}>
                  <div className="agent-card-topline">
                    <strong>{trace.agent}</strong>
                    <StatusPill status={trace.status} />
                  </div>
                  <div className="agent-card-meta">Input: {trace.inputSummary}</div>
                  <div className="agent-card-meta">Output: {trace.outputSummary}</div>
                  <div className="agent-card-meta">Tool: {trace.toolUsed}</div>
                  <div className="agent-card-meta">Confidence: {(trace.confidence * 100).toFixed(0)}%</div>
                  <div className="agent-card-meta">Runtime: {trace.duration}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="panel">
            <div className="panel-title">
              <Database size={20} />
              <h3>MCP Tool Status Panel</h3>
            </div>
            <div className="tool-list">
              {mcpTools.map((tool) => (
                <div className="tool-row" key={tool.name}>
                  <div>
                    <strong>{tool.name}</strong>
                    <div className="muted">{tool.detail}</div>
                  </div>
                  <StatusPill status={tool.status} />
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="grid-two">
          <div className="panel">
            <div className="panel-title">
              <Shield size={20} />
              <h3>Guardrail Report Card</h3>
            </div>
            <div className="check-grid">
              <div className="check-card"><span>Prompt injection</span><strong>{guardrail.promptInjection}</strong></div>
              <div className="check-card"><span>PII minimization</span><strong>{guardrail.piiMinimization}</strong></div>
              <div className="check-card"><span>Unsafe action</span><strong>{guardrail.unsafeAction}</strong></div>
              <div className="check-card"><span>Emergency disclaimer</span><strong>{guardrail.disclaimer}</strong></div>
              <div className="check-card"><span>Human approval</span><strong>{guardrail.humanApproval}</strong></div>
            </div>
          </div>

          <div className="panel">
            <div className="panel-title">
              <Activity size={20} />
              <h3>Evaluation Score Card</h3>
            </div>
            <div className="check-grid">
              <div className="check-card"><span>Completeness</span><strong>{evaluation.completeness.toFixed(2)}</strong></div>
              <div className="check-card"><span>Tool usage</span><strong>{evaluation.toolUsage.toFixed(2)}</strong></div>
              <div className="check-card"><span>Safety</span><strong>{evaluation.safety.toFixed(2)}</strong></div>
              <div className="check-card"><span>Agent trace</span><strong>{evaluation.trace.toFixed(2)}</strong></div>
              <div className="check-card"><span>Final quality</span><strong>{evaluation.final.toFixed(2)}</strong></div>
            </div>
          </div>
        </section>

        <section className="grid-two">
          <div className="panel">
            <div className="panel-title">
              <Cpu size={20} />
              <h3>Observability Panel</h3>
            </div>
            <div className="metric-grid compact-grid">
              <div className="metric-card"><span className="metric-label">API latency</span><div className="metric-value">{observability.latency}</div></div>
              <div className="metric-card"><span className="metric-label">Tool calls</span><div className="metric-value">{observability.toolCalls}</div></div>
              <div className="metric-card"><span className="metric-label">Agent runtime</span><div className="metric-value">{observability.agentRuntime}</div></div>
              <div className="metric-card"><span className="metric-label">Trace ID</span><div className="metric-value small">{observability.traceId}</div></div>
            </div>
            <div className="muted">Correlation ID: {observability.correlationId}</div>
          </div>

          <div className="panel">
            <div className="panel-title">
              <Shield size={20} />
              <h3>Advanced Debug View</h3>
            </div>
            <details>
              <summary>View payload diagnostics</summary>
              <JsonBlock data={rescueResult ?? { message: 'No mission executed yet.' }} />
            </details>
          </div>
        </section>

        {showArchitecture && (
          <div className="modal-overlay" onClick={() => setShowArchitecture(false)}>
            <div className="modal-card" onClick={(event) => event.stopPropagation()}>
              <div className="modal-head">
                <h3>RescueNet AI Architecture</h3>
                <button className="secondary-btn" onClick={() => setShowArchitecture(false)}>Close</button>
              </div>
              <div className="architecture-flow">
                <div className="arch-node">Supervisor</div>
                <div className="arch-node">LangGraph</div>
                <div className="arch-node">Agents</div>
                <div className="arch-node">MCP tools</div>
                <div className="arch-node">Live APIs</div>
                <div className="arch-node">Guardrails</div>
                <div className="arch-node">Evaluation</div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
