# Jira-Outlook Reminder Automation - Design Document

## Context
AppSec and SRE teams use Jira extensively for project management but often miss important milestones because ticket dates don't automatically sync to their Outlook calendars. This automation bridges the gap between Jira project management and Outlook calendar scheduling.

### Background
- Teams manage 200+ active Jira tickets across multiple projects
- Each engineer maintains their own Outlook calendar for time management
- Current process requires manual calendar entry for each ticket with dates
- Missed deadlines impact sprint completion rates and stakeholder trust

### Constraints
- Must work with both Jira Cloud and Jira Server
- Must support Office 365 (Microsoft Graph API)
- Should not require additional infrastructure (can run as scheduled job)
- Must handle API rate limits gracefully
- Must protect sensitive credentials

### Stakeholders
- **Primary Users**: AppSec engineers, SRE team members
- **Administrators**: Team leads who configure the automation
- **Affected Systems**: Jira Cloud, Office 365, AWS (for credential storage)

## Goals / Non-Goals

### Goals
- Automatically create Outlook calendar events for Jira tickets with planned start/end dates
- Keep calendar events synchronized with Jira ticket updates
- Remove calendar events when tickets are completed or deleted
- Support filtering by project, assignee, and custom fields
- Provide audit trail of all calendar operations
- Handle API failures gracefully with retry logic

### Non-Goals
- Bi-directional sync (Outlook → Jira) - one-way only (Jira → Outlook)
- Real-time synchronization (polling/scheduled sync is acceptable)
- Support for non-Office 365 email systems (Google Calendar, etc.)
- Advanced calendar features (recurring events, attendees, attachments)
- GUI application (CLI-only for initial version)

## Decisions

### Decision 1: Architecture Pattern - Pull-based Polling
**Choice**: Use scheduled polling instead of Jira webhooks

**Rationale**:
- Simpler deployment (no need for publicly accessible webhook endpoint)
- Works with both Jira Cloud and Server
- Easier to implement retry logic and error handling
- Sufficient for use case (5-15 minute sync delay acceptable)

**Alternatives Considered**:
- **Jira Webhooks**: Real-time but requires public endpoint, SSL certificate, and webhook management
- **Event-driven Lambda**: More complex infrastructure, overkill for current scale

**Trade-offs**:
- ✅ Pros: Simpler deployment, no infrastructure changes, works everywhere
- ❌ Cons: Slightly delayed updates (5-15 min), more API calls

### Decision 2: State Management - SQLite Database
**Choice**: Use local SQLite database for sync state tracking

**Rationale**:
- Persistent storage of ticket-to-event mappings
- Fast lookups for change detection
- No external database dependency
- Simple backup/restore with file copy
- Sufficient for expected scale (< 10,000 tickets)

**Alternatives Considered**:
- **In-memory dictionary**: Lost on restart, no persistence
- **JSON file**: Poor performance for large datasets, file corruption risk
- **Redis**: Requires additional infrastructure
- **PostgreSQL/MySQL**: Overkill for current scale

**Schema**:
```sql
CREATE TABLE sync_state (
    jira_key TEXT PRIMARY KEY,
    outlook_event_id TEXT NOT NULL,
    last_synced_at TIMESTAMP NOT NULL,
    jira_updated_at TIMESTAMP NOT NULL,
    ticket_hash TEXT NOT NULL,
    status TEXT NOT NULL
);
```

### Decision 3: Authentication - OAuth 2.0 with MSAL
**Choice**: Use Microsoft Authentication Library (MSAL) for OAuth 2.0 flow

**Rationale**:
- Official Microsoft library with best practices built-in
- Handles token refresh automatically
- Supports various authentication flows (device code, client credentials)
- Well-documented and maintained

**Authentication Flows**:
- **User-based**: Device code flow for personal calendar access
- **App-based**: Client credentials flow for shared calendar access

### Decision 4: Configuration - YAML + Environment Variables
**Choice**: Hybrid configuration using YAML files and environment variables

**Rationale**:
- YAML for non-sensitive settings (filters, preferences)
- Environment variables for credentials (follows 12-factor app principles)
- Easy to version control YAML, keep secrets out of git
- Compatible with Docker, Kubernetes, GitHub Actions

