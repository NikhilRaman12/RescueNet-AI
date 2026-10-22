import { FormEvent, useEffect, useMemo, useState } from 'react';
import {
  Activity,
  ArrowDownRight,
  AudioLines,
  Check,
  CheckCircle2,
  ChevronDown,
  CircleHelp,
  ExternalLink,
  HeartHandshake,
  House,
  ListChecks,
  LoaderCircle,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Waves,
} from 'lucide-react';
import './readyathome.css';

type ReadinessTask = {
  id: string;
  priority: 'Start here' | 'Prepare at home' | 'If flooding threatens';
  title: string;
  detail: string;
  rationale: string;
  source_id: string;
};

type ReadinessSource = { id: string; label: string; url: string };
type ReadinessPlan = {
  scenario_id: string;
  scenario_name: string;
  assistant_response: string;
  assessment: { label: string; summary: string; rationale: string[] };
  assumptions: string[];
  tasks: ReadinessTask[];
  sources: ReadinessSource[];
  tools: Array<{ name: string; status: string; detail: string }>;
};
type ActivityEvent = { timestamp: string; action: string; task_id?: string | null };

const DEMO_PROMPT = 'Help me prepare my household for possible flooding.';
const STORAGE_KEY = 'readyathome-progress-v1';
const API_BASE = import.meta.env.VITE_API_BASE?.trim() || 'http://127.0.0.1:8010';

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, init);
  } catch {
    throw new Error('Could not reach the local planner. Start the FastAPI backend on port 8010, then try again.');
  }
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = typeof body.detail === 'string' ? body.detail : `Request failed (${response.status}).`;
    throw new Error(detail);
  }
  return body as T;
}

function savedProgress(): Record<string, boolean> {
  try {
    const saved = JSON.parse(window.localStorage.getItem(STORAGE_KEY) || '{}') as unknown;
    if (saved && typeof saved === 'object' && !Array.isArray(saved)) {
      return Object.fromEntries(Object.entries(saved).map(([key, value]) => [key, value === true]));
    }
  } catch {
    // Browser storage is optional; task controls still work in memory.
  }
  return {};
}

function saveProgress(progress: Record<string, boolean>) {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
  } catch {
    // Keep the current session usable if browser storage is unavailable.
  }
}

function describeActivity(event: ActivityEvent, tasks: ReadinessTask[]) {
  if (event.action === 'readiness_plan_generated') return 'Prepared the flood-readiness demo plan';
  const taskTitle = tasks.find((task) => task.id === event.task_id)?.title ?? 'a preparedness task';
  if (event.action === 'readiness_task_completed') return `Marked “${taskTitle}” complete`;
  if (event.action === 'readiness_task_reopened') return `Reopened “${taskTitle}”`;
  return 'Updated the demo plan';
}

