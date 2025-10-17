# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it privately.

### How to Report

1. **DO NOT** open a public GitHub issue
2. Email security concerns to: security@yourcompany.com
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Initial Response**: Within 48 hours
- **Status Update**: Within 5 business days
- **Resolution Timeline**: Depends on severity

## Security Best Practices

### Credential Management

- **Never commit credentials** to the repository
- Use environment variables or secret managers (AWS Secrets Manager, Azure Key Vault)
- Rotate credentials regularly
- Use OAuth 2.0 tokens with appropriate scopes

### API Security

- **HTTPS Only**: All API communications must use HTTPS
- **Token Storage**: Store tokens in memory only, never persist to disk
- **Rate Limiting**: Implement request throttling to prevent abuse
- **Audit Logging**: Log all calendar operations for compliance

### Code Security

- Keep dependencies up to date
- Run security scans: `pip install safety && safety check`
- Use type hints to catch type-related bugs
- Validate all user inputs
- Handle errors gracefully without exposing sensitive data

### Deployment Security

- Use least privilege principle for API permissions
- Enable audit logging in production
- Monitor for suspicious activity
- Implement alerting for security events

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.x.x   | :white_check_mark: |

## Known Security Considerations

- **Credential Storage**: Use AWS Secrets Manager or Azure Key Vault in production
- **Token Refresh**: MSAL handles automatic token refresh
- **API Rate Limits**: Implement exponential backoff to avoid rate limit abuse
- **Database Security**: SQLite database contains only non-sensitive mapping data

## Security Updates

Security updates will be released as patch versions and announced via:
- GitHub Security Advisories
- Release notes
- Email to maintainers

## Compliance

This project includes:
- Audit logging (90-day retention)
- Credential protection
- HTTPS enforcement
- No PII/PHI storage
