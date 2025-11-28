import React, { useState } from 'react';

const AgentForm = ({ onGenerate, isLoading }) => {
    const [formData, setFormData] = useState({
        name: '',
        prompt: '',
        task: '',
        model: 'claude-3-5-sonnet-20241022'
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onGenerate(formData);
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
                    <label htmlFor="model">Model</label>
                    <select
                        id="model"
                        name="model"
                        value={formData.model}
                        onChange={handleChange}
                    >
                        <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet (Latest)</option>
                        <option value="claude-3-opus-20240229">Claude 3 Opus</option>
                        <option value="claude-3-haiku-20240307">Claude 3 Haiku</option>
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

                <button type="submit" className="btn-primary" disabled={isLoading}>
                    {isLoading ? 'Generating...' : 'Generate Agent'}
                </button>
            </form>
        </div>
    );
};

export default AgentForm;
