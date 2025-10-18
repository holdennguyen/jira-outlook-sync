"""OAuth authentication for Jira Cloud"""

import time
import webbrowser
from typing import Dict, Optional

import requests
from requests.auth import HTTPBasicAuth

from .config import Config


class JiraAuth:
    """Handle Jira OAuth authentication using device flow"""

    # Jira Cloud OAuth endpoints
    JIRA_AUTH_URL = "https://auth.atlassian.com/authorize"
    JIRA_TOKEN_URL = "https://auth.atlassian.com/oauth/token"
    JIRA_API_BASE = "https://api.atlassian.com"

    # OAuth client credentials (public client for device flow)
    CLIENT_ID = "jira-outlook-sync-cli"
    SCOPES = "read:jira-user read:jira-work offline_access"

    def __init__(self, config: Config) -> None:
        """Initialize Jira auth handler"""
        self.config = config

    def login(self) -> bool:
        """
        Perform device flow OAuth login for Jira
        Returns True if successful, False otherwise
        """
        print("🔐 Authenticating with Jira Cloud...")
        print("\nNote: This is a simplified demo implementation.")
        print("In production, you would need to:")
        print("1. Register an OAuth app in Atlassian Developer Console")
        print("2. Implement proper device code flow")
        print("3. Handle token refresh properly")
        print("\nFor now, we'll use API token authentication as a fallback.")
        print("\nPlease provide your Jira credentials:")

        jira_url = input("Jira URL (e.g., https://yourcompany.atlassian.net): ").strip()
        email = input("Email: ").strip()
        api_token = input("API Token (from https://id.atlassian.com/manage/api-tokens): ").strip()

        if not all([jira_url, email, api_token]):
            print("❌ All fields are required")
            return False

        # Validate credentials by making a test request
        try:
            response = requests.get(
                f"{jira_url}/rest/api/3/myself",
                auth=HTTPBasicAuth(email, api_token),
                timeout=10,
            )
            response.raise_for_status()
            user_info = response.json()

            # Store credentials
            credentials = self.config.load_credentials()
            credentials["jira"] = {
                "url": jira_url,
                "email": email,
                "api_token": api_token,
                "user_name": user_info.get("displayName", email),
                "account_id": user_info.get("accountId"),
            }
            self.config.save_credentials(credentials)

            print(f"✅ Successfully authenticated as {user_info.get('displayName', email)}")
            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ Authentication failed: {e}")
            return False

    def get_credentials(self) -> Optional[Dict[str, str]]:
        """Get stored Jira credentials"""
        credentials = self.config.load_credentials()
        return credentials.get("jira")

    def is_authenticated(self) -> bool:
        """Check if user is authenticated with Jira"""
        return self.config.has_credentials("jira")

    def logout(self) -> None:
        """Clear stored Jira credentials"""
        self.config.clear_credentials("jira")
        print("✅ Logged out from Jira")