**Example Structure**:
```yaml
# config.yaml
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

### Decision 5: Language - Python 3.8+
**Choice**: Python for implementation

**Rationale**:
- Excellent API client libraries (requests, msal)
- Easy to read and maintain
- Consistent with existing automation scripts in this repo
- Rich ecosystem for testing and error handling

**Key Libraries**:
- `requests` - HTTP client for Jira API
- `msal` - Microsoft Authentication Library
- `python-dotenv` - Environment variable management
- `PyYAML` - Configuration file parsing
- `sqlite3` - State management (built-in)

### Decision 6: Deployment - Multiple Options
**Choice**: Support multiple deployment patterns

**Supported Deployments**:
1. **Cron job** (simplest) - `*/10 * * * * python sync.py`
2. **systemd service** (Linux servers) - continuous daemon mode
3. **GitHub Actions** (cloud-based) - scheduled workflow
4. **AWS Lambda** (optional) - serverless with EventBridge trigger

**Rationale**: Different teams have different infrastructure preferences

## Technical Design

### Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Scheduler (Cron/systemd/GitHub Actions)  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  jira_outlook_sync.py (Main)                │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐ │
│  │ Config      │  │ State Manager│  │ Logging            │ │
│  │ Loader      │  │ (SQLite)     │  │                    │ │
│  └─────────────┘  └──────────────┘  └────────────────────┘ │
│                                                              │
│  ┌──────────────────────────┐  ┌─────────────────────────┐ │
│  │ JiraClient               │  │ OutlookClient           │ │
│  │ - authenticate()         │  │ - authenticate()        │ │
│  │ - fetch_tickets()        │  │ - create_event()        │ │
│  │ - get_ticket_updates()   │  │ - update_event()        │ │
│  └──────────────────────────┘  │ - delete_event()        │ │
│                                 │ - list_events()         │ │
│                                 └─────────────────────────┘ │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ SyncOrchestrator                                     │  │
│  │ - detect_changes()                                   │  │
│  │ - sync_new_tickets()                                 │  │
│  │ - sync_updated_tickets()                             │  │
│  │ - sync_deleted_tickets()                             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
           │                                    │
           ▼                                    ▼
┌──────────────────────┐          ┌─────────────────────────┐
│  Jira Cloud/Server   │          │  Microsoft Graph API    │
│  REST API            │          │  (Office 365)           │
└──────────────────────┘          └─────────────────────────┘
```

### Data Flow

#### Initial Sync
1. Load configuration and authenticate with Jira and Microsoft Graph
2. Execute JQL query to fetch matching Jira tickets
3. For each ticket:
   - Check if already synced (query sync_state table)
   - If new: Create Outlook event and record in sync_state
   - If exists: Skip (will be handled in update flow)
4. Log summary statistics

#### Update Sync (Subsequent Runs)
1. Fetch tickets from Jira that match filter
2. Query sync_state for previously synced tickets
3. Detect changes:
   - **New tickets**: Exist in Jira but not in sync_state
   - **Updated tickets**: Jira updated_at > last_synced_at
   - **Deleted tickets**: Exist in sync_state but not in Jira results
4. Apply changes:
   - Create Outlook events for new tickets
   - Update Outlook events for modified tickets
   - Delete Outlook events for removed tickets
5. Update sync_state table
6. Log summary and any errors

### Error Handling Strategy

#### Retry Logic
- Exponential backoff for transient failures (network errors, rate limits)
- Max 3 retries per API call
- Retry delays: 1s, 4s, 16s

#### Error Categories
1. **Authentication Errors**: Log and exit, require manual intervention
2. **Rate Limit Errors**: Sleep and retry with exponential backoff
3. **Network Errors**: Retry with backoff, skip ticket if still failing
4. **Data Validation Errors**: Log warning, skip ticket, continue processing
5. **Database Errors**: Critical, log and exit

#### Partial Failure Handling
- Process tickets in batches to limit impact of failures
- Continue processing remaining tickets even if one fails
- Log all failures for later review
- Send summary report with success/failure counts

### Security Considerations

#### Credential Storage
- **Development**: `.env` file (gitignored)
- **Production**: AWS Secrets Manager or Azure Key Vault
- **CI/CD**: GitHub Secrets or Azure DevOps secure variables

#### API Permissions
- **Jira**: Read-only access, limited to specific projects
- **Microsoft Graph**: `Calendars.ReadWrite` scope (user-specific)
- **Principle of Least Privilege**: Request minimal required permissions

#### Audit Logging
- Log all calendar operations (create, update, delete)
- Include user, timestamp, ticket key, event ID
- Retain logs for 90 days for compliance

### Performance Optimization

#### Batching
- Fetch Jira tickets in batches of 50-100
- Microsoft Graph supports batch requests (up to 20 requests/batch)

#### Caching
- Cache Jira field metadata (field IDs, custom field names)
- Cache Microsoft Graph tokens (refresh when needed)

#### Rate Limiting
- Jira Cloud: 300 requests/minute (per IP)
- Microsoft Graph: 10,000 requests/10 minutes (per app)
- Implement request throttling to stay under limits

#### Database Indexing
```sql
CREATE INDEX idx_jira_key ON sync_state(jira_key);
CREATE INDEX idx_outlook_event_id ON sync_state(outlook_event_id);
CREATE INDEX idx_last_synced ON sync_state(last_synced_at);
```

## Data Model

### Jira Ticket Fields (Input)
```json
{
  "key": "SRE-123",
  "summary": "Implement new monitoring dashboard",
  "assignee": "john.doe@company.com",
  "status": "In Progress",
  "customfield_10015": "2025-10-20T09:00:00Z",  // Planned Start
  "customfield_10016": "2025-10-25T17:00:00Z",  // Planned End
  "updated": "2025-10-18T14:30:00Z",
  "description": "Create dashboard for..."
}
```

