import React, { useState, useEffect } from 'react';
import AgentForm from './components/AgentForm';
import CodePreview from './components/CodePreview';
import PresetAgents from './components/PresetAgents';

function App() {
  const [generatedCode, setGeneratedCode] = useState(null);
  const [generatedPath, setGeneratedPath] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [theme, setTheme] = useState('dark');
  const [testResult, setTestResult] = useState(null);
  const [presetData, setPresetData] = useState(null);
  const [isTesting, setIsTesting] = useState(false);
  const [lastTask, setLastTask] = useState(null);

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

  const testAgentWithEngine = async (agentCode, task) => {
    setIsTesting(true);
    setTestResult(null);
    try {
      const apiUrl = import.meta.env.DEV ? 'http://localhost:8000/api/test-agent' : '/api/test-agent';
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          agent_code: agentCode,
          task: task,
          timeout: 60
        }),
      });
      
      const data = await response.json();
      
      // Handle AgentEngine response format
      if (data.status === 'success') {
        const output = data.output || '';
        const executionTime = data.execution_time ? `\n\nExecution time: ${data.execution_time.toFixed(2)}s` : '';
        setTestResult(output + executionTime);
      } else if (data.status === 'error') {
        const errorMsg = data.error || 'Unknown error occurred';
        const executionTime = data.execution_time ? `\n\nExecution time: ${data.execution_time.toFixed(2)}s` : '';
        setTestResult(`Error: ${errorMsg}${executionTime}`);
      } else if (data.status === 'timeout') {
        setTestResult(`Error: Execution timed out after ${data.execution_time || 60} seconds`);
      } else if (data.status === 'api_key_missing') {
        setTestResult(`Error: API key not found. Please set GITHUB_COPILOT_TOKEN or GITHUB_PAT environment variable.`);
      } else {
        setTestResult(`Error: ${data.detail || data.error || 'Unknown error occurred'}`);
      }
    } catch (error) {
      setTestResult(`Error: ${error.message}`);
    } finally {
      setIsTesting(false);
    }
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
      setPresetData(null); // Clear preset data after generation
      setLastTask(formData.task); // Store task for auto-testing

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

      // Automatically test the generated code with AgentEngine
      await testAgentWithEngine(data.code, formData.task);

    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container">
      <header className="header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', marginBottom: '1rem' }}>
          <div>
            <h1>LLM Agent Builder</h1>
            <p>Design, configure, and generate AI agents in seconds.</p>
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

      {(isTesting || testResult) && (
        <div style={{
          background: testResult && testResult.includes('Error') ? 'rgba(239, 68, 68, 0.1)' : testResult ? 'rgba(34, 197, 94, 0.1)' : 'rgba(59, 130, 246, 0.1)',
          border: `1px solid ${testResult && testResult.includes('Error') ? 'rgba(239, 68, 68, 0.2)' : testResult ? 'rgba(34, 197, 94, 0.2)' : 'rgba(59, 130, 246, 0.2)'}`,
          color: testResult && testResult.includes('Error') ? '#fca5a5' : testResult ? '#86efac' : '#93c5fd',
          padding: '1rem',
          borderRadius: '0.5rem',
          marginBottom: '2rem',
          whiteSpace: 'pre-wrap',
          fontFamily: 'monospace',
          fontSize: '0.875rem'
        }}>
          <strong>{isTesting ? '🔄 Auto-Testing Generated Agent...' : '✅ Test Result (Auto-Test):'}</strong>
          {testResult && (
            <pre style={{ margin: '0.5rem 0 0 0', whiteSpace: 'pre-wrap' }}>{testResult}</pre>
          )}
          {isTesting && !testResult && (
            <div style={{ margin: '0.5rem 0 0 0', opacity: 0.7 }}>
              Testing agent functionality with AgentEngine...
            </div>
          )}
        </div>
      )}

      <PresetAgents onSelectPreset={(config) => {
        setPresetData(config);
        setGeneratedCode(null);
        setTestResult(null);
        setError(null);
        // Scroll to form
        setTimeout(() => {
          document.querySelector('form')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
      }} />

      <div className="layout">
        <AgentForm 
          onGenerate={handleGenerate} 
          isLoading={isLoading} 
          generatedCode={generatedCode} 
          onTestResult={setTestResult}
          presetData={presetData}
        />
        <CodePreview code={generatedCode} path={generatedPath} />
      </div>
    </div>
  );
}

export default App;
