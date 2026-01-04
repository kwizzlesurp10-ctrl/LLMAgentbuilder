import React, { useState, useEffect } from 'react';
import AgentForm from './components/AgentForm';
import CodePreview from './components/CodePreview';
import FlowBuilder from './pages/FlowBuilder';

function App() {
  const [view, setView] = useState('classic'); // 'classic' or 'visual'
  const [generatedCode, setGeneratedCode] = useState(null);
  const [generatedPath, setGeneratedPath] = useState(null);
  const [testResult, setTestResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [theme, setTheme] = useState('dark');

  useEffect(() => {
    // Load theme from localStorage or default to dark
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
    document.documentElement.setAttribute('data-theme', savedTheme);
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
  };

  const handleGenerate = async (formData) => {
    setIsLoading(true);
    setError(null);
    setTestResult(null);
    try {
      // Use relative URL for production (served by same origin)
      // For dev (different ports), we might need full URL, but let's assume proxy or CORS handles it.
      // Since we enabled CORS for *, localhost:8000 works for dev.
      // In production (Docker), it will be same origin.
      const apiUrl = import.meta.env.DEV ? 'http://localhost:8000/api/generate' : '/api/generate';
      console.log('Using API URL:', apiUrl);

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const data = await response.json();
      setGeneratedCode(data.code);
      setGeneratedPath(null); // No server path anymore

      // Trigger download
      const blob = new Blob([data.code], { type: 'text/x-python' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = data.filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container" style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header className="header" style={{ flexShrink: 0 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', marginBottom: '0.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div>
              <h1 style={{ margin: 0 }}>LLM Agent Builder</h1>
              <p style={{ margin: 0, opacity: 0.7 }}>Design, configure, and generate AI agents.</p>
            </div>
            <div style={{ display: 'flex', background: 'var(--glass-bg)', padding: '4px', borderRadius: '8px', border: '1px solid var(--glass-border)' }}>
              <button
                onClick={() => setView('classic')}
                style={{
                  padding: '4px 12px',
                  borderRadius: '6px',
                  border: 'none',
                  background: view === 'classic' ? 'var(--primary-color)' : 'transparent',
                  color: view === 'classic' ? 'white' : 'var(--text-primary)',
                  cursor: 'pointer'
                }}
              >
                Classic
              </button>
              <button
                onClick={() => setView('visual')}
                style={{
                  padding: '4px 12px',
                  borderRadius: '6px',
                  border: 'none',
                  background: view === 'visual' ? 'var(--primary-color)' : 'transparent',
                  color: view === 'visual' ? 'white' : 'var(--text-primary)',
                  cursor: 'pointer'
                }}
              >
                Visual Builder
              </button>
            </div>
          </div>
          <button
            onClick={toggleTheme}
            className="btn-secondary"
            style={{
              padding: '0.5rem 1rem',
              borderRadius: '0.5rem',
              border: '1px solid var(--glass-border)',
              background: 'var(--glass-bg)',
              color: 'var(--text-primary)',
              cursor: 'pointer',
              fontSize: '1.5rem'
            }}
            aria-label="Toggle theme"
          >
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>
        </div>
      </header>

      {view === 'visual' ? (
        <div style={{ flex: 1, overflow: 'hidden' }}>
          <FlowBuilder />
        </div>
      ) : (
        <div style={{ flex: 1, overflow: 'auto', padding: '1rem' }}>
          {error && (
            <div style={{
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.2)',
              color: '#fca5a5',
              padding: '1rem',
              borderRadius: '0.5rem',
              marginBottom: '2rem'
            }}>
              {error}
            </div>
          )}

          <div className="layout">
            <AgentForm
              onGenerate={handleGenerate}
              isLoading={isLoading}
              generatedCode={generatedCode}
              onTestResult={setTestResult}
            />
            <CodePreview
              code={generatedCode}
              path={generatedPath}
              testResult={testResult}
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
