"""Manage email recipients for calendar invites"""

import re
from pathlib import Path
from typing import List, Tuple

from .config import Config


class RecipientsManager:
    """Manage email recipient lists"""

    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    OPTIONAL_HEADER = "[optional]"

    def __init__(self, config: Config) -> None:
        """Initialize recipients manager"""
        self.config = config
        self.recipients_file = config.RECIPIENTS_FILE

    def load_recipients(self, file_path: Path = None) -> List[str]:
        """
        Load required recipients from file

        Args:
            file_path: Optional custom file path, uses default if None

        Returns:
            List of valid required email addresses
        """
        return self.load_all(file_path)[0]

    def load_all(self, file_path: Path = None) -> Tuple[List[str], List[str]]:
        """
        Load required and optional recipients from file

        Emails listed after an `[optional]` line are optional attendees.

        Args:
            file_path: Optional custom file path, uses default if None

        Returns:
            Tuple of (required, optional) valid email addresses
        """
        file_path = file_path or self.recipients_file

        if not file_path.exists():
            return [], []

        required: List[str] = []
        optional: List[str] = []
        current = required
        try:
            with open(file_path, "r") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # Skip empty lines and comments
                    if not line or line.startswith("#"):
                        continue

                    if line.lower() == self.OPTIONAL_HEADER:
                        current = optional
                        continue

                    # Validate email
                    if self.validate_email(line):
                        current.append(line)
                    else:
                        print(f"⚠️  Line {line_num}: Skipped invalid email: {line}")

        except IOError as e:
            print(f"⚠️  Failed to read recipients file: {e}")

        return required, optional

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
        required, optional = self.load_all()
        if email in required or email in optional:
            print(f"ℹ️  {email} is already in the recipients list")
            return True

        # Insert before the [optional] section so it stays required
        try:
            lines = []
            if self.recipients_file.exists():
                lines = self.recipients_file.read_text().splitlines(keepends=True)
            index = next(
                (i for i, l in enumerate(lines) if l.strip().lower() == self.OPTIONAL_HEADER),
                len(lines),
            )
            if index == len(lines) and lines and not lines[-1].endswith("\n"):
                lines[-1] += "\n"
            lines.insert(index, f"{email}\n")
            self.recipients_file.write_text("".join(lines))
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

        required, optional = self.load_all()
        if email not in required and email not in optional:
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
        required, optional = self.load_all()

        if not required and not optional:
            print("ℹ️  No recipients configured")
            print(f"\nAdd recipients with: jira-outlook-sync recipients add <email>")
            return []

        print(f"\nCurrent recipients ({len(required)}):")
        for i, email in enumerate(required, 1):
            print(f"  {i}. {email}")

        if optional:
            print(f"\nOptional recipients ({len(optional)}):")
            for i, email in enumerate(optional, 1):
                print(f"  {i}. {email}")

        return required

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address format"""
        return bool(RecipientsManager.EMAIL_REGEX.match(email))
