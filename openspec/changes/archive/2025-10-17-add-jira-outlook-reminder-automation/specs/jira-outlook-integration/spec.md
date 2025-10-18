# Jira-Outlook Integration Specification

## ADDED Requirements

### Requirement: Jira Ticket Query
The system SHALL query Jira using JQL (Jira Query Language) to retrieve tickets matching user-defined filters.

#### Scenario: Query tickets with planned dates
- **GIVEN** a configured JQL filter `project = SRE AND plannedStart is not EMPTY`
- **WHEN** the system executes the query
- **THEN** the system SHALL return all tickets matching the criteria
- **AND** each ticket SHALL include key, summary, assignee, status, planned start date, and planned end date

#### Scenario: Handle empty result set
- **GIVEN** a JQL filter that matches no tickets
- **WHEN** the system executes the query
- **THEN** the system SHALL return an empty list
- **AND** the system SHALL log an informational message indicating zero tickets found

#### Scenario: Handle Jira API authentication failure
- **GIVEN** invalid Jira credentials
- **WHEN** the system attempts to query Jira
- **THEN** the system SHALL raise an authentication error
- **AND** the system SHALL log the error with details
- **AND** the system SHALL exit with non-zero status code

### Requirement: Outlook Calendar Event Creation
The system SHALL create Outlook calendar events corresponding to Jira tickets with planned start and end dates.

#### Scenario: Create event for ticket with both start and end dates
- **GIVEN** a Jira ticket `SRE-123` with planned start `2025-10-20T09:00:00Z` and planned end `2025-10-25T17:00:00Z`
- **WHEN** the system processes the ticket
- **THEN** the system SHALL create an Outlook calendar event with:
  - Subject: `[SRE-123] <ticket summary>`
  - Start: `2025-10-20T09:00:00` in user's timezone
  - End: `2025-10-25T17:00:00` in user's timezone
  - Description: Link to Jira ticket and ticket description
  - Reminder: 15 minutes before (configurable)
  - Category: `Jira`

#### Scenario: Create event for ticket with only start date
- **GIVEN** a Jira ticket with planned start date but no end date
- **WHEN** the system processes the ticket
- **THEN** the system SHALL create a 1-day calendar event starting at the planned start date

#### Scenario: Skip ticket without dates
- **GIVEN** a Jira ticket with no planned start or end date
- **WHEN** the system processes the ticket
- **THEN** the system SHALL skip the ticket
- **AND** the system SHALL log a warning indicating the ticket was skipped

#### Scenario: Handle Microsoft Graph API authentication failure
- **GIVEN** invalid Microsoft Graph credentials or expired token
- **WHEN** the system attempts to create a calendar event
- **THEN** the system SHALL attempt token refresh
- **AND** if refresh fails, the system SHALL raise an authentication error
- **AND** the system SHALL log the error and exit

### Requirement: Synchronization State Tracking
The system SHALL maintain a persistent record of which Jira tickets have been synchronized to Outlook events.

#### Scenario: Record successful synchronization
- **GIVEN** a Jira ticket `SRE-123` successfully synchronized to Outlook event `evt-abc-123`
- **WHEN** the synchronization completes
- **THEN** the system SHALL store a record containing:
  - Jira key: `SRE-123`
  - Outlook event ID: `evt-abc-123`
  - Last synced timestamp
  - Jira last updated timestamp
  - Ticket data hash

#### Scenario: Detect previously synced ticket
- **GIVEN** a ticket `SRE-123` that was previously synced
- **WHEN** the system queries the sync state
- **THEN** the system SHALL return the existing sync record
- **AND** the system SHALL use the record to determine if an update is needed

#### Scenario: Persist state across restarts
- **GIVEN** sync state stored in SQLite database
- **WHEN** the system restarts
- **THEN** the system SHALL load all previous sync records from the database
- **AND** the system SHALL continue synchronization without duplicating events

### Requirement: Change Detection and Update
The system SHALL detect changes to Jira tickets and update corresponding Outlook events.

#### Scenario: Detect updated ticket dates
- **GIVEN** a synced ticket `SRE-123` with updated planned dates in Jira
- **WHEN** the system queries for updates
- **THEN** the system SHALL detect the change by comparing Jira updated_at with last_synced_at
- **AND** the system SHALL update the Outlook event with new dates

#### Scenario: Detect ticket status change to Done
- **GIVEN** a synced ticket `SRE-123` marked as Done in Jira
- **WHEN** the system queries for updates
- **THEN** the system SHALL delete the corresponding Outlook event
- **AND** the system SHALL update the sync state to mark the record as deleted

#### Scenario: Detect new ticket matching filter
- **GIVEN** a new Jira ticket `SRE-456` that matches the configured JQL filter
- **WHEN** the system runs synchronization
- **THEN** the system SHALL create a new Outlook event for the ticket
- **AND** the system SHALL record the new sync state

