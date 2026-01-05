import React, { useState } from 'react';

const AgentForm = ({ onGenerate, isLoading, generatedCode, onTestResult }) => {
    const [formData, setFormData] = useState({
        name: '',
        prompt: '',
        task: '',
        provider: 'anthropic',
        model: 'claude-3-5-sonnet-20241022',
        stream: false
    });
    const [isExecuting, setIsExecuting] = useState(false);
    const [enhanceLoading, setEnhanceLoading] = useState(false);
    const [enhancementOptions, setEnhancementOptions] = useState(null);
    const [avatarUrl, setAvatarUrl] = useState(null);
    const [avatarLoading, setAvatarLoading] = useState(false);

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => {
            const newData = {
                ...prev,
                [name]: type === 'checkbox' ? checked : value
            };

            // Reset model when provider changes
            if (name === 'provider' && value !== prev.provider) {
                if (value === 'anthropic') {
                    newData.model = 'claude-3-5-sonnet-20241022';
                } else if (value === 'huggingface') {
                    newData.model = 'meta-llama/Meta-Llama-3-8B-Instruct';
                }
            }
            return newData;
        });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onGenerate(formData);
        if (onTestResult) onTestResult(null);
    };

    const handleTestAgent = async () => {
        if (!generatedCode) return;
        setIsExecuting(true);
        if (onTestResult) onTestResult(null);
        try {
            const apiUrl = import.meta.env.DEV ? 'http://localhost:8000/api/execute' : '/api/execute';
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    code: generatedCode,
                    task: formData.task
                }),
            });
            const data = await response.json();
            if (data.status === 'success') {
                if (onTestResult) onTestResult(data.output);
            } else {
                if (onTestResult) onTestResult(`Error: ${data.detail}`);
            }
        } catch (error) {
            if (onTestResult) onTestResult(`Error: ${error.message}`);
        } finally {
            setIsExecuting(false);
        }
    };

    const handleEnhance = async () => {
        if (!formData.prompt) return;
        setEnhanceLoading(true);
        setEnhancementOptions(null);
        try {
            const apiUrl = import.meta.env.DEV ? 'http://localhost:8000/api/enhance-prompt' : '/api/enhance-prompt';
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    keyword: formData.prompt,
                    provider: formData.provider,
                    model: formData.model
                }),
            });
            const data = await response.json();
            if (data.status === 'success') {
                setEnhancementOptions(data.options);
            } else {
                alert(`Error: ${data.detail}`);
            }
        } catch (error) {
            alert(`Error: ${error.message}`);
        } finally {
            setEnhanceLoading(false);
        }
    };

    const handleGenerateAvatar = async () => {
        if (!formData.prompt) {
            alert("Please enter a system prompt first.");
            return;
        }
        setAvatarLoading(true);
        try {
            const apiUrl = import.meta.env.DEV ? 'http://localhost:8000/api/generate-avatar' : '/api/generate-avatar';
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: `Avatar for an AI agent named ${formData.name}. ${formData.prompt}`,
                    name: formData.name
                }),
            });
            const data = await response.json();
            if (data.status === 'success') {
                setAvatarUrl(data.image);
            } else {
                alert(`Error: ${data.detail}`);
            }
        } catch (error) {
            alert(`Error generating avatar: ${error.message}`);
        } finally {
            setAvatarLoading(false);
        }
    };

    return (
        <div className="card">
            <h2 style={{ marginBottom: '1.5rem' }}>Configure Agent</h2>
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <label htmlFor="name">Agent Name</label>
                        <button
                            type="button"
                            onClick={handleGenerateAvatar}
                            disabled={avatarLoading || !formData.prompt}
                            style={{
                                padding: '0.25rem 0.5rem',
                                fontSize: '0.75rem',
                                background: 'var(--accent-primary)',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                opacity: avatarLoading || !formData.prompt ? 0.5 : 1
                            }}
                        >
                            {avatarLoading ? 'Generating...' : '🎨 Gen Avatar'}
                        </button>
                    </div>
                    <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
                        <input
                            type="text"
                            id="name"
                            name="name"
                            value={formData.name}
                            onChange={handleChange}
                            placeholder="e.g., CodeReviewer"
                            required
                            style={{ flex: 1 }}
                        />
                        {avatarUrl && (
                            <div style={{
                                width: '50px',
                                height: '50px',
                                borderRadius: '50%',
                                overflow: 'hidden',
                                border: '2px solid var(--accent-primary)',
                                flexShrink: 0
                            }}>
                                <img src={avatarUrl} alt="Agent Avatar" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                            </div>
                        )}
                    </div>
                </div>

                <div className="form-group">
                    <label htmlFor="provider">Provider</label>
                    <select
                        id="provider"
                        name="provider"
                        value={formData.provider}
                        onChange={handleChange}
                    >
                        <option value="anthropic">Anthropic</option>
                        <option value="huggingface">Hugging Face</option>
                    </select>
                </div>

                <div className="form-group" style={{
                    background: 'rgba(59, 130, 246, 0.05)',
                    padding: '1rem',
                    borderRadius: '0.5rem',
                    border: '1px solid rgba(59, 130, 246, 0.2)',
                    marginTop: '0.5rem',
                    marginBottom: '1.5rem'
                }}>
                    <label htmlFor="model" style={{ color: 'var(--accent-primary)', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span>🧠</span> Model
                    </label>
                    <select
                        id="model"
                        name="model"
                        value={formData.model}
                        onChange={handleChange}
                        style={{ background: 'rgba(15, 23, 42, 0.8)' }}
                    >
                        {formData.provider === 'anthropic' ? (
                            <>
                                <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet (Latest)</option>
                                <option value="claude-3-5-haiku-20241022">Claude 3.5 Haiku</option>
                                <option value="claude-3-opus-20240229">Claude 3 Opus</option>
                                <option value="claude-3-haiku-20240307">Claude 3 Haiku (Legacy)</option>
                            </>
                        ) : (
                            <>
                                <option value="meta-llama/Meta-Llama-3-8B-Instruct">Meta Llama 3 8B Instruct</option>
                                <option value="mistralai/Mistral-7B-Instruct-v0.3">Mistral 7B Instruct v0.3</option>
                            </>
                        )}
                    </select>
                </div>

                <div className="form-group">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                        <label htmlFor="prompt" style={{ margin: 0 }}>System Prompt</label>
                        <button
                            type="button"
                            onClick={handleEnhance}
                            disabled={enhanceLoading || !formData.prompt}
                            style={{
                                padding: '0.25rem 0.75rem',
                                fontSize: '0.875rem',
                                background: 'transparent',
                                border: '1px solid var(--accent-primary)',
                                color: 'var(--accent-primary)',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                opacity: enhanceLoading || !formData.prompt ? 0.5 : 1
                            }}
                        >
                            {enhanceLoading ? 'Enhancing...' : '✨ Enhance'}
                        </button>
                    </div>
                    <textarea
                        id="prompt"
                        name="prompt"
                        value={formData.prompt}
                        onChange={handleChange}
                        placeholder="You are a helpful AI assistant... (or enter a keyword)"
                        rows="4"
                        required
                    />
                    {enhancementOptions && (
                        <div style={{
                            marginTop: '1rem',
                            display: 'grid',
                            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                            gap: '1rem'
                        }}>
                            {Object.entries(enhancementOptions).map(([key, option]) => (
                                <div key={key} style={{
                                    background: 'rgba(59, 130, 246, 0.1)',
                                    border: '1px solid rgba(59, 130, 246, 0.2)',
                                    borderRadius: '0.5rem',
                                    padding: '1rem',
                                    display: 'flex',
                                    flexDirection: 'column'
                                }}>
                                    <h4 style={{ margin: '0 0 0.5rem 0', color: 'var(--accent-primary)' }}>Option {key}</h4>

                                    <div style={{ marginBottom: '0.5rem' }}>
                                        <div style={{ fontSize: '0.75rem', fontWeight: 'bold', color: '#888', textTransform: 'uppercase' }}>System Prompt</div>
                                        <p style={{ fontSize: '0.875rem', margin: '0.25rem 0 0.5rem', whiteSpace: 'pre-wrap', maxHeight: '100px', overflowY: 'auto' }}>
                                            {typeof option === 'string' ? option : option.prompt}
                                        </p>
                                    </div>

                                    {typeof option !== 'string' && option.task && (
                                        <div style={{ marginBottom: '1rem' }}>
                                            <div style={{ fontSize: '0.75rem', fontWeight: 'bold', color: '#888', textTransform: 'uppercase' }}>Example Task</div>
                                            <p style={{ fontSize: '0.875rem', margin: '0.25rem 0', whiteSpace: 'pre-wrap', maxHeight: '60px', overflowY: 'auto', fontStyle: 'italic' }}>
                                                {option.task}
                                            </p>
                                        </div>
                                    )}

                                    <button
                                        type="button"
                                        onClick={() => {
                                            const newPrompt = typeof option === 'string' ? option : option.prompt;
                                            const newTask = typeof option === 'string' ? '' : option.task;

                                            setFormData(prev => ({
                                                ...prev,
                                                prompt: newPrompt,
                                                task: newTask || prev.task
                                            }));
                                            setEnhancementOptions(null);
                                        }}
                                        style={{
                                            marginTop: 'auto',
                                            width: '100%',
                                            padding: '0.5rem',
                                            background: 'var(--accent-primary)',
                                            color: 'white',
                                            border: 'none',
                                            borderRadius: '4px',
                                            cursor: 'pointer'
                                        }}
                                    >
                                        Use Option {key}
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                <div className="form-group">
                    <label htmlFor="task">Example Task</label>
                    <textarea
                        id="task"
                        name="task"
                        value={formData.task}
                        onChange={handleChange}
                        placeholder="Review this code for bugs..."
                        rows="3"
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="docs_path">Knowledge Base Path (Optional)</label>
                    <input
                        type="text"
                        id="docs_path"
                        name="docs_path"
                        value={formData.docs_path || ''}
                        onChange={handleChange}
                        placeholder="/path/to/documents (for RAG)"
                    />
                </div>

                <div className="form-group checkbox-group">
                    <label>
                        <input
                            type="checkbox"
                            name="stream"
                            checked={formData.stream}
                            onChange={handleChange}
                        />
                        Stream Response
                    </label>
                </div>

                <div style={{ display: 'flex', gap: '1rem' }}>
                    <button type="submit" className="btn-primary" disabled={isLoading}>
                        {isLoading ? 'Generating...' : 'Generate Agent'}
                    </button>
                    {generatedCode && (
                        <button
                            type="button"
                            className="btn-secondary"
                            onClick={handleTestAgent}
                            disabled={isExecuting}
                            style={{ backgroundColor: '#6c757d', color: 'white', border: 'none', padding: '0.75rem 1.5rem', borderRadius: '4px', cursor: 'pointer' }}
                        >
                            {isExecuting ? 'Running...' : 'Test Agent'}
                        </button>
                    )}
                </div>
            </form>

        </div >
    );
};

export default AgentForm;
