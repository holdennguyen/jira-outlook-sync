# Jira-Outlook Integration Specification - Interactive CLI Deltas

## ADDED Requirements

### Requirement: Browser-Based OAuth Authentication for Jira
The system SHALL authenticate with Jira Cloud using OAuth 2.0 device authorization flow via browser.

#### Scenario: Initiate Jira OAuth login
- **GIVEN** the user runs `jira-outlook-sync login jira`
- **WHEN** the command executes
- **THEN** the system SHALL display a device code and verification URL
- **AND** the system SHALL automatically open the user's default browser to the verification URL
- **AND** the system SHALL poll for authorization completion

#### Scenario: Complete Jira OAuth login
- **GIVEN** the user authorizes the application in the browser
- **WHEN** authorization is complete
- **THEN** the system SHALL receive an access token and refresh token
- **AND** the system SHALL store tokens securely in `~/.jira-outlook-sync/credentials.json`
- **AND** the system SHALL display "Successfully authenticated with Jira"

#### Scenario: Handle OAuth authorization timeout
- **GIVEN** the user does not complete authorization within 5 minutes
- **WHEN** the timeout expires
- **THEN** the system SHALL display "Authorization timed out. Please try again."
- **AND** the system SHALL exit with non-zero status code

### Requirement: Browser-Based OAuth Authentication for Microsoft Outlook
The system SHALL authenticate with Microsoft Graph using OAuth 2.0 device authorization flow via browser.

#### Scenario: Initiate Outlook OAuth login
- **GIVEN** the user runs `jira-outlook-sync login outlook`
- **WHEN** the command executes
- **THEN** the system SHALL display a device code and verification URL
- **AND** the system SHALL automatically open the user's default browser to the Microsoft login page
- **AND** the system SHALL poll for authorization completion

#### Scenario: Complete Outlook OAuth login with consent
- **GIVEN** the user logs in and consents to calendar permissions
- **WHEN** authorization is complete
- **THEN** the system SHALL receive an access token and refresh token
- **AND** the system SHALL store tokens in `~/.jira-outlook-sync/credentials.json`
- **AND** the system SHALL display "Successfully authenticated with Outlook"

#### Scenario: Automatic token refresh
- **GIVEN** stored Outlook access token is expired
- **WHEN** the user runs a command requiring Outlook access
- **THEN** the system SHALL automatically refresh the token using the refresh token
- **AND** the system SHALL update the stored credentials
- **AND** the system SHALL proceed with the command

### Requirement: Keyword-Based Jira Ticket Search
The system SHALL search Jira tickets by keyword in title/summary and display matching tickets with planned dates.

#### Scenario: Search tickets by keyword
- **GIVEN** the user runs `jira-outlook-sync search "API migration"`
- **WHEN** the search executes
- **THEN** the system SHALL query Jira using JQL: `summary ~ "API migration" AND (startDate is not EMPTY OR dueDate is not EMPTY) ORDER BY startDate ASC`
- **AND** the system SHALL display a formatted list of matching tickets with key, summary, start date, due date, and assignee

#### Scenario: Display search results with dates
- **GIVEN** search returns tickets SRE-123, SRE-456, SRE-789
- **WHEN** results are displayed
- **THEN** the system SHALL show:
  ```
  Found 3 tickets matching "API migration":
  
  1. [SRE-123] Migrate user API to v2
     Start: 2025-10-20  |  Due: 2025-10-25  |  Assignee: John Doe
     
  2. [SRE-456] Update API documentation
     Start: 2025-10-22  |  Due: 2025-10-28  |  Assignee: Jane Smith
     
  3. [SRE-789] API performance testing
     Start: None  |  Due: 2025-10-30  |  Assignee: Bob Jones
  ```

#### Scenario: Handle no search results
- **GIVEN** the user searches for keyword with no matches
- **WHEN** the search executes
- **THEN** the system SHALL display "No tickets found matching 'keyword'"
- **AND** the system SHALL exit with status code 0

### Requirement: Interactive Approval Workflow
The system SHALL present matching tickets to the user and ask for explicit approval before creating calendar events.

#### Scenario: Request approval for calendar event creation
- **GIVEN** search found 3 matching tickets
- **WHEN** the system displays the results
- **THEN** the system SHALL prompt: "Create Outlook calendar events for these 3 tickets? [y/N]: "
- **AND** the system SHALL wait for user input

#### Scenario: User approves calendar event creation
- **GIVEN** the approval prompt is displayed
- **WHEN** the user enters "y" or "yes"
- **THEN** the system SHALL create Outlook calendar events for all displayed tickets
- **AND** the system SHALL show progress: "Creating event 1/3... Created [SRE-123]"
- **AND** after completion, the system SHALL display summary: "Successfully created 3 calendar events"