### Requirement: Error Handling and Retry Logic
The system SHALL handle API failures gracefully with exponential backoff retry logic.

#### Scenario: Retry on transient network failure
- **GIVEN** a transient network failure when calling Jira API
- **WHEN** the system encounters the failure
- **THEN** the system SHALL retry the request up to 3 times
- **AND** the system SHALL use exponential backoff delays (1s, 4s, 16s)
- **AND** if all retries fail, the system SHALL log the error and skip the ticket

#### Scenario: Handle rate limit errors
- **GIVEN** a rate limit error (HTTP 429) from Microsoft Graph API
- **WHEN** the system encounters the error
- **THEN** the system SHALL parse the Retry-After header
- **AND** the system SHALL wait for the specified duration before retrying
- **AND** the system SHALL log the rate limit event

#### Scenario: Handle partial batch failures
- **GIVEN** processing a batch of 50 tickets where 1 ticket fails
- **WHEN** the failure occurs
- **THEN** the system SHALL log the error for the failed ticket
- **AND** the system SHALL continue processing the remaining 49 tickets
- **AND** the system SHALL include failure details in the summary report

### Requirement: Configuration Management
The system SHALL load configuration from YAML files and environment variables.

#### Scenario: Load valid configuration
- **GIVEN** a config.yaml file with valid Jira URL, JQL filter, and Outlook settings
- **AND** environment variables with Jira token and Microsoft credentials
- **WHEN** the system starts
- **THEN** the system SHALL load all configuration values
- **AND** the system SHALL validate required fields are present

#### Scenario: Fail on missing required configuration
- **GIVEN** missing Jira URL in configuration
- **WHEN** the system attempts to load configuration
- **THEN** the system SHALL raise a configuration error
- **AND** the system SHALL list all missing required fields
- **AND** the system SHALL exit with non-zero status

#### Scenario: Override configuration with environment variables
- **GIVEN** a config.yaml with `sync.interval_minutes = 10`
- **AND** environment variable `SYNC_INTERVAL_MINUTES=5`
- **WHEN** the system loads configuration
- **THEN** the environment variable value SHALL take precedence
- **AND** the system SHALL use interval of 5 minutes

### Requirement: Logging and Audit Trail
The system SHALL log all operations and maintain an audit trail for compliance.

#### Scenario: Log successful calendar event creation
- **GIVEN** a calendar event created for ticket `SRE-123`
- **WHEN** the creation succeeds
- **THEN** the system SHALL log an INFO message containing:
  - Timestamp
  - Action: "Created calendar event"
  - Jira key
  - Outlook event ID
  - User/assignee

#### Scenario: Log failed API calls
- **GIVEN** a failed Jira API call
- **WHEN** the failure occurs
- **THEN** the system SHALL log an ERROR message containing:
  - Timestamp
  - Action: "Jira API call failed"
  - Error details
  - Request parameters (without sensitive data)
  - Stack trace (in debug mode)

#### Scenario: Generate sync summary report
- **GIVEN** a completed sync run
- **WHEN** the sync finishes
- **THEN** the system SHALL log a summary containing:
  - Total tickets processed
  - Events created count
  - Events updated count
  - Events deleted count
  - Errors encountered
  - Execution duration

### Requirement: Security and Credential Protection
The system SHALL protect credentials and prevent exposure in logs or code.

#### Scenario: Load credentials from environment variables
- **GIVEN** credentials stored in environment variables `JIRA_API_TOKEN` and `MS_CLIENT_SECRET`
- **WHEN** the system starts
- **THEN** the system SHALL load credentials from environment
- **AND** the system SHALL never log credential values
- **AND** the system SHALL mask credentials in error messages

#### Scenario: Support AWS Secrets Manager
- **GIVEN** configuration specifying AWS Secrets Manager for credential storage
- **WHEN** the system retrieves credentials
- **THEN** the system SHALL fetch credentials from AWS Secrets Manager
- **AND** the system SHALL cache credentials in memory (not disk)
- **AND** the system SHALL refresh credentials on expiration

#### Scenario: Prevent credential exposure in logs
- **GIVEN** any log message containing request data
- **WHEN** the log is written
- **THEN** the system SHALL mask or redact any credential fields
- **AND** the system SHALL replace credential values with `***REDACTED***`

### Requirement: Filtering and Customization
The system SHALL support flexible filtering of Jira tickets for synchronization.

#### Scenario: Filter by Jira project
- **GIVEN** JQL filter `project = SRE`
- **WHEN** the system queries Jira
- **THEN** the system SHALL only retrieve tickets from the SRE project

#### Scenario: Filter by assignee
- **GIVEN** JQL filter `assignee = currentUser()`
- **WHEN** the system queries Jira
- **THEN** the system SHALL only retrieve tickets assigned to the authenticated user

#### Scenario: Filter by custom labels
- **GIVEN** JQL filter `labels = important AND plannedStart is not EMPTY`
- **WHEN** the system queries Jira
- **THEN** the system SHALL only retrieve important tickets with planned start dates

