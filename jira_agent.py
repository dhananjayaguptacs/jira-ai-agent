"""
Jira AI Bot that creates and processes tickets.
"""

import time
from typing import Dict
from jira_client import JiraClient
from ticket_analyzer import TicketAnalyzer
from similarity_checker import SimilarityChecker

class JiraAIBot:
    def __init__(self, jira_url: str, username: str, api_token: str, jql_filter: str):
        self.jira_client = JiraClient(jira_url, username, api_token)
        self.ticket_analyzer = TicketAnalyzer()
        self.similarity_checker = SimilarityChecker()
        self.jql_filter = jql_filter
        self.processed_tickets = set()
        self.jira_base_url = jira_url

    def create_ticket(self, summary: str, description: str, ticket_type: str, project_key: str) -> Dict:
        """Create a new Jira ticket and analyze it."""
        # Create ticket
        ticket = self.jira_client.create_ticket(summary, description, ticket_type, project_key)
        if "error" in ticket:
            return ticket

        ticket_id = ticket["ticket_id"]
        # Add ticket to similarity store
        self.similarity_checker.add_ticket(ticket)
        # Find similar tickets
        similar_tickets = self.similarity_checker.find_similar_tickets(ticket, self.jira_base_url)
        # Fetch logs
        logs = self.jira_client.fetch_attachment_content(ticket_id)
        # Analyze ticket
        comment = self.ticket_analyzer.analyze_ticket(ticket, logs, similar_tickets, self.jira_base_url)
        # Add comment to Jira
        self.jira_client.add_comment(ticket_id, comment)
        self.processed_tickets.add(ticket_id)
        return ticket

    def process_new_tickets(self):
        """Process new tickets and add comments."""
        tickets = self.jira_client.get_tickets(self.jql_filter)
        for ticket in tickets:
            ticket_id = ticket["ticket_id"]
            if ticket_id not in self.processed_tickets and not self.jira_client.has_bot_comment(ticket_id):
                print(f"Processing new ticket {ticket_id}: {ticket['summary']}")
                # Add ticket to similarity store
                self.similarity_checker.add_ticket(ticket)
                # Find similar tickets
                similar_tickets = self.similarity_checker.find_similar_tickets(ticket, self.jira_base_url)
                # Fetch logs
                logs = self.jira_client.fetch_attachment_content(ticket_id)
                # Analyze ticket and format response
                comment = self.ticket_analyzer.analyze_ticket(ticket, logs, similar_tickets, self.jira_base_url)
                # Add comment to Jira
                self.jira_client.add_comment(ticket_id, comment)
                self.processed_tickets.add(ticket_id)

    def run(self, poll_interval: int = 60):
        """Run the bot to periodically check for new tickets."""
        print("Starting Jira AI Bot...")
        while True:
            try:
                self.process_new_tickets()
                print(f"Waiting {poll_interval} seconds before next check...")
                time.sleep(poll_interval)
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(poll_interval)