"""
Main CLI interface for jira-outlook-sync
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import click
from colorama import Fore, Style, init as colorama_init

from . import __version__
from .config import Config
from .ics_exporter import ICSExporter
from .jira_auth import JiraAuth
from .jira_client import JiraClient
from .recipients import RecipientsManager

# Initialize colorama for colored output
colorama_init(autoreset=True)


@click.group()
@click.version_option(version=__version__)
@click.pass_context
def main(ctx: click.Context) -> None:
    """
    Jira-Outlook Sync - Export Jira tickets to calendar events
    
    Run 'jira-outlook-sync --help' for usage information.
    """
    ctx.ensure_object(dict)
    ctx.obj["config"] = Config()


@main.command()
@click.pass_context
def login(ctx: click.Context) -> None:
    """Authenticate with Jira"""
    config = ctx.obj["config"]
    
    jira_auth = JiraAuth(config)
    if jira_auth.login():
        sys.exit(0)
    else:
        sys.exit(1)


@main.command()
@click.pass_context
def logout(ctx: click.Context) -> None:
    """Clear stored Jira credentials"""
    config = ctx.obj["config"]
    
    config.clear_credentials("jira")
    click.echo("✅ Logged out from Jira")


@main.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Show authentication status and configuration"""
    config = ctx.obj["config"]
    credentials = config.load_credentials()

    click.echo("\n" + Fore.CYAN + "Authentication Status:" + Style.RESET_ALL)
    click.echo("-" * 40)

    # Jira status
    jira_creds = credentials.get("jira")
    if jira_creds:
        user_name = jira_creds.get("user_name", jira_creds.get("email", ""))
        click.echo(f"Jira:    {Fore.GREEN}✓{Style.RESET_ALL} Authenticated as {user_name}")
        click.echo(f"         URL: {jira_creds.get('url')}")
    else:
        click.echo(f"Jira:    {Fore.RED}✗{Style.RESET_ALL} Not authenticated")
        click.echo(f"         Run: jira-outlook-sync login")

    click.echo("\n" + Fore.CYAN + "Configuration:" + Style.RESET_ALL)
    click.echo("-" * 40)
    click.echo(f"Config directory: {config.CONFIG_DIR}")

    app_config = config.load_config()
    click.echo(f"Reminder: {app_config.get('reminder_minutes')} minutes before")
    click.echo(f"Default recipients: {'Enabled' if app_config.get('default_recipients') else 'Disabled'}")


