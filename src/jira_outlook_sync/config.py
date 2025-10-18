"""Configuration management for jira-outlook-sync"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Manages configuration and credentials for jira-outlook-sync"""

    CONFIG_DIR = Path.home() / ".jira-outlook-sync"
    CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    RECIPIENTS_FILE = CONFIG_DIR / "recipients.txt"

    DEFAULT_CONFIG = {
        "reminder_minutes": 15,
        "calendar_name": "Calendar",
        "timezone": "UTC",
        "default_recipients": False,
    }

    def __init__(self) -> None:
        """Initialize config manager and ensure config directory exists"""
        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        """Create config directory with secure permissions if it doesn't exist"""
        if not self.CONFIG_DIR.exists():
            self.CONFIG_DIR.mkdir(mode=0o700, parents=True)

    def load_config(self) -> Dict[str, Any]:
        """Load configuration, merging defaults with saved config"""
        config = self.DEFAULT_CONFIG.copy()
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, "r") as f:
                    saved_config = json.load(f)
                    config.update(saved_config)
            except (json.JSONDecodeError, IOError):
                pass
        return config

    def save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file"""
        with open(self.CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)

    def set_config_value(self, key: str, value: Any) -> None:
        """Set a single configuration value"""
        config = self.load_config()
        config[key] = value
        self.save_config(config)

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a single configuration value"""
        config = self.load_config()
        return config.get(key, default)

    def load_credentials(self) -> Dict[str, Any]:
        """Load stored OAuth credentials"""
        if not self.CREDENTIALS_FILE.exists():
            return {}

        try:
            with open(self.CREDENTIALS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def save_credentials(self, credentials: Dict[str, Any]) -> None:
        """Save OAuth credentials with secure permissions"""
        with open(self.CREDENTIALS_FILE, "w") as f:
            json.dump(credentials, f, indent=2)
        # Ensure secure permissions (user read/write only)
        os.chmod(self.CREDENTIALS_FILE, 0o600)

    def clear_credentials(self, service: Optional[str] = None) -> None:
        """Clear credentials for a specific service or all services"""
        if not self.CREDENTIALS_FILE.exists():
            return

        credentials = self.load_credentials()
        if service:
            credentials.pop(service, None)
            self.save_credentials(credentials)
        else:
            # Clear all credentials
            self.CREDENTIALS_FILE.unlink()

    def has_credentials(self, service: str) -> bool:
        """Check if credentials exist for a service"""
        credentials = self.load_credentials()
        return service in credentials and credentials[service]