#### Scenario: User declines calendar event creation
- **GIVEN** the approval prompt is displayed
- **WHEN** the user enters "n", "no", or just presses Enter
- **THEN** the system SHALL display "No events created"
- **AND** the system SHALL exit without creating any calendar events

#### Scenario: User approves with selective creation
- **GIVEN** search found 3 tickets but user only wants 2
- **WHEN** the system prompts for approval
- **THEN** the system SHALL support prompt: "Enter ticket numbers to sync (comma-separated, or 'all'): "
- **AND** if user enters "1,3", the system SHALL create events only for tickets 1 and 3
- **AND** the system SHALL skip ticket 2

### Requirement: CLI Command Structure
The system SHALL provide a simple command-line interface with clear commands.

#### Scenario: Display help information
- **GIVEN** the user runs `jira-outlook-sync --help`
- **WHEN** the command executes
- **THEN** the system SHALL display:
  - Tool description
  - Available commands: login, logout, search, sync, status
  - Usage examples
  - Options and flags

#### Scenario: Check authentication status
- **GIVEN** the user runs `jira-outlook-sync status`
- **WHEN** the command executes
- **THEN** the system SHALL display:
  - Jira authentication status (✓ Authenticated as user@example.com OR ✗ Not authenticated)
  - Outlook authentication status (✓ Authenticated as user@company.com OR ✗ Not authenticated)
  - Token expiration times
  - Credential storage location

#### Scenario: Logout from services
- **GIVEN** the user runs `jira-outlook-sync logout`
- **WHEN** the command executes
- **THEN** the system SHALL prompt: "Logout from: [1] Jira, [2] Outlook, [3] Both: "
- **AND** the system SHALL remove selected credentials from storage
- **AND** the system SHALL display "Successfully logged out from [service]"

### Requirement: Sync Specific Ticket by Key
The system SHALL support syncing a specific Jira ticket to Outlook without search.

#### Scenario: Sync single ticket by key
- **GIVEN** the user runs `jira-outlook-sync sync SRE-123`
- **WHEN** the command executes
- **THEN** the system SHALL fetch ticket SRE-123 from Jira
- **AND** the system SHALL display ticket details
- **AND** the system SHALL prompt: "Create calendar event for this ticket? [y/N]: "
- **AND** if approved, the system SHALL create the Outlook event

#### Scenario: Sync multiple tickets by keys
- **GIVEN** the user runs `jira-outlook-sync sync SRE-123 SRE-456 SRE-789`
- **WHEN** the command executes
- **THEN** the system SHALL fetch all specified tickets
- **AND** the system SHALL display all ticket details
- **AND** the system SHALL prompt for approval once for all tickets
- **AND** if approved, the system SHALL create events for all tickets

#### Scenario: Handle non-existent ticket key
- **GIVEN** the user runs `jira-outlook-sync sync INVALID-999`
- **WHEN** the command executes
- **THEN** the system SHALL display "Error: Ticket INVALID-999 not found"
- **AND** the system SHALL exit with non-zero status code

### Requirement: Secure Credential Storage
The system SHALL store OAuth tokens securely in the user's home directory with appropriate file permissions.

#### Scenario: Store credentials with secure permissions
- **GIVEN** successful OAuth authentication
- **WHEN** the system saves credentials
- **THEN** the system SHALL create `~/.jira-outlook-sync/` directory if it doesn't exist
- **AND** the system SHALL set directory permissions to 700 (user read/write/execute only)
- **AND** the system SHALL save credentials to `credentials.json` with permissions 600 (user read/write only)

#### Scenario: Encrypt sensitive credential data
- **GIVEN** access tokens and refresh tokens to be stored
- **WHEN** the system writes to credentials.json
- **THEN** the system SHALL encrypt tokens using OS keyring if available
- **AND** if keyring unavailable, SHALL store with file permissions as security

#### Scenario: Load credentials on command execution
- **GIVEN** the user runs a command requiring authentication
- **WHEN** the system starts
- **THEN** the system SHALL load credentials from `~/.jira-outlook-sync/credentials.json`
- **AND** the system SHALL validate token expiration
- **AND** if expired, SHALL automatically attempt refresh
- **AND** if refresh fails, SHALL prompt user to re-authenticate

### Requirement: Email Recipient List for Calendar Invites
The system SHALL support adding recipients from a user-defined email list file when creating Outlook calendar events.