@main.command()
@click.argument("keyword")
@click.option("--output", "-o", type=click.Path(), help="Output path for ICS file")
@click.option("--open-file", is_flag=True, help="Automatically open the exported ICS file")
@click.option("--with-recipients", is_flag=True, help="Include recipients from file")
@click.option("--recipients-file", type=click.Path(exists=True), help="Custom recipients file")
@click.option("--reminder", type=int, help="Reminder minutes before event")
@click.pass_context
def search(
    ctx: click.Context,
    keyword: str,
    output: Optional[str],
    open_file: bool,
    with_recipients: bool,
    recipients_file: Optional[str],
    reminder: Optional[int],
) -> None:
    """Search Jira tickets by keyword and export to ICS calendar file"""
    config = ctx.obj["config"]

    # Check Jira authentication
    if not config.has_credentials("jira"):
        click.echo(f"{Fore.RED}❌ Not authenticated with Jira{Style.RESET_ALL}")
        click.echo("Run: jira-outlook-sync login jira")
        sys.exit(1)

    # Get configuration
    app_config = config.load_config()
    reminder_minutes = reminder or app_config.get("reminder_minutes", 15)
    use_recipients = with_recipients or app_config.get("default_recipients", False)

    # Load recipients if needed
    recipients_list: List[str] = []
    optional_recipients_list: List[str] = []
    if use_recipients:
        recipients_manager = RecipientsManager(config)
        if recipients_file:
            recipients_list, optional_recipients_list = recipients_manager.load_all(Path(recipients_file))
        else:
            recipients_list, optional_recipients_list = recipients_manager.load_all()

        if not recipients_list:
            if not click.confirm("\n⚠️  No recipients found. Continue without recipients?"):
                sys.exit(0)

    # Search Jira
    click.echo(f"\n🔍 Searching Jira for: {Fore.YELLOW}{keyword}{Style.RESET_ALL}")

    jira_creds = config.load_credentials()["jira"]
    jira_client = JiraClient(
        url=jira_creds["url"],
        email=jira_creds["email"],
        api_token=jira_creds["api_token"],
    )

    try:
        tickets = jira_client.search_by_keyword(keyword)
    except Exception as e:
        click.echo(f"{Fore.RED}❌ Search failed: {e}{Style.RESET_ALL}")
        sys.exit(1)

    if not tickets:
        click.echo(f"\nℹ️  No tickets found matching '{keyword}'")
        sys.exit(0)

    # Display results
    click.echo(f"\n{Fore.GREEN}Found {len(tickets)} tickets:{Style.RESET_ALL}\n")
    for i, ticket in enumerate(tickets, 1):
        click.echo(f"{Fore.CYAN}{i}. [{ticket['key']}] {ticket['summary']}{Style.RESET_ALL}")
        
        # Display planned start/end with times if available
        start_display = f"{ticket['start_date']}"
        if ticket.get('start_time'):
            start_display += f" {ticket['start_time']}"
        
        due_display = f"{ticket['due_date']}" if ticket['due_date'] else 'None'
        if ticket.get('due_time'):
            due_display = f"{ticket['due_date']} {ticket['due_time']}"
        
        click.echo(f"   Planned: {start_display or 'None'}  →  {due_display}")
        click.echo(f"   Assignee: {ticket['assignee']}")
        click.echo()

    # Export to ICS file
    exporter = ICSExporter()
    
    # Determine output path
    if output:
        output_path = Path(output)
    else:
        output_path = Path.cwd() / exporter.get_export_filename(keyword)
    
    # Ask for confirmation
    click.echo(f"\n📄 Export location: {Fore.CYAN}{output_path}{Style.RESET_ALL}")
    if not click.confirm(f"Export {len(tickets)} tickets to ICS file?"):
        click.echo("Export cancelled")
        sys.exit(0)
    
    # Export to ICS
    try:
        exporter.export_to_ics(
            tickets=tickets,
            output_path=output_path,
            reminder_minutes=reminder_minutes,
            recipients=recipients_list,
            optional_recipients=optional_recipients_list,
        )
        click.echo(f"\n{Fore.GREEN}✅ Successfully exported to: {output_path}{Style.RESET_ALL}")
        
        # Auto-open if requested
        if open_file:
            import subprocess
            import platform
            
            click.echo(f"\n{Fore.CYAN}Opening file...{Style.RESET_ALL}")
            try:
                if platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", str(output_path)], check=True)
                elif platform.system() == "Windows":
                    subprocess.run(["start", str(output_path)], shell=True, check=True)
                else:  # Linux
                    subprocess.run(["xdg-open", str(output_path)], check=True)
                click.echo(f"{Fore.GREEN}✓{Style.RESET_ALL} Opened in default calendar application")
            except Exception as e:
                click.echo(f"{Fore.YELLOW}⚠️  Could not auto-open file: {e}{Style.RESET_ALL}")
                click.echo(f"Please manually open: {output_path}")
        else:
            click.echo(f"\n{Fore.CYAN}To import into Outlook (macOS):{Style.RESET_ALL}")
            click.echo(f"  1. Simply double-click the file: {output_path}")
            click.echo("  2. Outlook will open and prompt you to import")
            click.echo("  3. Choose which calendar to add the events to")
            click.echo("  4. Click 'Import'\n")
            click.echo(f"{Fore.CYAN}Alternative methods:{Style.RESET_ALL}")
            click.echo(f"  • Run: open {output_path}")
            click.echo(f"  • Or drag and drop the file onto Outlook calendar")
            click.echo(f"  • Or use: jira-outlook-sync search \"{keyword}\" --open-file\n")
    except Exception as e:
        click.echo(f"{Fore.RED}❌ Export failed: {e}{Style.RESET_ALL}")
        sys.exit(1)


@main.group()
def recipients() -> None:
    """Manage email recipients for calendar invites"""
    pass


@recipients.command("add")
@click.argument("email")
@click.pass_context
def recipients_add(ctx: click.Context, email: str) -> None:
    """Add a recipient to the list"""
    config = ctx.obj["config"]
    manager = RecipientsManager(config)
    manager.add_recipient(email)


@recipients.command("remove")
@click.argument("email")
@click.pass_context
def recipients_remove(ctx: click.Context, email: str) -> None:
    """Remove a recipient from the list"""
    config = ctx.obj["config"]
    manager = RecipientsManager(config)
    manager.remove_recipient(email)


@recipients.command("list")
@click.pass_context
def recipients_list(ctx: click.Context) -> None:
    """List all recipients"""
    config = ctx.obj["config"]
    manager = RecipientsManager(config)
    manager.list_recipients()


@main.group()
def config() -> None:
    """Manage configuration settings"""
    pass


@config.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_context
def config_set(ctx: click.Context, key: str, value: str) -> None:
    """Set a configuration value"""
    cfg = ctx.obj["config"]

    # Convert value to appropriate type
    if key == "reminder_minutes":
        value = int(value)
    elif key == "default_recipients":
        value = value.lower() in ("true", "1", "yes")

    cfg.set_config_value(key, value)
    click.echo(f"✅ Set {key} = {value}")


@config.command("get")
@click.argument("key")
@click.pass_context
def config_get(ctx: click.Context, key: str) -> None:
    """Get a configuration value"""
    cfg = ctx.obj["config"]
    value = cfg.get_config_value(key)
    if value is not None:
        click.echo(f"{key} = {value}")
    else:
        click.echo(f"❌ Configuration key '{key}' not found")


@config.command("show")
@click.pass_context
def config_show(ctx: click.Context) -> None:
    """Show all configuration values"""
    cfg = ctx.obj["config"]
    app_config = cfg.load_config()

    click.echo("\nConfiguration:")
    click.echo("-" * 40)
    for key, value in app_config.items():
        click.echo(f"{key}: {value}")


if __name__ == "__main__":
    main()
