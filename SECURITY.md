# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of LLM Agent Builder seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please Do Not

- **Do not** open a public GitHub issue for security vulnerabilities
- **Do not** discuss the vulnerability publicly until it has been addressed

### Please Do

1. **Email us** at [security@example.com](mailto:security@example.com) with:
   - A description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact of the vulnerability
   - Any possible mitigations you've identified

2. **Allow time** for us to respond and address the issue before public disclosure

3. **Work with us** to understand and resolve the issue quickly

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your report within 48 hours
- **Updates**: We will provide regular updates on our progress
- **Timeline**: We aim to resolve critical vulnerabilities within 30 days
- **Credit**: We will credit you for the discovery (unless you prefer to remain anonymous)

## Security Best Practices

### For Users

1. **API Keys**: Never commit API keys to version control
   ```bash
   # Always use environment variables
   export ANTHROPIC_API_KEY=your-key-here
   ```

2. **Environment Files**: Keep `.env` files out of git
   ```gitignore
   .env
   .env.local
   ```

3. **Dependencies**: Keep dependencies up to date
   ```bash
   pip install --upgrade -r requirements.txt
   cd frontend && npm update
   ```

4. **Sandbox Execution**: The built-in sandbox has resource limits
   - 30-second timeout for code execution
   - 100KB code size limit
   - Isolated process execution

5. **Rate Limiting**: API endpoints have rate limits
   - Generation: 20 requests/minute
   - Execution: 10 requests/minute

### For Developers

1. **Input Validation**: Always validate user input
   ```python
   # Example from server/models.py
   @validator('name')
   def validate_name(cls, v):
       if not v or not v.strip():
           raise ValueError("Agent name cannot be empty")
       return v.strip()
   ```

2. **Secure Code Execution**: Use sandboxed execution
   ```python
   # Use subprocess with timeout
   subprocess.run(cmd, timeout=30, capture_output=True)
   ```

3. **CORS Configuration**: Configure CORS appropriately
   ```python
   # In production, specify allowed origins
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourdomain.com"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

4. **Dependency Scanning**: Regularly scan for vulnerabilities
   ```bash
   # Using safety
   pip install safety
   safety check
   
   # Using bandit
   pip install bandit
   bandit -r llm_agent_builder server
   ```

## Security Features

### Current Protections

- **Rate Limiting**: All API endpoints are rate-limited
- **Input Validation**: Pydantic models validate all inputs
- **Sandbox Execution**: Code execution is sandboxed with timeouts
- **Size Limits**: Code and prompt size limits prevent abuse
- **Retry Logic**: Exponential backoff prevents API hammering
- **HTTPS**: Use HTTPS in production deployments

### Planned Improvements

- [ ] Content Security Policy (CSP) headers
- [ ] API key rotation mechanism
- [ ] Enhanced audit logging
- [ ] Two-factor authentication for admin endpoints
- [ ] Automated dependency updates (Dependabot)

## Known Security Considerations

1. **API Key Storage**: Users must protect their API keys
2. **Code Generation**: Generated agents execute with user privileges
3. **Network Access**: Generated agents may make network requests
4. **Resource Usage**: Long-running agents may consume significant resources

## Security Updates

We publish security updates through:

- GitHub Security Advisories
- Release notes in CHANGELOG.md
- GitHub releases with security tags

Subscribe to repository notifications to stay informed.

## Third-Party Dependencies

We regularly audit our dependencies for security vulnerabilities:

- **Python**: anthropic, fastapi, pydantic, and others
- **JavaScript**: React, Vite, TailwindCSS, and others

Run security audits:

```bash
# Python dependencies
pip install safety
safety check

# JavaScript dependencies
cd frontend
npm audit
```

## Compliance

This project handles:

- **API Keys**: Sensitive credential management
- **User Code**: User-generated content execution
- **AI Interactions**: LLM API communications

Users are responsible for:

- Securing their API keys
- Complying with Anthropic/Hugging Face terms of service
- Reviewing generated code before production use
- Protecting generated agents appropriately

## Contact

For security concerns, contact:

- **Email**: [security@example.com](mailto:security@example.com)
- **GitHub**: Open a security advisory on GitHub (preferred for verified issues)

## Acknowledgments

We appreciate the security research community and will acknowledge researchers who report valid vulnerabilities:

- [Your Name] - Description of contribution

---

**Last Updated**: December 2024

Thank you for helping keep LLM Agent Builder secure! 🔒
