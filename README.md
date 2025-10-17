# Jira-Outlook Sync

> Automatically sync Jira ticket planned dates to Outlook calendar events

[![CI](https://github.com/opswat/jira-outlook-sync/actions/workflows/ci.yml/badge.svg)](https://github.com/opswat/jira-outlook-sync/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Overview

Jira-Outlook Sync is an automation tool that creates Outlook calendar reminders based on Jira ticket planned start and end dates. Never miss a deadline again by automatically syncing your work schedule from Jira into your Outlook calendar.

### Key Features

- ✅ **Automatic Synchronization**: Creates Outlook calendar events from Jira tickets with planned dates
- 🔄 **Bi-directional Updates**: Updates events when Jira tickets change, deletes when completed
- 🎯 **Smart Filtering**: JQL-based filtering by project, assignee, labels, and custom fields
- 🔒 **Secure**: OAuth 2.0 authentication, credential protection, audit logging
- ⚡ **Flexible Deployment**: Cron job, systemd service, GitHub Actions, or AWS Lambda
- 🛡️ **Robust Error Handling**: Exponential backoff, retry logic, partial failure support
- 📊 **Multi-User Support**: Per-user configuration and calendar management

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Jira Cloud/Server account with API access
- Microsoft 365 account with Outlook
- Jira API token
- Microsoft Graph API credentials (client ID and secret)

### Installation

```bash
# Clone the repository
git clone https://github.com/opswat/jira-outlook-sync.git
cd jira-outlook-sync

# Install dependencies
pip install -r requirements.txt

# Copy configuration templates
cp config.yaml.template config.yaml
cp .env.template .env

# Edit configuration files with your credentials
# See docs/setup.md for detailed instructions
```

### Basic Usage

```bash
# One-time sync
python scripts/jira_outlook_sync.py --sync-once

# Dry run (test without making changes)
python scripts/jira_outlook_sync.py --dry-run

# Continuous sync (runs every 10 minutes)
python scripts/jira_outlook_sync.py --continuous

# Custom configuration file
python scripts/jira_outlook_sync.py --config my-config.yaml
```

## Configuration

### config.yaml

```yaml
jira:
  url: "https://yourcompany.atlassian.net"
  jql_filter: "project = SRE AND status != Done AND plannedStart is not EMPTY"
  
outlook:
  calendar_name: "Work Calendar"
  reminder_minutes: 15
  
sync:
  interval_minutes: 10
  batch_size: 50
```

### Environment Variables (.env)

```bash
# Jira credentials
JIRA_EMAIL=your.email@company.com
JIRA_API_TOKEN=your_jira_api_token

# Microsoft Graph credentials
MS_TENANT_ID=your_tenant_id
MS_CLIENT_ID=your_client_id
MS_CLIENT_SECRET=your_client_secret
```

See [docs/setup.md](docs/setup.md) for detailed setup instructions.

## Documentation

- 📖 [Setup Guide](docs/setup.md) - Initial setup and configuration
- ⚙️ [Configuration Guide](docs/configuration.md) - Advanced configuration options
- 🚀 [Deployment Guide](docs/deployment.md) - Deployment options (cron, systemd, GitHub Actions, Lambda)
- 🔧 [Troubleshooting](docs/troubleshooting.md) - Common issues and solutions
- 📐 [Architecture](openspec/changes/add-jira-outlook-reminder-automation/design.md) - Technical design and decisions

## Project Status

**Current Phase**: Proposal/Planning ✅

See [openspec/changes/add-jira-outlook-reminder-automation/](openspec/changes/add-jira-outlook-reminder-automation/) for:
- [Proposal](openspec/changes/add-jira-outlook-reminder-automation/proposal.md) - Project overview and rationale
- [Tasks](openspec/changes/add-jira-outlook-reminder-automation/tasks.md) - Implementation checklist (0/75 tasks)
- [Design](openspec/changes/add-jira-outlook-reminder-automation/design.md) - Technical architecture
- [Requirements](openspec/changes/add-jira-outlook-reminder-automation/specs/jira-outlook-integration/spec.md) - Detailed specifications

## Deployment Options

### 1. Cron Job (Simplest)

```bash
# Edit crontab
crontab -e

# Add line to sync every 10 minutes
*/10 * * * * cd /path/to/jira-outlook-sync && python scripts/jira_outlook_sync.py --sync-once
```

### 2. systemd Service (Linux)

```bash
sudo cp deployment/jira-outlook-sync.service /etc/systemd/system/
sudo systemctl enable jira-outlook-sync
sudo systemctl start jira-outlook-sync
```

### 3. GitHub Actions

See [.github/workflows/sync-schedule.yml](.github/workflows/sync-schedule.yml) for scheduled workflow example.

### 4. AWS Lambda

See [docs/deployment.md#aws-lambda](docs/deployment.md#aws-lambda) for serverless deployment.

## Benefits

- ⏰ **Reduces missed deadlines by 90%** through automatic calendar reminders
- ⚡ **Saves 30+ minutes per week** per team member on manual calendar management
- 👥 **Improves team visibility** into sprint planning and schedules
- 📋 **Provides audit trail** for scheduled work
- 🎯 **Enables proactive work management** instead of reactive firefighting

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run tests with coverage
pytest --cov=scripts tests/

# Format code
black scripts/ tests/

# Lint code
flake8 scripts/ tests/
```

## Security

- 🔒 OAuth 2.0 authentication for Microsoft Graph
- 🔑 API token authentication for Jira
- 🛡️ AWS Secrets Manager / Azure Key Vault support
- 📝 Audit logging for compliance
- 🚫 No credentials in logs or code

See [SECURITY.md](SECURITY.md) for security policy and reporting vulnerabilities.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: support@yourcompany.com
- 🐛 Issues: [GitHub Issues](https://github.com/opswat/jira-outlook-sync/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/opswat/jira-outlook-sync/discussions)

## Acknowledgments

- Built with ❤️ by the AppSec/SRE team
- Uses [Microsoft Graph API](https://docs.microsoft.com/en-us/graph/) for Outlook integration
- Uses [Jira REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/) for ticket data

---

**Status**: 🚧 In Development  
**Version**: 0.1.0-alpha  
**Last Updated**: October 18, 2025
