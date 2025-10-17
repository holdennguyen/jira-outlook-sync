# Project Context

## Purpose
Jira-Outlook Sync is an automation tool that synchronizes Jira ticket planned dates to Outlook calendar events, helping teams stay on top of deadlines by automatically creating calendar reminders.

## Tech Stack
- **Language**: Python 3.8+
- **Jira Integration**: Jira REST API (Cloud/Server)
- **Outlook Integration**: Microsoft Graph API, MSAL (Microsoft Authentication Library)
- **State Management**: SQLite
- **Configuration**: YAML, Environment Variables
- **Testing**: pytest, unittest
- **Deployment**: Cron, systemd, GitHub Actions, AWS Lambda

## Project Conventions

### Code Style
- **Python Style**: PEP 8 compliant
- **Formatting**: Black (line length 100)
- **Linting**: Flake8, pylint
- **Type Hints**: Use type annotations for all functions
- **Docstrings**: Google-style docstrings for all public functions and classes

### Architecture Patterns
- **Separation of Concerns**: Separate modules for Jira client, Outlook client, sync orchestrator
- **Dependency Injection**: Pass dependencies explicitly rather than using globals
- **Configuration**: Centralized configuration loading with validation
- **Error Handling**: Custom exception hierarchy, comprehensive logging
- **State Management**: SQLite for persistence, indexed queries for performance

### Testing Strategy
- **Unit Tests**: Test individual components in isolation (>80% coverage)
- **Integration Tests**: Test Jira and Outlook API interactions with mocks
- **End-to-End Tests**: Test full sync workflow with test data
- **Fixtures**: Use pytest fixtures for common test setup
- **Mocking**: Mock external API calls to avoid rate limits and dependencies

### Git Workflow
- **Branching**: 
  - `main` - stable production code
  - `develop` - integration branch
  - `feature/*` - feature branches
  - `bugfix/*` - bug fix branches
- **Commits**: Conventional commits format (feat:, fix:, docs:, test:, refactor:)
- **Pull Requests**: Required for all changes, must pass CI/CD
- **Code Review**: At least one approval required

### Directory Structure
```
jira-outlook-sync/
├── scripts/
│   ├── jira_outlook_sync.py      # Main sync script
│   ├── jira_client.py            # Jira API client
│   ├── outlook_client.py         # Microsoft Graph API client
│   ├── sync_orchestrator.py     # Sync coordination logic
│   ├── state_manager.py         # SQLite state management
│   └── config_loader.py         # Configuration management
├── tests/
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── fixtures/                # Test fixtures and data
├── docs/
│   ├── setup.md                 # Setup instructions
│   ├── configuration.md         # Configuration guide
│   ├── deployment.md            # Deployment options
│   └── troubleshooting.md       # Common issues and solutions
├── .github/workflows/
│   ├── ci.yml                   # CI/CD pipeline
│   └── sync-schedule.yml        # Optional scheduled sync workflow
├── openspec/                    # OpenSpec specifications
├── config.yaml.template         # Configuration template
├── .env.template                # Environment variables template
├── requirements.txt             # Python dependencies
├── requirements-dev.txt         # Development dependencies
├── .gitignore                   # Git ignore rules
├── LICENSE                      # MIT License
└── README.md                    # Project overview
```

## Domain Context

### Jira Integration
- **Supported Versions**: Jira Cloud, Jira Server 8.x+
- **Authentication**: API tokens (Cloud), Basic auth (Server)
- **Query Language**: JQL (Jira Query Language)
- **Custom Fields**: Support for custom field mapping (e.g., plannedStart, plannedEnd)
- **Rate Limits**: 300 requests/minute (Cloud), varies by server configuration

### Outlook/Microsoft Graph
- **API Version**: Microsoft Graph v1.0
- **Authentication**: OAuth 2.0 (device code flow, client credentials)
- **Scopes Required**: `Calendars.ReadWrite`, `User.Read`
- **Rate Limits**: 10,000 requests/10 minutes per application
- **Batch Support**: Up to 20 requests per batch

### Sync Logic
- **Polling Interval**: Configurable (default: 10 minutes)
- **State Tracking**: SQLite database with ticket-to-event mapping
- **Change Detection**: Compare Jira updated_at timestamp with last_synced_at
- **Conflict Resolution**: Jira is source of truth, Outlook events updated to match

## Important Constraints

### Technical Constraints
- No real-time synchronization (polling-based with configurable interval)
- One-way sync only (Jira → Outlook, not bidirectional)
- SQLite database limited to ~10,000 tickets (migration to PostgreSQL if needed)
- Must handle API rate limits gracefully
- No GUI (command-line interface only for MVP)

### Security Constraints
- Never log credentials or tokens
- Credentials must be stored in environment variables or secret managers
- OAuth tokens cached in memory only, not persisted to disk
- Audit logging required for compliance (90-day retention)
- HTTPS required for all API communications

### Business Constraints
- Must work with existing Jira and Office 365 deployments
- No additional infrastructure required (can run on existing servers)
- Must support multiple users with separate configurations
- Must be self-service (users can configure without admin help)

## External Dependencies

### Required Services
- **Jira Cloud/Server**: Source of ticket data
- **Microsoft 365**: Outlook calendar destination
- **Optional**: AWS Secrets Manager or Azure Key Vault for credential storage

### Python Libraries
- `requests` - HTTP client for Jira API
- `msal` - Microsoft Authentication Library
- `python-dotenv` - Environment variable management
- `PyYAML` - YAML configuration parsing
- `sqlite3` - Built-in SQLite support

### Development Dependencies
- `pytest` - Testing framework
- `pytest-cov` - Code coverage
- `black` - Code formatting
- `flake8` - Linting
- `mypy` - Type checking
- `responses` - HTTP mocking for tests

## Logging and Monitoring

### Logging Levels
- **DEBUG**: API requests/responses, detailed flow
- **INFO**: Sync operations (created/updated/deleted events)
- **WARNING**: Skipped tickets, minor issues
- **ERROR**: API failures, authentication errors
- **CRITICAL**: Database errors, unrecoverable failures

### Metrics to Track
- Tickets processed per sync
- Events created/updated/deleted
- API call counts and latency
- Error rates by type
- Sync duration

### Monitoring Recommendations
- Health check endpoint (if running as service)
- Alerts on consecutive failures (3+)
- Dashboard for sync statistics
- Log aggregation (CloudWatch, Datadog, etc.)

## Performance Targets
- **Sync Latency**: <5 minutes from Jira update to Outlook event
- **Throughput**: Handle 500+ tickets per sync run
- **Database Queries**: <100ms per query (indexed)
- **API Error Rate**: <1%
- **Availability**: 99% uptime for scheduled syncs
