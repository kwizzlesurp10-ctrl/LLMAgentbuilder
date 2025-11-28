import React, { useState } from 'react';

const AgentForm = ({ onGenerate, isLoading, generatedCode }) => {
    const [formData, setFormData] = useState({
        name: '',
        prompt: '',
        task: '',
        provider: 'anthropic',
        model: 'claude-3-5-sonnet-20241022',
        stream: false
    });
    const [executionResult, setExecutionResult] = useState(null);
    const [isExecuting, setIsExecuting] = useState(false);

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
        setExecutionResult(null);
    };

    const handleTestAgent = async () => {
        if (!generatedCode) return;
        setIsExecuting(true);
        setExecutionResult(null);
        try {
            const response = await fetch('http://localhost:8000/api/execute', {
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
                setExecutionResult(data.output);
            } else {
                setExecutionResult(`Error: ${data.detail}`);
            }
        } catch (error) {
            setExecutionResult(`Error: ${error.message}`);
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

                <div className="form-group">
                    <label htmlFor="model">Model</label>
                    <select
                        id="model"
                        name="model"
                        value={formData.model}
                        onChange={handleChange}
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

            {executionResult && (
                <div style={{ marginTop: '1.5rem', padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '4px', border: '1px solid #dee2e6' }}>
                    <h3>Execution Result:</h3>
                    <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>{executionResult}</pre>
                </div>
            )}
        </div>
    );
};

export default AgentForm;
