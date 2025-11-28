import React from 'react';

const CodePreview = ({ code, path }) => {
    if (!code) {
        return (
            <div className="card" style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)' }}>
                <p>Generated code will appear here</p>
            </div>
        );
    }

    return (
        <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h2>Preview</h2>
                {path && <span className="status-badge status-success">Saved to {path.split('/').pop()}</span>}
            </div>
            <pre>
                <code>{code}</code>
            </pre>
        </div>
    );
};

export default CodePreview;
