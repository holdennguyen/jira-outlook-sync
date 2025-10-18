# Jira-Outlook Reminder Automation

## Overview
This is the OpenSpec proposal for the Jira-Outlook Sync automation. It defines automation to create Outlook calendar reminders based on Jira ticket planned start and end dates, solving the problem of missed deadlines by automatically syncing work schedules from Jira into team members' Outlook calendars.

## Proposal Files

### 📋 [proposal.md](./proposal.md)
**Purpose**: High-level overview of the change
- **Why**: Teams miss deadlines because Jira dates don't sync to calendars
- **What**: Automated Jira → Outlook calendar synchronization
- **Impact**: New capability, no infrastructure changes needed
- **Benefits**: 90% reduction in missed deadlines, 30+ min/week saved per person

### ✅ [tasks.md](./tasks.md)
**Purpose**: Implementation checklist (75 tasks across 12 phases)
- Phase 1-2: Project setup and core integrations (Jira + Outlook)
- Phase 3-4: Sync logic and configuration management
- Phase 5-7: CLI, scheduling, and documentation
- Phase 8-12: Testing, security, monitoring, and rollout

**Status**: 0/75 tasks completed

### 🏗️ [design.md](./design.md)
**Purpose**: Technical architecture and decisions
- **Architecture**: Pull-based polling with SQLite state management
- **Key Decisions**:
  - Polling over webhooks (simpler deployment)
  - SQLite for state (sufficient for <10K tickets)
  - OAuth 2.0 with MSAL (official Microsoft library)
  - YAML + env vars for configuration
  - Python 3.8+ implementation
- **Data Flow**: Jira API → Sync Logic → Microsoft Graph API → Outlook
- **Security**: AWS Secrets Manager, OAuth 2.0, audit logging

### 📐 [specs/jira-outlook-integration/spec.md](./specs/jira-outlook-integration/spec.md)
**Purpose**: Detailed requirements with scenarios (NEW capability)

**Key Requirements**:
1. **Jira Ticket Query** - JQL-based ticket filtering
2. **Outlook Event Creation** - Calendar event generation with reminders
3. **Sync State Tracking** - SQLite database for ticket-to-event mapping
4. **Change Detection** - Identify new/updated/deleted tickets
5. **Error Handling** - Exponential backoff, retry logic, partial failures
6. **Configuration** - YAML + environment variables
7. **Logging** - Audit trail for compliance
8. **Security** - Credential protection, no exposure in logs
9. **Filtering** - Project, assignee, label-based filtering
10. **Dry Run Mode** - Test without modifying calendars
11. **Multi-User Support** - Per-user configuration and calendars
12. **Performance** - Batch processing, database indexing
13. **Timezone Handling** - UTC storage, user timezone display
14. **Monitoring** - Metrics, health checks, alerting

Each requirement includes multiple scenarios with GIVEN/WHEN/THEN format.

## Implementation Status

**Current Phase**: Planning (Proposal Approved ✅)  
**Tasks Completed**: 0/75  
**Next Phase**: Development

## Getting Started

### 1. Review the Proposal
```bash
# View proposal overview
cat proposal.md

# Review technical design
cat design.md

# Check detailed requirements
cat specs/jira-outlook-integration/spec.md

# View implementation checklist
cat tasks.md
```

### 2. Validate with OpenSpec
```bash
# Check proposal validity
openspec validate add-jira-outlook-reminder-automation --strict

# View proposal details
openspec show add-jira-outlook-reminder-automation

# Check task progress
openspec list
```

### 3. Start Implementation
- Follow [tasks.md](./tasks.md) checklist sequentially
- Mark tasks as complete: `- [x]` in tasks.md
- Implement features in `scripts/` directory
- Add tests in `tests/` directory

## Key Features

### Core Functionality
- ✅ Automatic Outlook event creation from Jira tickets with planned dates
- ✅ Update events when Jira tickets change
- ✅ Delete events when tickets are completed
- ✅ Configurable reminders (default 15 min before)
- ✅ JQL-based filtering (project, assignee, labels)

### Deployment Options
1. **Cron job** (simplest) - Every 10 minutes
2. **systemd service** - Continuous daemon mode
3. **GitHub Actions** - Cloud-based scheduled workflow
4. **AWS Lambda** - Serverless with EventBridge

### Security
- OAuth 2.0 for Microsoft Graph (MSAL library)
- API tokens for Jira
- AWS Secrets Manager or Azure Key Vault support
- No credentials in logs or code
- Audit trail for compliance

### Error Handling
- Exponential backoff (1s, 4s, 16s)
- Rate limit detection and throttling
- Partial failure support (continue processing)
- Comprehensive error logging

## Technical Stack

```
┌─────────────────────────────────────────┐
│   Scheduler (Cron/GitHub Actions)       │
└─────────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────┐
│   jira_outlook_sync.py (Python 3.8+)    │
│   - JiraClient (requests)               │
│   - OutlookClient (msal + Graph API)    │
│   - SyncOrchestrator                    │
│   - SQLite State Database               │
└─────────────────────────────────────────┘
          ▼                    ▼
┌──────────────────┐  ┌──────────────────┐
│   Jira Cloud     │  │  Microsoft       │
│   REST API       │  │  Graph API       │
└──────────────────┘  └──────────────────┘
```

## Dependencies
- **Python**: 3.8+
- **Libraries**: requests, msal, python-dotenv, PyYAML
- **APIs**: Jira REST API, Microsoft Graph API
- **Storage**: SQLite (local), AWS Secrets Manager (optional)

## Success Criteria
- ✅ 100+ tickets synced without errors
- ✅ <5 min sync latency
- ✅ 99% reliability as scheduled job
- ✅ Zero credential exposure
- ✅ Positive user feedback (4/5 rating)
- ✅ 80%+ test coverage

## Timeline Estimate
- **Week 1-2**: Development (core features)
- **Week 3**: Testing (unit, integration, performance)
- **Week 4**: Pilot (5-10 users, gather feedback)
- **Week 5**: Rollout (documentation, training, broader deployment)

## Questions?
Refer to the [Open Questions](./design.md#open-questions) section in design.md or contact the proposal author.

---

**Proposal Status**: ✅ Validated  
**Created**: 2025-10-18  
**Change ID**: `add-jira-outlook-reminder-automation`  
**Validation**: `openspec validate add-jira-outlook-reminder-automation --strict`
