import React, { useState } from 'react';

const CodePreview = ({ code, path }) => {
    const [copied, setCopied] = useState(false);

    const copyToClipboard = () => {
        if (code) {
            navigator.clipboard.writeText(code);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    if (!code) {
        return (
            <div className="card" style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)' }}>
                <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📝</div>
                <p>Generated code will appear here</p>
                <p style={{ fontSize: '0.875rem', marginTop: '0.5rem', opacity: 0.7 }}>Fill out the form and click "Generate Agent"</p>
            </div>
        );
    }

    return (
        <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h2>Code Preview</h2>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    {path && <span className="status-badge status-success">Saved to {path.split('/').pop()}</span>}
                    <button
                        onClick={copyToClipboard}
                        style={{
                            padding: '0.5rem 1rem',
                            borderRadius: '0.5rem',
                            border: '1px solid var(--glass-border)',
                            background: copied ? 'rgba(34, 197, 94, 0.2)' : 'var(--glass-bg)',
                            color: copied ? '#4ade80' : 'var(--text-primary)',
                            cursor: 'pointer',
                            fontSize: '0.875rem',
                            transition: 'all 0.2s ease'
                        }}
                    >
                        {copied ? '✓ Copied!' : '📋 Copy'}
                    </button>
                </div>
            </div>
            <div style={{ position: 'relative' }}>
                <pre style={{ maxHeight: '600px', overflow: 'auto' }}>
                    <code>{code}</code>
                </pre>
            </div>
            <div style={{ marginTop: '1rem', padding: '0.75rem', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                💡 <strong>Tip:</strong> Save this code to a .py file and run it with your API key set.
            </div>
        </div>
    );
};

export default CodePreview;
