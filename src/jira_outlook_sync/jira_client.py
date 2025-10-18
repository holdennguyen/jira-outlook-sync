"""Jira API client for searching and retrieving tickets"""

from typing import Any, Dict, List, Optional

import requests
from requests.auth import HTTPBasicAuth


class JiraClient:
    """Client for interacting with Jira REST API"""

    def __init__(self, url: str, email: str, api_token: str) -> None:
        """Initialize Jira client with credentials"""
        self.url = url.rstrip("/")
        self.auth = HTTPBasicAuth(email, api_token)
        self.session = requests.Session()
        self.session.auth = self.auth

    def search_by_keyword(self, keyword: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search for Jira tickets by keyword in summary
        Returns list of tickets with planned dates
        """
        # Build JQL query to search for keyword
        # Note: Not filtering by dates since custom date fields vary by instance
        jql = f'summary ~ "{keyword}" ORDER BY created DESC'

        return self.search_jql(jql, max_results)

    def search_jql(self, jql: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search Jira using JQL query
        Returns list of tickets
        """
        # Use the new search/jql endpoint (post-2023 Jira Cloud)
        url = f"{self.url}/rest/api/3/search/jql"
        params = {
            "jql": jql,
            "maxResults": max_results,
            # Include planned start/end custom fields for calendar events
            "fields": "summary,assignee,status,created,customfield_16880,customfield_16881",
        }

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            tickets = []
            for issue in data.get("issues", []):
                tickets.append(self._format_ticket(issue))

            return tickets

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to search Jira: {e}")

    def get_ticket_by_key(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a specific ticket by its key"""
        url = f"{self.url}/rest/api/3/issue/{key}"
        params = {"fields": "summary,assignee,status,created,customfield_16880,customfield_16881"}

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            issue = response.json()
            return self._format_ticket(issue)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise Exception(f"Failed to get ticket {key}: {e}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get ticket {key}: {e}")

    def _format_ticket(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Format raw Jira issue data into simplified structure"""
        fields = issue.get("fields", {})
        assignee = fields.get("assignee") or {}
        
        # Extract created date
        created = fields.get("created", "")
        created_date = created.split("T")[0] if created else None
        
        # Extract planned start and end dates (custom fields for OPSWAT Jira)
        planned_start = fields.get("customfield_16880", "")  # Planned start
        planned_end = fields.get("customfield_16881", "")    # Planned end
        
        # Parse datetime strings (format: 2025-10-22T12:00:00.000-0700)
        start_date = planned_start.split("T")[0] if planned_start else created_date
        start_time = None
        if planned_start and "T" in planned_start:
            # Extract time portion (e.g., "12:00:00")
            start_time = planned_start.split("T")[1].split(".")[0] if "T" in planned_start else None
            
        due_date = planned_end.split("T")[0] if planned_end else None
        due_time = None
        if planned_end and "T" in planned_end:
            due_time = planned_end.split("T")[1].split(".")[0] if "T" in planned_end else None

        return {
            "key": issue.get("key"),
            "summary": fields.get("summary", ""),
            "description": fields.get("description", ""),
            "status": fields.get("status", {}).get("name", "Unknown"),
            "assignee": assignee.get("displayName", "Unassigned"),
            "assignee_email": assignee.get("emailAddress", ""),
            "start_date": start_date,
            "start_time": start_time,
            "due_date": due_date,
            "due_time": due_time,
            "planned_start_datetime": planned_start,  # Full ISO datetime
            "planned_end_datetime": planned_end,      # Full ISO datetime
            "url": f"{self.url}/browse/{issue.get('key')}",
        }
