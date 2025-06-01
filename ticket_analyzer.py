"""
Analyzes Jira tickets using an LLM and formats responses using templates.
"""

from langchain_ollama import OllamaLLM
from agent_template import (
    GREETING,
    get_root_cause_prompt,
    get_initial_triage_prompt,
    format_root_cause_response,
    format_initial_triage_response,
    UNCLEAR_ISSUE_RESPONSE,
    format_final_response,
    format_similar_tickets
)

class TicketAnalyzer:
    def __init__(self):
        self.llm = OllamaLLM(model="gemma3:1b", temperature=0.7)

    def analyze_ticket(self, ticket: dict, logs: str, similar_tickets: list, jira_base_url: str) -> str:
        """Analyze a ticket and return a formatted response with greeting and similar tickets."""
        ticket_id = ticket["ticket_id"]
        description = ticket["description"]
        ticket_type = ticket.get("issue_type", "Unknown")

        if not description and not logs:
            analysis = UNCLEAR_ISSUE_RESPONSE
        else:
            # Use triage for short descriptions (<50 chars) or non-Bug/Support tickets, root cause otherwise
            if len(description) < 50 or ticket_type not in ["Bug", "Support"]:
                analysis = self._perform_initial_triage(ticket_id, description)
            else:
                analysis = self._perform_root_cause_analysis(ticket_id, description, logs)

        # Format similar tickets
        similar_tickets_text = format_similar_tickets(similar_tickets, jira_base_url)
        # Combine greeting, analysis, and similar tickets
        return format_final_response(GREETING, analysis, similar_tickets_text)

    def _perform_root_cause_analysis(self, ticket_id: str, description: str, logs: str) -> str:
        """Perform root cause analysis and format the response."""
        prompt = get_root_cause_prompt(description, logs)
        try:
            response = self.llm.invoke(prompt).strip()
            if response == "The issue is unclear.":
                return UNCLEAR_ISSUE_RESPONSE
            # Split response into cause and insights
            parts = response.split("\n", 1)
            root_cause = parts[0]
            insights = parts[1] if len(parts) > 1 else "Please verify the suggested cause."
            return format_root_cause_response(ticket_id, logs, root_cause, insights)
        except Exception as e:
            print(f"Error analyzing ticket {ticket_id}: {e}")
            return UNCLEAR_ISSUE_RESPONSE

    def _perform_initial_triage(self, ticket_id: str, description: str) -> str:
        """Perform initial triage and format the response."""
        prompt = get_initial_triage_prompt(description)
        try:
            response = self.llm.invoke(prompt).strip()
            # Split response into summary and team/component
            parts = response.split("\n", 1)
            summary = parts[0]
            team = parts[1] if len(parts) > 1 else "Development Team"
            return format_initial_triage_response(ticket_id, summary, team)
        except Exception as e:
            print(f"Error triaging ticket {ticket_id}: {e}")
            return UNCLEAR_ISSUE_RESPONSE