export default function ReadyAtHome() {
  const [utterance, setUtterance] = useState(DEMO_PROMPT);
  const [plan, setPlan] = useState<ReadinessPlan | null>(null);
  const [completed, setCompleted] = useState<Record<string, boolean>>({});
  const [activity, setActivity] = useState<ActivityEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [savingTask, setSavingTask] = useState('');
  const [activityLoading, setActivityLoading] = useState(false);
  const [error, setError] = useState('');
  const [activityError, setActivityError] = useState('');

  const completedCount = useMemo(
    () => plan?.tasks.filter((task) => completed[task.id]).length ?? 0,
    [completed, plan],
  );

  async function refreshActivity() {
    setActivityLoading(true);
    setActivityError('');
    try {
      const result = await requestJson<{ items: ActivityEvent[] }>('/api/readiness/activity');
      setActivity(result.items);
    } catch (refreshError) {
      setActivityError(refreshError instanceof Error ? refreshError.message : 'Activity is unavailable.');
    } finally {
      setActivityLoading(false);
    }
  }

  useEffect(() => {
    void refreshActivity();
  }, []);

  async function submitRequest(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError('');
    setPlan(null);
    try {
      const result = await requestJson<ReadinessPlan>('/api/readiness/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ utterance }),
      });
      const saved = savedProgress();
      const nextProgress = Object.fromEntries(result.tasks.map((task) => [task.id, saved[task.id] === true]));
      setCompleted(nextProgress);
      setPlan(result);
      saveProgress(nextProgress);
      await refreshActivity();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : 'The local planner could not make a plan.');
    } finally {
      setLoading(false);
    }
  }

  async function changeTask(task: ReadinessTask, nextValue: boolean) {
    setSavingTask(task.id);
    setError('');
    try {
      await requestJson(`/api/readiness/tasks/${encodeURIComponent(task.id)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ completed: nextValue }),
      });
      const nextProgress = { ...completed, [task.id]: nextValue };
      setCompleted(nextProgress);
      saveProgress(nextProgress);
      await refreshActivity();
    } catch (taskError) {
      setError(taskError instanceof Error ? taskError.message : 'The task could not be updated.');
    } finally {
      setSavingTask('');
    }
  }

  function sourceFor(id: string) {
    return plan?.sources.find((source) => source.id === id);
  }

  return (
    <div className="ready-app">
      <header className="ready-header">
        <a className="brand" href="#top" aria-label="ReadyAtHome home">
          <span className="brand-mark"><House size={19} strokeWidth={2.2} /></span>
          <span className="brand-name">ReadyAtHome<span>by RescueNet AI</span></span>
        </a>
        <div className="simulation-badge"><AudioLines size={15} /> Alexa+ interaction simulation</div>
        <a className="about-link" href="#about-simulation">About this demo <ArrowDownRight size={15} /></a>
      </header>

      <main id="top">
        <section className="hero-grid" aria-labelledby="hero-title">
          <div className="hero-copy">
            <div className="eyebrow"><Sparkles size={15} /> Household preparedness, made clearer</div>
            <h1 id="hero-title">A steadier plan<br />starts <em>at home.</em></h1>
            <p className="hero-description">
              Ask for help getting ready. ReadyAtHome turns a simulated voice request into a short,
              explainable checklist you can work through at your own pace.
            </p>
            <div className="hero-note"><ShieldCheck size={17} /> Local demo · deterministic plan · no account needed</div>
          </div>

          <div className="request-card">
            <div className="request-card-top">
              <span className="assistant-avatar"><AudioLines size={19} /></span>
              <div><strong>Your preparedness assistant</strong><span>Type a request as if you were speaking</span></div>
            </div>
            <form onSubmit={submitRequest}>
              <label htmlFor="voice-request">What would you like help preparing for?</label>
              <textarea
                id="voice-request"
                value={utterance}
                onChange={(event) => setUtterance(event.target.value)}
                maxLength={240}
                rows={3}
                required
                minLength={3}
                aria-describedby="request-hint"
                placeholder="For example: Help me get ready for possible flooding."
              />
              <div className="request-actions">
                <span id="request-hint" className="input-hint">Up to 240 characters · request text is not stored</span>
                <button className="primary-button" type="submit" disabled={loading || !utterance.trim()}>
                  {loading ? <><LoaderCircle className="spin" size={17} /> Building plan</> : <><Waves size={17} /> Prepare my plan</>}
                </button>
              </div>
            </form>
            <div className="sample-prompt"><span>Try the reproducible demo</span>
              <button type="button" className="sample-button" onClick={() => { setUtterance(DEMO_PROMPT); setError(''); }}>
                “Help me prepare for possible flooding”
              </button>
            </div>
            <p className="voice-note"><CircleHelp size={14} /> Text input only. No microphone, speech recognition, or Alexa+ service is connected.</p>
          </div>
        </section>

        {error && <div className="error-banner" role="alert"><ShieldAlert size={18} /><span>{error}</span></div>}

        {plan ? (
          <>
            <section className="plan-overview" aria-labelledby="plan-title">
              <div className="overview-heading">
                <div className="section-icon"><Waves size={19} /></div>
                <div><p className="eyebrow">Your local demo plan</p><h2 id="plan-title">{plan.scenario_name}</h2></div>
              </div>
              <div className="progress-summary" aria-live="polite">
                <div className="progress-copy"><span>Checklist progress</span><strong>{completedCount}<small> / {plan.tasks.length}</small></strong></div>
                <div className="progress-track" role="progressbar" aria-label="Preparedness checklist progress" aria-valuemin={0} aria-valuemax={plan.tasks.length} aria-valuenow={completedCount}>
                  <span style={{ width: `${plan.tasks.length ? (completedCount / plan.tasks.length) * 100 : 0}%` }} />
                </div>
              </div>
            </section>

            <section className="conversation-card" aria-label="Simulated assistant response">
              <span className="conversation-icon"><AudioLines size={17} /></span>
              <div><span className="conversation-label">ReadyAtHome · simulated response</span><p>{plan.assistant_response}</p></div>
            </section>

            <div className="content-grid">
              <section className="panel checklist-panel" aria-labelledby="checklist-title">
                <div className="panel-heading">
                  <div><p className="eyebrow">Five practical next steps</p><h2 id="checklist-title"><ListChecks size={21} /> Your checklist</h2></div>
                  <span className="task-count">{completedCount === plan.tasks.length ? 'All steps checked' : `${plan.tasks.length - completedCount} to review`}</span>
                </div>
                <div className="task-list">
                  {plan.tasks.map((task, index) => {
                    const source = sourceFor(task.source_id);
                    const isDone = completed[task.id] === true;
                    return (
                      <article className={`task-card ${isDone ? 'task-done' : ''}`} key={task.id}>
                        <label className="task-main">
                          <input
                            type="checkbox"
                            checked={isDone}
                            disabled={savingTask === task.id}
                            onChange={(event) => void changeTask(task, event.target.checked)}
                          />
                          <span className="custom-check" aria-hidden="true">{isDone && <Check size={14} />}</span>
                          <span className="task-title-wrap"><span className="task-index">{String(index + 1).padStart(2, '0')}</span><strong>{task.title}</strong></span>
                          <span className={`priority-tag priority-${index === 0 ? 'first' : index === plan.tasks.length - 1 ? 'safety' : 'prep'}`}>{task.priority}</span>
                        </label>
                        <p className="task-detail">{task.detail}</p>
                        <details className="why-details">
                          <summary>Why this is on the list <ChevronDown size={15} /></summary>
                          <p>{task.rationale}</p>
                          {source && <a href={source.url} target="_blank" rel="noreferrer">{source.label} <ExternalLink size={13} /></a>}
                        </details>
                      </article>
                    );
                  })}
                </div>
              </section>

              <aside className="side-column">
                <section className="panel assessment-panel" aria-labelledby="assessment-title">
                  <div className="panel-heading compact-heading">
                    <div className="assessment-icon"><ShieldCheck size={18} /></div>
                    <div><p className="eyebrow">Transparent assessment</p><h2 id="assessment-title">{plan.assessment.label}</h2></div>
                  </div>
                  <p className="assessment-summary">{plan.assessment.summary}</p>
                  <ul className="rationale-list">
                    {plan.assessment.rationale.map((item) => <li key={item}><CheckCircle2 size={15} />{item}</li>)}
                  </ul>
                  <div className="assumption-box"><strong>Scenario assumptions</strong>
                    <ul>{plan.assumptions.map((item) => <li key={item}>{item}</li>)}</ul>
                  </div>
                </section>

                <section className="panel activity-panel" aria-labelledby="activity-title">
                  <div className="panel-heading activity-heading">
                    <div><p className="eyebrow">Local SQLite audit</p><h2 id="activity-title"><Activity size={19} /> Recent activity</h2></div>
                    <button className="icon-button" type="button" onClick={() => void refreshActivity()} disabled={activityLoading} aria-label="Refresh activity">
                      <RefreshCw size={16} className={activityLoading ? 'spin' : ''} />
                    </button>
                  </div>
                  {activityError ? <p className="activity-message" role="status">{activityError}</p> : activity.length ? (
                    <ol className="activity-list">
                      {activity.slice(0, 6).map((event, index) => (
                        <li key={`${event.timestamp}-${index}`}><span className="activity-dot" /><div><strong>{describeActivity(event, plan.tasks)}</strong><time dateTime={event.timestamp}>{new Date(event.timestamp).toLocaleString()}</time></div></li>
                      ))}
                    </ol>
                  ) : <p className="activity-message">Your demo actions will appear here. Only task IDs and event times are recorded.</p>}
                </section>
              </aside>
            </div>

            <section className="sources-panel panel" aria-labelledby="sources-title">
              <div className="panel-heading">
                <div><p className="eyebrow">Reference material, not live feeds</p><h2 id="sources-title"><HeartHandshake size={20} /> Guidance sources</h2></div>
                <span className="source-disclaimer">Official links · opened only when selected</span>
              </div>
              <div className="source-list">
                {plan.sources.map((source) => <a href={source.url} key={source.id} target="_blank" rel="noreferrer"><span><ExternalLink size={15} /></span>{source.label}<ExternalLink size={13} className="source-arrow" /></a>)}
              </div>
            </section>

            <section className="integration-strip" aria-label="Integration status">
              {plan.tools.map((tool) => <div className="integration-item" key={tool.name}>
                <span className={`integration-status status-${tool.status.replace(/\s+/g, '-')}`} />
                <div><strong>{tool.name}</strong><span>{tool.status}</span></div>
                <p>{tool.detail}</p>
              </div>)}
            </section>
          </>
        ) : (
          <section className="empty-state panel" aria-label="Demo preview">
            <div className="empty-art"><House size={32} /><span><ShieldCheck size={15} /></span></div>
            <p className="eyebrow">Ready when you are</p>
            <h2>Try a flood-preparedness rehearsal</h2>
            <p>Use the sample request above to build the same five-step plan every time. The demo will not check weather, infer your location, or contact anyone.</p>
            <div className="empty-facts"><span><CheckCircle2 size={15} /> No account or credentials</span><span><CheckCircle2 size={15} /> No live data</span><span><CheckCircle2 size={15} /> Request text stays in this page</span></div>
          </section>
        )}

        <footer className="safety-footer" id="about-simulation">
          <div className="safety-icon"><ShieldAlert size={19} /></div>
          <div><strong>Preparedness support only</strong><p>ReadyAtHome is an independent prototype and is not an Amazon product or a connected Alexa device. It is not an emergency-dispatch service and does not provide current alerts, evacuation orders, routes, or shelter availability. Follow official local alerts and emergency services.</p></div>
        </footer>
        <div className="page-footnote">A reproducible local scenario · Built on the existing RescueNet AI repository</div>
      </main>
    </div>
  );
}
