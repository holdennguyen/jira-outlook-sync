"""Basic tests for jira-outlook-sync CLI"""

import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from jira_outlook_sync.cli import main
from jira_outlook_sync.config import Config
from jira_outlook_sync.recipients import RecipientsManager


def test_cli_version():
    """Test CLI version command"""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "1.0.0" in result.output


def test_cli_help():
    """Test CLI help command"""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Jira-Outlook Sync" in result.output
    assert "login" in result.output
    assert "search" in result.output


def test_status_command_no_auth():
    """Test status command when not authenticated"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["status"])
        assert result.exit_code == 0
        assert "Not authenticated" in result.output


def test_config_manager():
    """Test configuration manager"""
    with pytest.MonkeyPatch.context() as mp:
        # Use temporary directory
        import tempfile

        temp_dir = Path(tempfile.mkdtemp())
        mp.setattr(Config, "CONFIG_DIR", temp_dir)

        config = Config()
        assert config.CONFIG_DIR == temp_dir

        # Test default config
        app_config = config.load_config()
        assert app_config["reminder_minutes"] == 15
        assert app_config["default_recipients"] is False

        # Test set/get config
        config.set_config_value("reminder_minutes", 45)
        assert config.get_config_value("reminder_minutes") == 45


def test_recipients_email_validation():
    """Test email validation"""
    assert RecipientsManager.validate_email("john@example.com") is True
    assert RecipientsManager.validate_email("jane.smith@company.co.uk") is True
    assert RecipientsManager.validate_email("invalid-email") is False
    assert RecipientsManager.validate_email("@example.com") is False
    assert RecipientsManager.validate_email("john@") is False


def test_recipients_add_remove():
    """Test adding and removing recipients"""
    with pytest.MonkeyPatch.context() as mp:
        import tempfile

        temp_dir = Path(tempfile.mkdtemp())
        mp.setattr(Config, "CONFIG_DIR", temp_dir)

        config = Config()
        manager = RecipientsManager(config)

        # Add recipient
        assert manager.add_recipient("john@example.com") is True

        # Verify it was added
        recipients = manager.load_recipients()
        assert "john@example.com" in recipients

        # Try adding duplicate
        assert manager.add_recipient("john@example.com") is True

        # Remove recipient
        assert manager.remove_recipient("john@example.com") is True

        # Verify it was removed
        recipients = manager.load_recipients()
        assert "john@example.com" not in recipients


def test_recipients_file_parsing():
    """Test recipients file parsing with comments and empty lines"""
    with pytest.MonkeyPatch.context() as mp:
        import tempfile

        temp_dir = Path(tempfile.mkdtemp())
        mp.setattr(Config, "CONFIG_DIR", temp_dir)

        config = Config()
        manager = RecipientsManager(config)

        # Create test file with various formats
        test_file = temp_dir / "test_recipients.txt"
        test_file.write_text(
            """# Comment line
john@example.com

# Another comment
jane@example.com
invalid-email
bob@test.org
"""
        )

        recipients = manager.load_recipients(test_file)
        assert len(recipients) == 3
        assert "john@example.com" in recipients
        assert "jane@example.com" in recipients
        assert "bob@test.org" in recipients
        assert "invalid-email" not in recipients
