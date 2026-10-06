import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

function App() {
  const [repo, setRepo] = useState('');
  const [bug, setBug] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [mode, setMode] = useState('mock');
  const [token, setToken] = useState('');
  const [config, setConfig] = useState(null);
  useEffect(() => {
    fetch('/api/config').then(response => {
      if (!response.ok) throw new Error('Service configuration unavailable');
      return response.json();
    }).then(setConfig).catch(() => setConfig({ live_available: false }));
  }, []);
  async function diagnose(event) {
    event.preventDefault(); setBusy(true); setError(''); setResult(null);
    try {
      const response = await fetch('/api/diagnose', { method: 'POST', headers: { 'Content-Type': 'application/json', ...(mode === 'live' ? { 'X-RepoMedic-Token': token } : {}) }, body: JSON.stringify({ repo_url: repo, bug_description: bug, mode }), signal: AbortSignal.timeout(110000) });
      const data = await response.json();
      if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Check your repository URL and bug description (10–5000 characters).');
      setResult(data);
    } catch (err) { setError(err.name === 'TimeoutError' ? 'Analysis timed out. Please try again.' : err instanceof TypeError ? 'Cannot reach the service. Please try again shortly.' : err.message); }
    finally { setBusy(false); }
  }
  return <main>
    <header><a href="/" className="brand"><span className="mark">✚</span> RepoMedic</a><span className="pill">{mode === 'live' ? 'NEBIUS + NEMOTRON' : 'MOCK DEMO'}</span></header>
    <section className="intro"><span className="eyebrow">A LITTLE CARE FOR YOUR CODE</span><h1>From bug report<br/>to a clearer next step.</h1><p>Bring a repository and describe what broke. RepoMedic turns the symptoms into a structured triage plan.</p></section>
    <div className="workspace"><section className="card"><div className="section-title"><span className="number">01</span><h2>Tell us what happened</h2></div>
      <form onSubmit={diagnose}><label htmlFor="mode">Diagnosis mode</label><select id="mode" value={mode} disabled={busy} onChange={e => { setMode(e.target.value); setResult(null); setError(''); }}><option value="mock">Mock demo · no model calls</option><option value="live" disabled={!config?.live_available}>Live · Nebius + Nemotron{config && !config.live_available ? ' (setup required)' : ''}</option></select>{config && !config.live_available && <p className="hint">Live analysis will be available after server credentials are configured.</p>}{mode === 'live' && <><label htmlFor="token">Demo access token</label><input id="token" type="password" autoComplete="off" value={token} onChange={e => setToken(e.target.value)} required disabled={busy}/></>}<label htmlFor="repo">Public GitHub repository</label><input id="repo" type="url" placeholder="https://github.com/owner/repository" value={repo} onChange={e => setRepo(e.target.value)} required disabled={busy}/><label htmlFor="bug">Bug description</label><textarea id="bug" placeholder="What did you expect? What happened instead? Include steps to reproduce and any error messages." minLength={10} maxLength={5000} value={bug} onChange={e => setBug(e.target.value)} required disabled={busy}/><div className="hint">Be specific. A useful symptom is the start of a useful diagnosis.</div><button disabled={busy}>{busy ? (mode === 'live' ? 'Reading code and analyzing…' : 'Preparing triage…') : 'Diagnose repository ↗'}</button><p className="disclosure">{mode === 'live' ? 'Live mode sends your bug report and selected public source files to Nebius for analysis. It does not execute code.' : 'Mock demo: no repository is fetched and no AI model is called.'}</p>{error && <div className="error" role="alert">{error}</div>}</form>
    </section><section className="card report" aria-live="polite" aria-busy={busy}><div className="section-title"><span className="number">02</span><h2>Your triage report</h2></div>{result ? <><span className="pill">{result.mode === 'live' ? 'AI DIAGNOSIS · VERIFY FINDINGS' : 'MOCK DIAGNOSIS'}</span><h3>{result.title}</h3><p>{result.summary}</p><p className="repository">{result.repo_url}</p>{result.model && <p className="hint">Model: {result.model} · Commit: {result.commit?.slice(0, 7)}</p>}<h4>Suggested investigation</h4><ol>{result.steps.map(step => <li key={step}>{step}</li>)}</ol>{result.evidence?.length > 0 && <><h4>Source evidence</h4><ul>{result.evidence.map((item, index) => <li key={index}><a href={item.url} target="_blank" rel="noreferrer">{item.path}:{item.line}</a><p>{item.explanation}</p></li>)}</ul></>}{result.files_reviewed?.length > 0 && <details><summary>{result.files_reviewed.length} files reviewed</summary><ul>{result.files_reviewed.map(path => <li key={path}>{path}</li>)}</ul></details>}<div className="note">{result.disclaimer}</div></> : <div className="empty"><span className="pulse">✚</span><h3>{busy ? 'Organizing the symptoms' : 'Ready when you are'}</h3><p>Your suggested investigation steps will appear here after you submit a bug report.</p><div className="tags"><span>Reproduce</span><span>Investigate</span><span>Verify</span></div></div>}</section></div>
    <footer><span>RepoMedic · Nebius × NVIDIA hackathon project</span><span>Public code. Clearer next steps.</span></footer>
  </main>;
}
createRoot(document.getElementById('root')).render(<App/>);
