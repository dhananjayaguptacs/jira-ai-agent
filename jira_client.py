"""
Handles interactions with Jira API for ticket creation and retrieval.
"""

from typing import List, Dict
from jira import JIRA
import requests

class JiraClient:
    def __init__(self, jira_url: str, username: str, api_token: str):
        self.jira = JIRA(server=jira_url, basic_auth=(username, api_token))
        self.username = username

    def create_ticket(self, summary: str, description: str, ticket_type: str, project_key: str) -> Dict:
        """Create a Jira ticket with the specified details."""
        issue_dict = {
            "project": {"key": project_key},
            "summary": summary,
            "description": description,
            "issuetype": {"name": ticket_type}
        }
        try:
            issue = self.jira.create_issue(fields=issue_dict)
            return {
                "ticket_id": issue.key,
                "issue_type": ticket_type,
                "summary": summary,
                "description": description,
                "created_at": issue.fields.created,
                "key": issue.key,
                "fields": {
                    "summary": summary,
                    "description": description
                }
            }
        except Exception as e:
            print(f"Error creating ticket: {e}")
            return {"error": str(e)}

    def get_tickets(self, jql_filter: str) -> List[Dict]:
        """Fetch tickets matching the JQL filter."""
        try:
            tickets = self.jira.search_issues(jql_filter, maxResults=100)
            return [{
                "ticket_id": ticket.key,
                "issue_type": ticket.fields.issuetype.name,
                "summary": ticket.fields.summary,
                "description": ticket.fields.description or "",
                "created_at": ticket.fields.created,
                "key": ticket.key,
                "fields": {
                    "summary": ticket.fields.summary,
                    "description": ticket.fields.description or ""
                }
            } for ticket in tickets]
        except Exception as e:
            print(f"Error fetching tickets: {e}")
            return []

    def fetch_attachment_content(self, ticket_id: str) -> str:
        """Fetch and read text-based attachments (e.g., .log, .txt)."""
        ticket = self.jira.issue(ticket_id)
        attachments = ticket.fields.attachment
        log_content = ""
        for attachment in attachments:
            if attachment.filename.endswith((".log", ".txt")):
                try:
                    response = requests.get(attachment.content, auth=(self.username, self.jira._options["basic_auth"][1]))
                    response.raise_for_status()
                    log_content += response.text + "\n"
                except Exception as e:
                    print(f"Error fetching attachment {attachment.filename} for ticket {ticket_id}: {e}")
        return log_content.strip()

    def has_bot_comment(self, ticket_id: str) -> bool:
        """Check if the bot has already commented on the ticket."""
        ticket = self.jira.issue(ticket_id)
        comments = self.jira.comments(ticket)
        return any(comment.author.emailAddress == self.username for comment in comments)

    def add_comment(self, ticket_id: str, comment: str):
        """Add a comment to the specified ticket."""
        try:
            self.jira.add_comment(ticket_id, comment)
            print(f"Commented on ticket {ticket_id}: {comment[:100]}...")
        except Exception as e:
            print(f"Error adding comment to ticket {ticket_id}: {e}")