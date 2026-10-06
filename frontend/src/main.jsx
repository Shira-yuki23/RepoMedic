import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

function App() {
  const [repo, setRepo] = useState('');
  const [bug, setBug] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  async function diagnose(event) {
    event.preventDefault(); setBusy(true); setError(''); setResult(null);
    try {
      const response = await fetch('/api/diagnose', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ repo_url: repo, bug_description: bug }) });
      const data = await response.json();
      if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Check your repository URL and bug description (10–5000 characters).');
      setResult(data);
    } catch (err) { setError(err instanceof TypeError ? 'Cannot reach the backend. Start FastAPI on port 8000 and try again.' : err.message); }
    finally { setBusy(false); }
  }
  return <main>
    <header><a href="/" className="brand"><span className="mark">✚</span> RepoMedic</a><span className="pill">MILESTONE 01 · MOCK MODE</span></header>
    <section className="intro"><span className="eyebrow">A LITTLE CARE FOR YOUR CODE</span><h1>From bug report<br/>to a clearer next step.</h1><p>Bring a repository and describe what broke. RepoMedic turns the symptoms into a structured triage plan.</p></section>
    <div className="workspace"><section className="card"><div className="section-title"><span className="number">01</span><h2>Tell us what happened</h2></div>
      <form onSubmit={diagnose}><label htmlFor="repo">Public GitHub repository</label><input id="repo" type="url" placeholder="https://github.com/owner/repository" value={repo} onChange={e => setRepo(e.target.value)} required disabled={busy}/><label htmlFor="bug">Bug description</label><textarea id="bug" placeholder="What did you expect? What happened instead? Include steps to reproduce and any error messages." minLength={10} maxLength={5000} value={bug} onChange={e => setBug(e.target.value)} required disabled={busy}/><div className="hint">Be specific. A useful symptom is the start of a useful diagnosis.</div><button disabled={busy}>{busy ? 'Preparing triage…' : 'Diagnose repository ↗'}</button><p className="disclosure">Demo only: no repository is fetched and no AI model is called.</p>{error && <div className="error" role="alert">{error}</div>}</form>
    </section><section className="card report" aria-live="polite" aria-busy={busy}><div className="section-title"><span className="number">02</span><h2>Your triage report</h2></div>{result ? <><span className="pill">MOCK DIAGNOSIS</span><h3>{result.title}</h3><p>{result.summary}</p><p className="repository">{result.repo_url}</p><h4>Suggested investigation</h4><ol>{result.steps.map(step => <li key={step}>{step}</li>)}</ol><div className="note">{result.disclaimer}</div></> : <div className="empty"><span className="pulse">✚</span><h3>{busy ? 'Organizing the symptoms' : 'Ready when you are'}</h3><p>Your suggested investigation steps will appear here after you submit a bug report.</p><div className="tags"><span>Reproduce</span><span>Investigate</span><span>Verify</span></div></div>}</section></div>
    <footer><span>RepoMedic · Nebius × NVIDIA hackathon project</span><span>Next up: Nebius + Nemotron</span></footer>
  </main>;
}
createRoot(document.getElementById('root')).render(<App/>);
