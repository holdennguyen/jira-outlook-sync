# Implementation Tasks - Interactive CLI Tool Refactor

## 1. Project Restructuring & Setup
- [ ] 1.1 Create proper Python package structure with `src/jira_outlook_sync/` layout
- [ ] 1.2 Add `setup.py` or `pyproject.toml` for pip/pipx installation
- [ ] 1.3 Define CLI entry point (`jira-outlook-sync` command)
- [ ] 1.4 Update requirements.txt with new dependencies (click, oauthlib)
- [ ] 1.5 Create `~/.jira-outlook-sync/` directory structure for credentials and config

## 2. OAuth Authentication - Jira
- [ ] 2.1 Implement Jira OAuth 2.0 device authorization flow
- [ ] 2.2 Create `login jira` command with browser opening
- [ ] 2.3 Implement device code polling and token retrieval
- [ ] 2.4 Store Jira OAuth tokens securely in `~/.jira-outlook-sync/credentials.json`
- [ ] 2.5 Implement automatic token refresh for Jira
- [ ] 2.6 Handle OAuth timeout and error scenarios
- [ ] 2.7 Add unit tests for Jira OAuth flow

## 3. OAuth Authentication - Microsoft Outlook
- [ ] 3.1 Implement Microsoft Graph OAuth 2.0 device authorization flow
- [ ] 3.2 Create `login outlook` command with browser opening
- [ ] 3.3 Implement MSAL device code flow integration
- [ ] 3.4 Store Microsoft OAuth tokens in `~/.jira-outlook-sync/credentials.json`
- [ ] 3.5 Implement automatic token refresh using MSAL
- [ ] 3.6 Handle consent and permission errors
- [ ] 3.7 Add unit tests for Microsoft OAuth flow

## 4. Credential Storage & Security
- [ ] 4.1 Create secure credential file with proper permissions (600)
- [ ] 4.2 Implement credential encryption using OS keyring (optional)
- [ ] 4.3 Create credential loader with validation and refresh logic
- [ ] 4.4 Implement `logout` command to clear credentials
- [ ] 4.5 Add credential file migration/upgrade logic
- [ ] 4.6 Add unit tests for credential management

## 5. Keyword-Based Jira Search
- [ ] 5.1 Implement `search` command with keyword parameter
- [ ] 5.2 Build JQL query from keyword: `summary ~ "keyword" AND (startDate is not EMPTY OR dueDate is not EMPTY)`
- [ ] 5.3 Fetch tickets from Jira API using OAuth token
- [ ] 5.4 Parse and format ticket data (key, summary, dates, assignee)
- [ ] 5.5 Display formatted search results in CLI
- [ ] 5.6 Handle empty search results gracefully
- [ ] 5.7 Add unit tests for search functionality

## 6. Interactive Approval Workflow
- [ ] 6.1 Implement approval prompt after search results display
- [ ] 6.2 Parse user input (y/n/yes/no/Enter)
- [ ] 6.3 Implement selective approval (ticket numbers: "1,3,5" or "all")
- [ ] 6.4 Display clear prompt messages and instructions
- [ ] 6.5 Handle Ctrl+C interruption gracefully
- [ ] 6.6 Add integration tests for approval workflow

## 7. Outlook Calendar Event Creation
- [ ] 7.1 Update event creation to use "[REMINDER]" prefix in subject
- [ ] 7.2 Implement event creation with Microsoft Graph API using OAuth
- [ ] 7.3 Handle tickets with start and due dates
- [ ] 7.4 Handle tickets with only due date (create all-day event)
- [ ] 7.5 Add configurable reminder settings (--reminder flag)
- [ ] 7.6 Display progress indicator during event creation
- [ ] 7.7 Handle partial failures and continue processing
- [ ] 7.8 Add unit tests for event creation logic

## 8. CLI Command Structure
- [ ] 8.1 Implement main CLI entry point using click or argparse
- [ ] 8.2 Create `login` command with subcommands (jira, outlook)
- [ ] 8.3 Create `logout` command with interactive selection
- [ ] 8.4 Create `search` command with keyword argument
- [ ] 8.5 Create `sync` command for specific ticket keys
- [ ] 8.6 Create `status` command to show authentication state
- [ ] 8.7 Create `config` command for persistent preferences
- [ ] 8.8 Create `recipients` command with subcommands (add, remove, list)
- [ ] 8.9 Add `--help` text for all commands
- [ ] 8.10 Add global flags (--verbose, --debug, --reminder, --calendar, --with-recipients, --recipients-file)

## 9. Sync Specific Tickets
- [ ] 9.1 Implement `sync` command with ticket key(s) as arguments
- [ ] 9.2 Fetch specific tickets by key from Jira
- [ ] 9.3 Display ticket details before approval
- [ ] 9.4 Support multiple ticket keys in single command
- [ ] 9.5 Handle non-existent ticket keys with clear error
- [ ] 9.6 Add unit tests for ticket sync by key

## 10. Configuration Management
- [ ] 10.1 Create simple config file structure in `~/.jira-outlook-sync/config.json`
- [ ] 10.2 Implement config defaults (reminder: 15min, timezone: system)
- [ ] 10.3 Implement config get/set commands
- [ ] 10.4 Support command-line flag overrides (--reminder, --calendar)
- [ ] 10.5 Load and merge config on each command execution
- [ ] 10.6 Add validation for config values