#### Scenario: Combine multiple filter criteria
- **GIVEN** JQL filter `project = SRE AND status != Done AND assignee in (user1, user2)`
- **WHEN** the system queries Jira
- **THEN** the system SHALL retrieve tickets matching ALL criteria

### Requirement: Dry Run Mode
The system SHALL support a dry-run mode for testing without modifying calendars.

#### Scenario: Execute dry run
- **GIVEN** the system started with `--dry-run` flag
- **WHEN** the sync runs
- **THEN** the system SHALL fetch tickets from Jira
- **AND** the system SHALL calculate what changes would be made
- **AND** the system SHALL log all proposed changes
- **AND** the system SHALL NOT create, update, or delete any Outlook events
- **AND** the system SHALL NOT modify the sync state database

#### Scenario: Dry run summary report
- **GIVEN** a completed dry run
- **WHEN** the run finishes
- **THEN** the system SHALL log a summary of proposed actions:
  - Events that would be created (with ticket keys)
  - Events that would be updated (with changes)
  - Events that would be deleted (with ticket keys)

### Requirement: Multi-User Support
The system SHALL support configuration for multiple users to sync their respective tickets.

#### Scenario: User-specific calendar sync
- **GIVEN** configuration for user `john.doe@company.com`
- **WHEN** the system authenticates with Microsoft Graph
- **THEN** the system SHALL use delegated permissions for that user
- **AND** the system SHALL only modify that user's calendar

#### Scenario: Support multiple configuration files
- **GIVEN** multiple config files: `config-user1.yaml`, `config-user2.yaml`
- **WHEN** the system runs with `--config config-user1.yaml`
- **THEN** the system SHALL load configuration for user1
- **AND** the system SHALL use a separate SQLite database per configuration
- **AND** users' syncs SHALL NOT interfere with each other

### Requirement: Performance and Scalability
The system SHALL handle large volumes of tickets efficiently.

#### Scenario: Batch processing
- **GIVEN** 500 Jira tickets matching the filter
- **WHEN** the system processes the tickets
- **THEN** the system SHALL fetch tickets in batches of 50-100
- **AND** the system SHALL use Microsoft Graph batch API for event operations
- **AND** the total sync time SHALL be less than 10 minutes

#### Scenario: Database query optimization
- **GIVEN** 10,000 sync state records in the database
- **WHEN** the system queries for a specific ticket
- **THEN** the query SHALL complete in less than 100 milliseconds
- **AND** the system SHALL use indexed queries on jira_key and outlook_event_id

#### Scenario: Handle API rate limits proactively
- **GIVEN** approaching Microsoft Graph rate limit (9,000 of 10,000 requests used)
- **WHEN** the system detects high usage
- **THEN** the system SHALL slow down request rate
- **AND** the system SHALL complete sync without hitting rate limit errors

### Requirement: Timezone Handling
The system SHALL correctly handle timezones for calendar events.

#### Scenario: Convert UTC to user timezone
- **GIVEN** Jira ticket with planned start in UTC `2025-10-20T09:00:00Z`
- **AND** user's Outlook calendar timezone is `America/Los_Angeles` (UTC-7)
- **WHEN** the system creates the calendar event
- **THEN** the event SHALL display at `2025-10-20T02:00:00` in user's calendar
- **AND** the event SHALL be stored with correct timezone metadata

#### Scenario: Handle daylight saving time transitions
- **GIVEN** a calendar event spanning DST transition dates
- **WHEN** the system creates the event
- **THEN** the system SHALL use the user's calendar timezone
- **AND** Outlook SHALL automatically adjust for DST

#### Scenario: Support configurable default timezone
- **GIVEN** configuration specifying default timezone `UTC`
- **AND** Jira ticket dates without timezone information
- **WHEN** the system creates events
- **THEN** the system SHALL interpret dates as UTC
- **AND** the system SHALL convert to user's calendar timezone

### Requirement: Monitoring and Health Checks
The system SHALL provide monitoring capabilities for operational visibility.

#### Scenario: Expose sync metrics
- **GIVEN** a completed sync run
- **WHEN** metrics are collected
- **THEN** the system SHALL export metrics including:
  - Total tickets processed
  - Events created, updated, deleted counts
  - Error count by type
  - Sync duration
  - Last successful sync timestamp

#### Scenario: Health check endpoint
- **GIVEN** the system running as a service
- **WHEN** a health check is requested
- **THEN** the system SHALL respond with status `healthy` or `unhealthy`
- **AND** if unhealthy, SHALL include reason (e.g., "authentication failed")
- **AND** SHALL include last successful sync timestamp

#### Scenario: Alert on consecutive failures
- **GIVEN** 3 consecutive sync failures
- **WHEN** the third failure occurs
- **THEN** the system SHALL trigger an alert
- **AND** the alert SHALL include error details and recommended actions
