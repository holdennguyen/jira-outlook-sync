"""Export Jira tickets to ICS calendar file for Outlook import"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List
import uuid


class ICSExporter:
    """Generate ICS calendar files from Jira tickets"""

    def __init__(self) -> None:
        """Initialize ICS exporter"""
        pass

    def export_to_ics(
        self,
        tickets: List[Dict[str, Any]],
        output_path: Path,
        reminder_minutes: int = 45,
        recipients: List[str] = None,
    ) -> None:
        """
        Export Jira tickets to ICS file
        
        Args:
            tickets: List of Jira ticket dictionaries
            output_path: Path to save the ICS file
            reminder_minutes: Minutes before event to set reminder
            recipients: List of email addresses to add as attendees
        """
        ics_content = self._generate_ics(tickets, reminder_minutes, recipients or [])
        
        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(ics_content, encoding='utf-8')

    def _generate_ics(
        self,
        tickets: List[Dict[str, Any]],
        reminder_minutes: int,
        recipients: List[str],
    ) -> str:
        """Generate ICS file content"""
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//jira-outlook-sync//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            "X-WR-CALNAME:Jira Reminders",
            "X-WR-TIMEZONE:UTC",
        ]

        for ticket in tickets:
            event = self._generate_event(ticket, reminder_minutes, recipients)
            if event:
                lines.extend(event)

        lines.extend([
            "END:VCALENDAR",
            ""  # Empty line at end
        ])

        return "\r\n".join(lines)

    def _generate_event(
        self,
        ticket: Dict[str, Any],
        reminder_minutes: int,
        recipients: List[str],
    ) -> List[str]:
        """Generate ICS event for a single ticket"""
        
        # Get start and end times
        start_datetime = ticket.get("planned_start_datetime")
        end_datetime = ticket.get("planned_end_datetime")
        
        if not start_datetime or not end_datetime:
            # Skip tickets without both dates
            return []

        # Parse ISO datetime from Jira (e.g., "2025-10-22T12:00:00.000-0700")
        start_dt = self._parse_jira_datetime(start_datetime)
        end_dt = self._parse_jira_datetime(end_datetime)
        
        if not start_dt or not end_dt:
            return []

        # Generate unique ID for the event
        uid = f"{ticket['key']}-{uuid.uuid4().hex[:8]}@jira-outlook-sync"
        
        # Current timestamp for DTSTAMP
        now = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        
        # Format dates for ICS in UTC (with Z suffix to indicate UTC)
        # This tells Outlook these are absolute UTC times
        start_str = start_dt.strftime("%Y%m%dT%H%M%SZ")
        end_str = end_dt.strftime("%Y%m%dT%H%M%SZ")
        
        # Build event
        lines = [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{now}",
            f"DTSTART:{start_str}",
            f"DTEND:{end_str}",
            f"SUMMARY:[REMINDER] [{ticket['key']}] {self._escape_text(ticket['summary'])}",
            f"DESCRIPTION:{self._escape_text(self._build_description(ticket))}",
            f"LOCATION:{ticket['url']}",
            "STATUS:CONFIRMED",
            "SEQUENCE:0",
            "PRIORITY:5",
        ]
        
        # Add reminder/alarm
        lines.extend([
            "BEGIN:VALARM",
            "TRIGGER:-PT{}M".format(reminder_minutes),
            "ACTION:DISPLAY",
            f"DESCRIPTION:Reminder: {ticket['key']}",
            "END:VALARM",
        ])
        
        # Add attendees if provided
        for recipient in recipients:
            lines.append(f"ATTENDEE;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;CN={recipient}:mailto:{recipient}")
        
        # Add organizer (current user)
        if ticket.get("assignee_email"):
            lines.append(f"ORGANIZER;CN={ticket['assignee']}:mailto:{ticket['assignee_email']}")
        
        lines.append("END:VEVENT")
        
        return lines

    def _parse_jira_datetime(self, datetime_str: str) -> datetime:
        """
        Parse Jira datetime string to datetime object
        Format: 2025-10-22T12:00:00.000-0700
        Converts to UTC for proper ICS export
        """
        if not datetime_str:
            return None
            
        try:
            # Parse with timezone offset
            # Format: "2025-10-22T12:00:00.000-0700"
            if "." in datetime_str:
                # Split at the decimal point to separate milliseconds and timezone
                # "2025-10-22T12:00:00" + ".000-0700"
                main_part = datetime_str.split(".")[0]  # "2025-10-22T12:00:00"
                tz_part = datetime_str.split(".")[-1]   # "000-0700"
                
                # Extract timezone offset (last 5 chars: -0700 or +0530)
                tz_offset = tz_part[-5:]  # "-0700"
                
                # Parse the datetime
                dt = datetime.strptime(main_part, "%Y-%m-%dT%H:%M:%S")
                
                # Parse timezone offset
                tz_sign = 1 if tz_offset[0] == '+' else -1
                tz_hours = int(tz_offset[1:3])
                tz_minutes = int(tz_offset[3:5])
                
                # Convert to UTC by subtracting the offset
                # If time is in -0700 (PDT), we add 7 hours to get UTC
                from datetime import timedelta
                offset = timedelta(hours=tz_hours, minutes=tz_minutes)
                if tz_sign == -1:
                    dt = dt + offset  # Add offset to convert to UTC
                else:
                    dt = dt - offset  # Subtract offset to convert to UTC
                
                return dt
            else:
                # Try without milliseconds (assume UTC if no timezone)
                dt = datetime.strptime(datetime_str[:19], "%Y-%m-%dT%H:%M:%S")
                return dt
        except (ValueError, IndexError) as e:
            return None

    def _build_description(self, ticket: Dict[str, Any]) -> str:
        """Build event description from ticket data"""
        parts = [
            f"Jira Ticket: {ticket['url']}",
            f"Status: {ticket['status']}",
            f"Assignee: {ticket['assignee']}",
        ]
        
        if ticket.get("description"):
            parts.append("")
            parts.append("Description:")
            parts.append(ticket["description"][:500])  # Limit description length
        
        return "\\n\\n".join(parts)

    def _escape_text(self, text: str) -> str:
        """Escape text for ICS format"""
        if not text:
            return ""
        
        # Replace special characters
        text = text.replace("\\", "\\\\")
        text = text.replace(",", "\\,")
        text = text.replace(";", "\\;")
        text = text.replace("\n", "\\n")
        text = text.replace("\r", "")
        
        # Limit length to avoid issues
        if len(text) > 1000:
            text = text[:997] + "..."
        
        return text

    def get_export_filename(self, keyword: str) -> str:
        """Generate a filename for the ICS export"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_keyword = "".join(c if c.isalnum() else "_" for c in keyword)
        return f"jira_reminders_{safe_keyword}_{timestamp}.ics"
