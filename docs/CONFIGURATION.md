# Configuration Guide

LLM Agent Builder uses a comprehensive YAML-based configuration system that supports environment-specific settings, hierarchical configuration, and environment variable overrides.

## Table of Contents

- [Quick Start](#quick-start)
- [Configuration Loading](#configuration-loading)
- [Configuration Structure](#configuration-structure)
- [Environment-Specific Configuration](#environment-specific-configuration)
- [Environment Variable Overrides](#environment-variable-overrides)
- [CLI Commands](#cli-commands)
- [Examples](#examples)

## Quick Start

### 1. Using Default Configuration

LLM Agent Builder works out of the box with sensible defaults:

\`\`\`bash
llm-agent-builder generate
\`\`\`

### 2. View Current Configuration

\`\`\`bash
llm-agent-builder config show
\`\`\`

### 3. Generate Custom Configuration

\`\`\`bash
llm-agent-builder config generate --output my-config.yaml
\`\`\`

### 4. Use Custom Configuration

\`\`\`bash
llm-agent-builder --config my-config.yaml generate
\`\`\`

## Configuration Loading Priority

1. **Environment variables** (highest priority)
2. **Environment-specific config file** (\`config/{ENV}.yaml\`)
3. **Default config file** (\`config/default.yaml\`)
4. **Built-in defaults** (in code)

## Environment Variable Overrides

Override any configuration value using double underscore notation:

\`\`\`bash
# Server settings
SERVER__PORT=8080
SERVER__HOST="localhost"

# Provider settings
PROVIDERS__GOOGLE__RATE_LIMIT=50
PROVIDERS__ANTHROPIC__DEFAULT_MODEL="claude-3-opus"

# Database settings
DATABASE__POOL_SIZE=10

# Top-level settings
ENVIRONMENT="development"
\`\`\`

## CLI Commands

\`\`\`bash
# Show configuration
llm-agent-builder config show

# Validate configuration
llm-agent-builder config validate --file config/production.yaml

# Generate configuration
llm-agent-builder config generate --output my-config.yaml

# Use custom configuration
llm-agent-builder --config my-config.yaml web
\`\`\`

For complete documentation, see [docs/CONFIGURATION.md](./CONFIGURATION.md).
