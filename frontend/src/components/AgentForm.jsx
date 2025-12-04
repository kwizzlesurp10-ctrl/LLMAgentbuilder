import React, { useState } from 'react';

const AgentForm = ({ onGenerate, isLoading, generatedCode, onTestResult, presetData }) => {
    const [formData, setFormData] = useState({
        name: '',
        prompt: '',
        task: '',
        provider: 'anthropic',
        model: 'claude-3-5-sonnet-20241022',
        stream: false
    });
    const [isExecuting, setIsExecuting] = useState(false);

    // Update form when preset data is provided
    React.useEffect(() => {
        if (presetData) {
            setFormData(presetData);
        }
    }, [presetData]);

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
            const apiUrl = import.meta.env.DEV ? 'http://localhost:8000/api/test-agent' : '/api/test-agent';
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    agent_code: generatedCode,
                    task: formData.task,
                    timeout: 60
                }),
            });
            
            const data = await response.json();
            
            // Handle AgentEngine response format
            if (data.status === 'success') {
                const output = data.output || '';
                const executionTime = data.execution_time ? `\n\nExecution time: ${data.execution_time.toFixed(2)}s` : '';
                if (onTestResult) onTestResult(output + executionTime);
            } else if (data.status === 'error') {
                const errorMsg = data.error || 'Unknown error occurred';
                const executionTime = data.execution_time ? `\n\nExecution time: ${data.execution_time.toFixed(2)}s` : '';
                if (onTestResult) onTestResult(`Error: ${errorMsg}${executionTime}`);
            } else if (data.status === 'timeout') {
                if (onTestResult) onTestResult(`Error: Execution timed out after ${data.execution_time || 60} seconds`);
            } else if (data.status === 'api_key_missing') {
                if (onTestResult) onTestResult(`Error: API key not found. Please set GITHUB_COPILOT_TOKEN or GITHUB_PAT environment variable.`);
            } else {
                // Fallback for other statuses or error responses
                if (onTestResult) onTestResult(`Error: ${data.detail || data.error || 'Unknown error occurred'}`);
            }
        } catch (error) {
            if (onTestResult) onTestResult(`Error: ${error.message}`);
        } finally {
            setIsExecuting(false);
        }
    };

    return (
        <div className="card">
            <h2 style={{ marginBottom: '1.5rem' }}>Configure Agent</h2>
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="name">Agent Name</label>
                    <input
                        type="text"
                        id="name"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        placeholder="e.g., CodeReviewer"
                        required
                    />
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
                    <label htmlFor="prompt">System Prompt</label>
                    <textarea
                        id="prompt"
                        name="prompt"
                        value={formData.prompt}
                        onChange={handleChange}
                        placeholder="You are a helpful AI assistant..."
                        rows="4"
                        required
                    />
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
