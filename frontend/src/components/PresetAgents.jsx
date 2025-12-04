import React from 'react';

const PRESETS = [
    {
        id: 'code-reviewer',
        name: 'Code Reviewer',
        icon: '🔍',
        description: 'Expert code reviewer that analyzes code for bugs, security issues, and improvements',
        config: {
            name: 'CodeReviewer',
            prompt: 'You are an expert code reviewer specializing in Python, JavaScript, and TypeScript. You analyze code for bugs, security vulnerabilities, performance issues, and code quality. You provide constructive feedback with specific suggestions for improvement.',
            task: 'Review this Python function for bugs and suggest improvements:\n\ndef calculate_total(items):\n    total = 0\n    for item in items:\n        total += item.price\n    return total',
            provider: 'anthropic',
            model: 'claude-3-5-sonnet-20241022',
            stream: false
        }
    },
    {
        id: 'data-analyst',
        name: 'Data Analyst',
        icon: '📊',
        description: 'Data analysis expert that processes datasets and provides insights and visualizations',
        config: {
            name: 'DataAnalyst',
            prompt: 'You are a data analyst expert specializing in data analysis, statistics, and visualization. You analyze datasets, identify patterns, provide statistical insights, and suggest appropriate visualizations. You work with pandas, numpy, and matplotlib.',
            task: 'Analyze this CSV dataset and provide summary statistics:\n\nimport pandas as pd\ndf = pd.read_csv("sales_data.csv")\n# Analyze sales trends, top products, and revenue by region',
            provider: 'anthropic',
            model: 'claude-3-5-sonnet-20241022',
            stream: false
        }
    },
    {
        id: 'copilot-helper',
        name: 'GitHub Copilot Helper',
        icon: '🤖',
        description: 'AI coding assistant that helps with code generation, debugging, and best practices',
        config: {
            name: 'GitHubCopilotHelper',
            prompt: 'You are a helpful GitHub Copilot assistant that helps developers write better code. You provide code suggestions, explain code patterns, help with debugging, and suggest best practices. You understand multiple programming languages and can assist with code reviews, refactoring, and implementation.',
            task: 'Help me write a Python function to calculate the factorial of a number using recursion, with proper error handling.',
            provider: 'anthropic',
            model: 'claude-3-5-sonnet-20241022',
            stream: false
        }
    }
];

const PresetAgents = ({ onSelectPreset }) => {
    return (
        <div style={{
            marginBottom: '2rem',
            padding: '1.5rem',
            background: 'var(--glass-bg)',
            borderRadius: '0.75rem',
            border: '1px solid var(--glass-border)'
        }}>
            <h3 style={{
                marginBottom: '1rem',
                fontSize: '1.125rem',
                fontWeight: '600',
                color: 'var(--text-primary)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
            }}>
                <span>⚡</span> Quick Start - Try These Presets
            </h3>
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                gap: '1rem'
            }}>
                {PRESETS.map((preset) => (
                    <button
                        key={preset.id}
                        onClick={() => onSelectPreset(preset.config)}
                        style={{
                            padding: '1rem',
                            background: 'rgba(59, 130, 246, 0.1)',
                            border: '2px solid rgba(59, 130, 246, 0.3)',
                            borderRadius: '0.5rem',
                            cursor: 'pointer',
                            textAlign: 'left',
                            transition: 'all 0.2s ease',
                            color: 'var(--text-primary)'
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.background = 'rgba(59, 130, 246, 0.2)';
                            e.currentTarget.style.borderColor = 'rgba(59, 130, 246, 0.5)';
                            e.currentTarget.style.transform = 'translateY(-2px)';
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.background = 'rgba(59, 130, 246, 0.1)';
                            e.currentTarget.style.borderColor = 'rgba(59, 130, 246, 0.3)';
                            e.currentTarget.style.transform = 'translateY(0)';
                        }}
                    >
                        <div style={{
                            fontSize: '2rem',
                            marginBottom: '0.5rem'
                        }}>
                            {preset.icon}
                        </div>
                        <div style={{
                            fontWeight: '600',
                            fontSize: '1rem',
                            marginBottom: '0.25rem',
                            color: 'var(--text-primary)'
                        }}>
                            {preset.name}
                        </div>
                        <div style={{
                            fontSize: '0.875rem',
                            color: 'var(--text-secondary)',
                            lineHeight: '1.4'
                        }}>
                            {preset.description}
                        </div>
                    </button>
                ))}
            </div>
        </div>
    );
};

export default PresetAgents;