#### Scenario: Load recipients from file
- **GIVEN** a file exists at `~/.jira-outlook-sync/recipients.txt` with email addresses
- **WHEN** the user runs `jira-outlook-sync search "keyword" --with-recipients`
- **THEN** the system SHALL read the recipients file
- **AND** the system SHALL parse email addresses (one per line, ignoring empty lines and comments starting with #)
- **AND** the system SHALL validate each email address format

#### Scenario: Create calendar event with recipients
- **GIVEN** recipients file contains `john@example.com`, `jane@example.com`, `team@example.com`
- **AND** the user approves creating an event for ticket SRE-123
- **WHEN** the system creates the Outlook calendar event
- **THEN** the system SHALL add all valid recipients as required attendees
- **AND** the calendar invite SHALL be sent to all recipients
- **AND** the system SHALL display "✓ Created event for [SRE-123] with 3 recipients"

#### Scenario: Handle missing recipients file
- **GIVEN** no recipients file exists at `~/.jira-outlook-sync/recipients.txt`
- **AND** the user runs a command with `--with-recipients` flag
- **WHEN** the system attempts to load recipients
- **THEN** the system SHALL display a warning: "Recipients file not found at ~/.jira-outlook-sync/recipients.txt"
- **AND** the system SHALL prompt: "Create calendar event without recipients? [y/N]: "
- **AND** if user confirms, SHALL create event without attendees

#### Scenario: Validate email addresses in recipients file
- **GIVEN** recipients file contains valid and invalid email addresses:
  ```
  john@example.com
  jane.smith@company.com
  invalid-email
  # This is a comment
  bob@test.org
  ```
- **WHEN** the system loads the file
- **THEN** the system SHALL accept `john@example.com`, `jane.smith@company.com`, and `bob@test.org`
- **AND** the system SHALL display warning: "Skipped invalid email: invalid-email"
- **AND** the system SHALL ignore comment lines

#### Scenario: Specify custom recipients file location
- **GIVEN** the user has recipients stored in a custom location
- **WHEN** the user runs `jira-outlook-sync search "keyword" --recipients-file /path/to/my-team.txt`
- **THEN** the system SHALL load recipients from the specified file instead of default location
- **AND** the system SHALL follow the same validation and parsing rules

#### Scenario: Manage recipients via CLI
- **GIVEN** the user runs `jira-outlook-sync recipients add john@example.com`
- **WHEN** the command executes
- **THEN** the system SHALL append `john@example.com` to `~/.jira-outlook-sync/recipients.txt`
- **AND** the system SHALL validate the email format before adding
- **AND** the system SHALL display "✓ Added john@example.com to recipients list"

#### Scenario: List current recipients
- **GIVEN** the user runs `jira-outlook-sync recipients list`
- **WHEN** the command executes
- **THEN** the system SHALL read and display all recipients from the file:
  ```
  Current recipients (3):
  1. john@example.com
  2. jane@example.com
  3. team@example.com
  ```

#### Scenario: Remove recipient from list
- **GIVEN** the user runs `jira-outlook-sync recipients remove jane@example.com`
- **WHEN** the command executes
- **THEN** the system SHALL remove the email from `recipients.txt`
- **AND** the system SHALL display "✓ Removed jane@example.com from recipients list"

#### Scenario: Configure default recipients behavior
- **GIVEN** the user runs `jira-outlook-sync config set default-recipients true`
- **WHEN** the config is saved
- **THEN** all future calendar event creations SHALL automatically include recipients from the file
- **AND** the user SHALL NOT need to specify `--with-recipients` flag
- **AND** the user can override with `--no-recipients` flag

## MODIFIED Requirements

### Requirement: Jira Ticket Query
The system SHALL query Jira using keyword-based search or JQL filters to retrieve tickets with planned dates.

#### Scenario: Query tickets with planned dates using keyword
- **GIVEN** a user-provided keyword "sprint planning"
- **WHEN** the system executes the search
- **THEN** the system SHALL construct JQL: `summary ~ "sprint planning" AND (startDate is not EMPTY OR dueDate is not EMPTY)`
- **AND** the system SHALL return all tickets matching the criteria
- **AND** each ticket SHALL include key, summary, assignee, status, start date, and due date

#### Scenario: Handle empty result set
- **GIVEN** a keyword that matches no tickets
- **WHEN** the system executes the search
- **THEN** the system SHALL return an empty list
- **AND** the system SHALL display a user-friendly message "No tickets found matching 'keyword'"

#### Scenario: Handle Jira API authentication failure
- **GIVEN** expired or invalid OAuth token
- **WHEN** the system attempts to query Jira
- **THEN** the system SHALL attempt to refresh the OAuth token
- **AND** if refresh fails, SHALL display "Jira authentication expired. Please run: jira-outlook-sync login jira"
- **AND** the system SHALL exit with non-zero status code

### Requirement: Outlook Calendar Event Creation
The system SHALL create Outlook calendar events for approved Jira tickets with planned dates.

#### Scenario: Create event after user approval
- **GIVEN** user has approved creation for ticket `SRE-123` with start `2025-10-20` and due `2025-10-25`
- **WHEN** the system creates the event
- **THEN** the system SHALL create an Outlook calendar event with:
  - Subject: `[REMINDER] [SRE-123] <ticket summary>`
  - Start: `2025-10-20T09:00:00` in user's timezone
  - End: `2025-10-25T17:00:00` in user's timezone
  - Body: "Jira Ticket: https://jira.company.com/browse/SRE-123\n\n<ticket description>"
  - Reminder: 15 minutes before (configurable via --reminder flag)
  - Categories: ["Jira Reminder"]
- **AND** the system SHALL display "✓ Created event for [SRE-123]"

#### Scenario: Create event with only due date
- **GIVEN** a Jira ticket with only due date (no start date)
- **WHEN** user approves calendar event creation
- **THEN** the system SHALL create an all-day event on the due date
- **AND** the event subject SHALL include "[REMINDER]" prefix

#### Scenario: Handle Microsoft Graph API authentication failure
- **GIVEN** expired or invalid OAuth token
- **WHEN** the system attempts to create a calendar event
- **THEN** the system SHALL attempt token refresh using refresh token
- **AND** if refresh succeeds, SHALL retry the calendar creation
- **AND** if refresh fails, SHALL display "Outlook authentication expired. Please run: jira-outlook-sync login outlook"

### Requirement: Configuration Management
The system SHALL use simple command-line flags and minimal configuration file for user preferences.

#### Scenario: Use default configuration
- **GIVEN** no configuration file exists
- **WHEN** the user runs a command
- **THEN** the system SHALL use default values:
  - Reminder: 15 minutes before event
  - Calendar name: Default calendar
  - Timezone: System timezone

#### Scenario: Override defaults with command flags
- **GIVEN** the user runs `jira-outlook-sync search "migration" --reminder 60 --calendar "Work"`
- **WHEN** the command executes
- **THEN** the system SHALL use 60-minute reminder instead of default 15
- **AND** the system SHALL create events in "Work" calendar instead of default

#### Scenario: Persist user preferences
- **GIVEN** the user runs commands with custom flags repeatedly
- **WHEN** the user runs `jira-outlook-sync config set reminder 30`
- **THEN** the system SHALL save the preference to `~/.jira-outlook-sync/config.json`
- **AND** future commands SHALL use 30-minute reminder by default unless overridden

### Requirement: Error Handling and User Feedback
The system SHALL provide clear, actionable error messages and feedback during interactive operations.

#### Scenario: Display progress during event creation
- **GIVEN** user approved creation for 10 tickets
- **WHEN** the system creates events
- **THEN** the system SHALL display real-time progress:
  ```
  Creating calendar events...
  ✓ [1/10] Created event for SRE-123
  ✓ [2/10] Created event for SRE-456
  ✗ [3/10] Failed to create event for SRE-789: Network timeout
  ✓ [4/10] Created event for SRE-101
  ...
  Summary: 9 succeeded, 1 failed
  ```

#### Scenario: Handle partial failures gracefully
- **GIVEN** 5 tickets to sync, where 1 fails due to network error
- **WHEN** the error occurs
- **THEN** the system SHALL continue processing remaining tickets
- **AND** the system SHALL display which ticket failed and why
- **AND** the system SHALL provide retry suggestion: "Retry failed tickets with: jira-outlook-sync sync SRE-789"

#### Scenario: Provide actionable authentication errors
- **GIVEN** user is not authenticated with Jira
- **WHEN** user runs `jira-outlook-sync search "test"`
- **THEN** the system SHALL display:
  ```
  Error: Not authenticated with Jira
  
  To get started, run: jira-outlook-sync login jira
  ```
- **AND** the system SHALL exit with status code 1

## REMOVED Requirements

### Requirement: Synchronization State Tracking
**Reason**: Interactive CLI tool doesn't need persistent state tracking since each run is independent
**Migration**: Users should re-run searches as needed instead of relying on automatic sync state

### Requirement: Change Detection and Update
**Reason**: No longer supporting continuous sync or automatic updates
**Migration**: Users manually re-sync tickets when Jira changes occur

### Requirement: Dry Run Mode
**Reason**: Interactive approval workflow replaces dry-run functionality
**Migration**: Users see ticket details before approval, which serves the same purpose

### Requirement: Multi-User Support
**Reason**: Each user runs the CLI with their own OAuth credentials automatically
**Migration**: No migration needed - multi-user support is implicit via per-user OAuth

### Requirement: Performance and Scalability
**Reason**: Interactive tool processes small batches per user action, not bulk automation
**Migration**: For bulk operations, users can still use batch sync commands

### Requirement: Monitoring and Health Checks
**Reason**: No background service to monitor in interactive CLI model
**Migration**: Use exit codes and command output for operational monitoring
