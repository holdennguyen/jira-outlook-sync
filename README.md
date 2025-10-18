# Jira-Outlook Sync

> CLI tool to export Jira tickets to Outlook calendar events

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## What Does This Do?

Searches your Jira tickets and creates calendar events in Outlook with:
- ✅ Planned start and end times from Jira
- ✅ Reminders (45 minutes before by default)
- ✅ Team members as attendees
- ✅ Ticket links and details

**No OAuth setup needed!** Exports to `.ics` files that you can import into Outlook, Google Calendar, or any calendar app.

## Quick Start (5 minutes)

### Step 1: Install Python (if you don't have it)

Check if you have Python:
```bash
python3 --version
```

If you see `Python 3.8` or higher, you're good! If not, download from https://www.python.org/downloads/

### Step 2: Install This Tool

```bash
# 1. Download the code
git clone https://github.com/holdennguyen/jira-outlook-sync.git
cd jira-outlook-sync

# 2. Create a virtual environment (isolated Python environment)
python3 -m venv .venv

# 3. Activate the virtual environment
source .venv/bin/activate  # On macOS/Linux
# Or on Windows: .venv\Scripts\activate

# 4. Install the tool
pip install -e .
```

**What is a virtual environment?**
A virtual environment is like a separate Python installation just for this tool. It keeps all the dependencies isolated so they don't interfere with other Python programs on your computer. Think of it as a sandbox.

### Step 3: Login to Jira

```bash
jira-outlook-sync login
```

You'll need:
- **Jira URL**: Your company's Jira (e.g., `https://opswat.atlassian.net`)
- **Email**: Your Jira login email
- **API Token**: Create one at https://id.atlassian.com/manage-profile/security/api-tokens
  - Click "Create API token"
  - Give it a name like "jira-outlook-sync"
  - Copy the token and paste it

### Step 4: Search and Export

```bash
# Search for tickets and export to calendar file
jira-outlook-sync search "deployment" --open-file
```

This will:
1. Search Jira for tickets with "deployment" in the title
2. Show you the tickets found
3. Ask if you want to export
4. Create a `.ics` file
5. Automatically open it in Outlook

**Then in Outlook**: Just click "Import" when the dialog appears!

## Common Usage

### Export with Auto-Open
```bash
jira-outlook-sync search "4.70.1" --open-file
```

### Export to Specific File
```bash
jira-outlook-sync search "sprint" -o ~/Desktop/sprint-events.ics
```

### Add Team Members as Attendees
```bash
# Add recipients first
jira-outlook-sync recipients add john@company.com
jira-outlook-sync recipients add jane@company.com

# Export with recipients
jira-outlook-sync search "deployment" --with-recipients --open-file
```

### View All Recipients
```bash
jira-outlook-sync recipients list
```

### Check Login Status
```bash
jira-outlook-sync status
```

## How to Use Every Day

After the initial setup, using the tool is simple:

```bash
# 1. Activate the virtual environment (if not already active)
cd /path/to/jira-outlook-sync
source .venv/bin/activate  # You'll see (.venv) in your prompt

# 2. Run your search
jira-outlook-sync search "your-keyword" --open-file

# 3. Import in Outlook (click Import when it opens)

# 4. Done! Deactivate when finished (optional)
deactivate
```

## Importing the ICS File into Outlook

### macOS
1. The file opens automatically with `--open-file` flag
2. Or double-click the `.ics` file
3. Or run: `open filename.ics`
4. Click "Import" in Outlook

### Windows
1. Double-click the `.ics` file
2. Or in Outlook: File → Open & Export → Import/Export → Import an iCalendar file
3. Select the `.ics` file

### Web (Outlook.com)
1. Go to https://outlook.com/calendar
2. Click "Add calendar" → "Upload from file"
3. Select the `.ics` file

## Troubleshooting

### "Command not found: jira-outlook-sync"

Make sure you activated the virtual environment:
```bash
source .venv/bin/activate
```

You should see `(.venv)` in your command prompt.

### "Not authenticated with Jira"

Login again:
```bash
jira-outlook-sync login jira
```

### "No tickets found"

- Try a broader search keyword
- Make sure the tickets exist in Jira
- Check you have access to the tickets

### Times are Wrong

The tool uses UTC times from Jira and converts them properly. If times look wrong, check your Jira ticket's planned start/end times in Jira first.

## Files and Locations

**Where your data is stored:**
- Configuration: `~/.jira-outlook-sync/config.json`
- Credentials: `~/.jira-outlook-sync/credentials.json` (secure)
- Recipients: `~/.jira-outlook-sync/recipients.txt`

**Project files:**
- Source code: `src/jira_outlook_sync/`
- Tests: `tests/`

## Understanding the Files

- **requirements.txt** - Python packages needed to run the tool
- **requirements-dev.txt** - Extra packages only needed if you're developing/testing
- **pyproject.toml** - Package configuration
- **recipients.txt.example** - Example of how to format recipient emails

You don't need to touch these files unless you're developing the tool!

## For Developers

### Run Tests
```bash
# Activate virtual environment first
source .venv/bin/activate

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run tests with coverage
pytest --cov=jira_outlook_sync
```

## Getting Help

```bash
# Show all commands
jira-outlook-sync --help

# Show help for a specific command
jira-outlook-sync search --help
jira-outlook-sync recipients --help
```

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- Report issues: https://github.com/holdennguyen/jira-outlook-sync/issues
