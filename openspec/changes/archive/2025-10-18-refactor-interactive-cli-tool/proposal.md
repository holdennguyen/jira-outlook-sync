# Refactor to Interactive CLI Tool with Browser OAuth

## Why
The current design requires manual setup of API tokens and complex OAuth client credentials configuration, making it difficult for end users to adopt. Users want a simple, open-source CLI tool they can run locally with minimal setup. The tool should use browser-based OAuth login for both Jira and Outlook (similar to `gh auth login` or `az login`), present tickets for approval before creating calendar events, and support keyword-based filtering of Jira ticket titles.

## What Changes
- **BREAKING**: Transform from automated background service to interactive CLI tool
- Add browser-based OAuth device flow for Jira Cloud authentication (replacing API tokens)
- Add browser-based OAuth device flow for Microsoft Graph authentication (simplifying setup)
- Add interactive approval workflow: search Jira by keyword → display matching tickets → ask for confirmation → create Outlook events
- Add keyword search functionality for Jira ticket titles/summaries
- Simplify configuration to focus on search keywords and preferences (no complex JQL required)
- Remove continuous sync mode and polling infrastructure (keep one-time execution only)
- Package as installable CLI tool (via pip/pipx) with proper entry point
- Store OAuth tokens securely in user's home directory (`~/.jira-outlook-sync/`)
- Add `login`, `logout`, `search`, `sync`, and `status` commands

## Impact
**Affected Specs:**
- `specs/jira-outlook-integration/spec.md` (MODIFIED - add interactive features, browser OAuth, approval workflow)

**Affected Code:**
- Refactor `scripts/` into proper Python package structure with CLI entry point
- Add OAuth device flow implementations for Jira and Microsoft Graph
- Add interactive prompts and confirmation dialogs
- Add keyword-based search functionality
- Simplify configuration (remove complex YAML, use simple ~/.config file)
- Remove state tracking database (SQLite) - each run is independent
- Remove continuous sync/polling functionality
- Add CLI commands using `click` or `argparse`

**New Features:**
1. **Browser OAuth Login**:
   - `jira-outlook-sync login jira` - Opens browser for Jira OAuth
   - `jira-outlook-sync login outlook` - Opens browser for Microsoft OAuth
   - Tokens stored securely in `~/.jira-outlook-sync/credentials.json`

2. **Interactive Workflow**:
   ```bash
   jira-outlook-sync search "API migration"
   # Shows matching tickets with dates
   # Asks: "Create calendar events for these 3 tickets? [y/N]"
   # Creates events only after approval
   ```

3. **Email Recipient Lists for Calendar Invites**:
   ```bash
   jira-outlook-sync recipients add john@example.com
   jira-outlook-sync recipients add team@company.com
   jira-outlook-sync search "sprint" --with-recipients
   # Creates events and sends invites to all recipients in list
   ```

4. **Simple Commands**:
   - `search [keyword]` - Search Jira tickets by keyword in title
   - `sync [ticket-key]` - Sync specific ticket to Outlook
   - `logout` - Clear stored credentials
   - `status` - Show authentication status
   - `recipients add/remove/list` - Manage email recipient list
   - `recipients add/remove/list` - Manage email recipient list for calendar invites

**Breaking Changes:**
- **BREAKING**: Remove `--continuous` mode and polling functionality
- **BREAKING**: Remove YAML configuration file (use simple CLI flags)
- **BREAKING**: Remove SQLite state tracking database
- **BREAKING**: Remove environment variable-based credential management
- **BREAKING**: Remove AWS Secrets Manager / Azure Key Vault integration

**Migration Path:**
- Existing users will need to:
  1. Run `jira-outlook-sync login jira` and `jira-outlook-sync login outlook`
  2. Use new `search` command instead of continuous sync
  3. Remove old config.yaml and .env files

**Dependencies:**
- Add: `click` (CLI framework), `msal` (already present), `oauthlib` (OAuth flows)
- Keep: `requests`, `python-dotenv` (for optional overrides)
- Remove: `PyYAML` (no longer needed), complex AWS/Azure SDK dependencies

## Benefits
- **90% easier setup**: No API token creation, no app registration complexity
- **User-friendly**: Browser login like modern CLI tools (gh, az, gcloud)
- **Safe**: Explicit approval before creating calendar events (no surprises)
- **Flexible**: Keyword search instead of complex JQL queries
- **Open-source ready**: Simple enough for community adoption
- **No infrastructure**: Runs entirely locally, no background services needed

## Risks & Mitigation
- **Risk**: Users expect continuous sync like before
  - **Mitigation**: Document use case shift, provide cron examples if needed
- **Risk**: OAuth consent screen requires admin approval in some orgs
  - **Mitigation**: Document IT admin setup steps, provide pre-approved app IDs if possible
- **Risk**: Less automation than before
  - **Mitigation**: This is intentional - interactive approval is a feature, not a bug

## Success Metrics
- Time to first successful sync: <5 minutes (vs 30+ minutes before)
- User adoption rate increase by 3x
- Setup documentation reduced from 10 pages to 2 pages
- Zero credential-related support tickets
