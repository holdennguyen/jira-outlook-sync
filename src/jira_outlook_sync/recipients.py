"""Manage email recipients for calendar invites"""

import re
from pathlib import Path
from typing import List

from .config import Config


class RecipientsManager:
    """Manage email recipient lists"""

    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    def __init__(self, config: Config) -> None:
        """Initialize recipients manager"""
        self.config = config
        self.recipients_file = config.RECIPIENTS_FILE

    def load_recipients(self, file_path: Path = None) -> List[str]:
        """
        Load recipients from file
        
        Args:
            file_path: Optional custom file path, uses default if None
            
        Returns:
            List of valid email addresses
        """
        file_path = file_path or self.recipients_file

        if not file_path.exists():
            return []

        recipients = []
        try:
            with open(file_path, "r") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # Skip empty lines and comments
                    if not line or line.startswith("#"):
                        continue

                    # Validate email
                    if self.validate_email(line):
                        recipients.append(line)
                    else:
                        print(f"⚠️  Line {line_num}: Skipped invalid email: {line}")

        except IOError as e:
            print(f"⚠️  Failed to read recipients file: {e}")

        return recipients

    def add_recipient(self, email: str) -> bool:
        """
        Add a recipient to the list
        
        Returns:
            True if added successfully, False otherwise
        """
        if not self.validate_email(email):
            print(f"❌ Invalid email address: {email}")
            return False

        # Check if already exists
        recipients = self.load_recipients()
        if email in recipients:
            print(f"ℹ️  {email} is already in the recipients list")
            return True

        # Append to file
        try:
            with open(self.recipients_file, "a") as f:
                f.write(f"{email}\n")
            print(f"✅ Added {email} to recipients list")
            return True
        except IOError as e:
            print(f"❌ Failed to add recipient: {e}")
            return False

    def remove_recipient(self, email: str) -> bool:
        """
        Remove a recipient from the list
        
        Returns:
            True if removed successfully, False otherwise
        """
        if not self.recipients_file.exists():
            print("❌ Recipients file does not exist")
            return False

        recipients = self.load_recipients()
        if email not in recipients:
            print(f"❌ {email} not found in recipients list")
            return False

        # Rewrite file without the email
        try:
            with open(self.recipients_file, "r") as f:
                lines = f.readlines()

            with open(self.recipients_file, "w") as f:
                for line in lines:
                    if line.strip() != email:
                        f.write(line)

            print(f"✅ Removed {email} from recipients list")
            return True
        except IOError as e:
            print(f"❌ Failed to remove recipient: {e}")
            return False

    def list_recipients(self) -> List[str]:
        """Get and display all recipients"""
        recipients = self.load_recipients()

        if not recipients:
            print("ℹ️  No recipients configured")
            print(f"\nAdd recipients with: jira-outlook-sync recipients add <email>")
            return []

        print(f"\nCurrent recipients ({len(recipients)}):")
        for i, email in enumerate(recipients, 1):
            print(f"  {i}. {email}")

        return recipients

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address format"""
        return bool(RecipientsManager.EMAIL_REGEX.match(email))