## 11. Error Handling & User Feedback
- [ ] 11.1 Implement actionable error messages for auth failures
- [ ] 11.2 Add progress indicators for long operations
- [ ] 11.3 Display success/failure counts in summary
- [ ] 11.4 Provide retry suggestions for failed operations
- [ ] 11.5 Handle network timeouts gracefully
- [ ] 11.6 Add detailed debug logging (--debug flag)
- [ ] 11.7 Create user-friendly error message templates

## 12. Remove Unused Features
- [ ] 12.1 Remove SQLite state tracking database and code
- [ ] 12.2 Remove continuous sync mode (`--continuous` flag)
- [ ] 12.3 Remove polling and scheduling infrastructure
- [ ] 12.4 Remove YAML configuration file support
- [ ] 12.5 Remove environment variable-based credential loading
- [ ] 12.6 Remove AWS Secrets Manager integration
- [ ] 12.7 Remove Azure Key Vault integration
- [ ] 12.8 Remove dry-run mode (replaced by approval workflow)
- [ ] 12.9 Remove multi-user configuration files (implicit via OAuth)

## 13. Documentation
- [ ] 13.1 Update README.md with new CLI-first approach
- [ ] 13.2 Document browser OAuth login process for Jira
- [ ] 13.3 Document browser OAuth login process for Outlook
- [ ] 13.4 Create quick start guide (<5 minutes to first sync)
- [ ] 13.5 Document all CLI commands with examples
- [ ] 13.6 Create troubleshooting guide for OAuth issues
- [ ] 13.7 Document corporate IT admin setup requirements
- [ ] 13.8 Add migration guide from old version

## 14. Testing
- [ ] 14.1 Create unit tests for OAuth flows (mocked)
- [ ] 14.2 Create unit tests for search and sync commands
- [ ] 14.3 Create integration tests with test Jira and Outlook accounts
- [ ] 14.4 Test complete workflow: login → search → approve → sync
- [ ] 14.5 Test error scenarios (expired tokens, network failures)
- [ ] 14.6 Test on macOS, Linux, and Windows
- [ ] 14.7 Test with different shell environments
- [ ] 14.8 Achieve >80% code coverage

## 15. Packaging & Distribution
- [ ] 15.1 Configure setup.py for pip installation
- [ ] 15.2 Test installation via `pip install -e .`
- [ ] 15.3 Test installation via `pipx install .`
- [ ] 15.4 Verify CLI command is available after installation
- [ ] 15.5 Create release workflow for PyPI (optional)
- [ ] 15.6 Add version management
- [ ] 15.7 Create installation instructions for end users

## 16. Open Source Preparation
- [ ] 16.1 Review LICENSE file (ensure MIT is appropriate)
- [ ] 16.2 Add CONTRIBUTING.md guidelines
- [ ] 16.3 Create CODE_OF_CONDUCT.md
- [ ] 16.4 Add issue templates for GitHub
- [ ] 16.5 Add pull request template
- [ ] 16.6 Create security policy (SECURITY.md)
- [ ] 16.7 Add CI/CD workflow for testing and linting
- [ ] 16.8 Prepare repository for public release

## 17. Email Recipients Management
- [ ] 17.1 Implement recipients file creation at `~/.jira-outlook-sync/recipients.txt`
- [ ] 17.2 Create `recipients add` command with email validation
- [ ] 17.3 Create `recipients remove` command
- [ ] 17.4 Create `recipients list` command with formatted output
- [ ] 17.5 Implement recipients file parser (handle comments, empty lines, validation)
- [ ] 17.6 Add `--with-recipients` flag to search and sync commands
- [ ] 17.7 Add `--recipients-file` flag to specify custom file location
- [ ] 17.8 Add `--no-recipients` flag to override default behavior
- [ ] 17.9 Implement email address validation (RFC 5322 compliant)
- [ ] 17.10 Add recipients as required attendees to calendar events
- [ ] 17.11 Handle missing recipients file gracefully
- [ ] 17.12 Add config option for default recipients behavior
- [ ] 17.13 Display recipient count in event creation summary
- [ ] 17.14 Add unit tests for recipients management
- [ ] 17.15 Add integration tests for calendar invites with recipients

## 18. User Experience Polish
- [ ] 18.1 Add colored output for better readability (using colorama)
- [ ] 18.2 Add spinners for loading states
- [ ] 18.3 Add success/error emoji indicators (✓/✗)
- [ ] 18.4 Implement better table formatting for search results
- [ ] 18.5 Add command completion suggestions
- [ ] 18.6 Test UX with real users and iterate

## 19. Final Validation
- [ ] 19.1 End-to-end test: fresh install to successful sync
- [ ] 19.2 Validate OAuth consent screens look correct
- [ ] 19.3 Verify calendar events have correct formatting
- [ ] 19.4 Verify calendar invites are sent to recipients
- [ ] 19.5 Test recipients file parsing with various formats
- [ ] 19.6 Confirm credential security (file permissions, encryption)
- [ ] 19.7 Performance test with 50+ tickets
- [ ] 19.8 Accessibility review (screen reader friendly?)
- [ ] 19.9 Final documentation review