### Outlook Event (Output)
```json
{
  "subject": "[SRE-123] Implement new monitoring dashboard",
  "body": {
    "contentType": "HTML",
    "content": "<a href='https://yourcompany.atlassian.net/browse/SRE-123'>SRE-123</a><br><br>Create dashboard for..."
  },
  "start": {
    "dateTime": "2025-10-20T09:00:00",
    "timeZone": "UTC"
  },
  "end": {
    "dateTime": "2025-10-25T17:00:00",
    "timeZone": "UTC"
  },
  "reminderMinutesBeforeStart": 15,
  "isReminderOn": true,
  "showAs": "busy",
  "categories": ["Jira", "SRE"]
}
```

### Sync State Record
```json
{
  "jira_key": "SRE-123",
  "outlook_event_id": "AAMkAGI2THVSAAA=",
  "last_synced_at": "2025-10-18T14:35:00Z",
  "jira_updated_at": "2025-10-18T14:30:00Z",
  "ticket_hash": "a3f8d9c7e1b2",
  "status": "synced"
}
```

## Migration Plan

### Phase 1: Development (Week 1-2)
- Implement core Jira and Outlook clients
- Implement basic sync logic
- Create configuration templates
- Write unit tests

### Phase 2: Testing (Week 3)
- Test with small dataset (10-20 tickets)
- Validate error handling
- Performance testing with 100+ tickets
- Security review

### Phase 3: Pilot (Week 4)
- Deploy for 5-10 pilot users
- Monitor for issues
- Gather feedback
- Iterate on filtering and configuration

### Phase 4: Rollout (Week 5)
- Document lessons learned
- Create training materials
- Announce to broader team
- Provide support during onboarding

### Rollback Plan
- Stop scheduled sync jobs
- Document any calendar events created (for manual cleanup if needed)
- SQLite database serves as audit trail
- Can manually delete calendar events by category filter

## Open Questions

1. **Q**: Should we support calendar sharing (creating events in other users' calendars)?
   **A**: Not in MVP. Requires different Microsoft Graph permissions and adds complexity. Can be added in v2 if needed.

2. **Q**: How should we handle recurring Jira tickets (e.g., weekly security reviews)?
   **A**: Create individual calendar events for each occurrence based on sprint dates. Investigate recurring event support in v2.

3. **Q**: Should the calendar event link back to Jira?
   **A**: Yes, include Jira URL in event description/location field for easy access.

4. **Q**: What happens if a ticket's planned dates are in the past?
   **A**: Still create the event (for historical tracking) but mark as "free" instead of "busy" so it doesn't block current time.

5. **Q**: Should we support multiple calendar destinations (e.g., team calendar + personal calendar)?
   **A**: Not in MVP. Focus on single calendar per user/configuration. Can be added via multiple config files.

6. **Q**: How to handle tickets with only start date or only end date?
   **A**: 
   - Only start date: Create 1-day event
   - Only end date: Create event ending on that date, starting 1 day before (configurable)
   - No dates: Skip ticket (log warning)

## Risks / Trade-offs

### Risk 1: API Rate Limiting
- **Impact**: Sync failures for large ticket volumes
- **Mitigation**: Implement request throttling, batching, and exponential backoff
- **Acceptance Criteria**: Must handle 500 tickets without hitting rate limits

### Risk 2: Token Expiration
- **Impact**: Authentication failures during long-running syncs
- **Mitigation**: MSAL handles automatic token refresh, implement error handling
- **Acceptance Criteria**: 24-hour continuous operation without manual intervention

### Risk 3: Clock Drift / Timezone Issues
- **Impact**: Events created at wrong times
- **Mitigation**: Always use UTC timestamps, convert to user timezone on display
- **Acceptance Criteria**: Events appear at correct local times for users in different timezones

### Risk 4: Credential Compromise
- **Impact**: Unauthorized access to Jira or Outlook
- **Mitigation**: Use short-lived tokens, audit logging, credential rotation
- **Acceptance Criteria**: Security review approval, no credentials in logs

### Risk 5: Scale Beyond SQLite Capacity
- **Impact**: Performance degradation with >10,000 tickets
- **Mitigation**: Start with SQLite, plan migration path to PostgreSQL if needed
- **Acceptance Criteria**: Sub-second query performance up to 10,000 records

## Success Criteria

### Technical
- [x] Successfully syncs 100+ tickets without errors
- [x] Handles API failures gracefully (retries, logging)
- [x] Sync latency < 5 minutes from Jira update to Outlook event
- [x] Zero credential exposure in logs or code
- [x] Comprehensive test coverage (>80%)

### User Experience
- [x] Simple setup process (<30 minutes from README to working sync)
- [x] Clear error messages for common issues
- [x] Calendar events match Jira ticket information accurately
- [x] Events update when Jira tickets change
- [x] Events deleted when tickets are completed

### Operational
- [x] Runs reliably as scheduled job (99% success rate)
- [x] Monitoring dashboard shows sync statistics
- [x] Alerts configured for critical failures
- [x] Documentation covers common troubleshooting scenarios
- [x] Positive feedback from pilot users (4/5 rating)
