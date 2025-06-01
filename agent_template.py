"""
This module defines templates for the AI assistant's responses.
"""

# Base instructions for the AI assistant
BASE_INSTRUCTIONS = (
    "You are an AI assistant designed to analyze Jira tickets. "
    "Your primary goal is to humanize responses, making them clear, concise, and helpful, "
    "without sounding like an AI-generated bot. Focus on providing actionable insights."
)

# Formal greeting for all comments
GREETING = (
    "Hello,\n\nThank you for raising this ticket. Below is our initial analysis to assist with resolving the issue.\n\n"
)

# Template for root cause analysis of a Jira ticket
ROOT_CAUSE_TEMPLATE = (
    "--- AI Bot Ticket Analysis ---\n"
    "*Ticket:* {ticket_id}\n"
    "*Error Logs:* {logs}\n\n"
    "*Root Cause:* {root_cause_suggestion}\n\n"
    "*Actionable Insights:*\n"
    "{actionable_insights}\n"
)

# Template for initial triage of a Jira ticket
INITIAL_TRIAGE_TEMPLATE = (
    "--- AI Bot Ticket Triage ---\n"
    "*Ticket:* {ticket_id}\n"
    "*Summary:* {problem_summary}\n"
    "*Suggested Team/Component:* {team_or_component}\n"
)

# Fallback response for unclear issues
UNCLEAR_ISSUE_RESPONSE = (
    "The issue is unclear based on the provided details. Our team will investigate further "
    "and respond soon. Thank you for your patience."
)

# Similar tickets section
SIMILAR_TICKETS_TEMPLATE = (
    "\n*Similar Tickets:*\n"
    "For additional context, you may review the following similar tickets:\n"
    "{similar_tickets}\n"
)

# Template for highly similar ticket found
HIGHLY_SIMILAR_TICKET_TEMPLATE = (
    "\n*Similar Issue Found:*\n"
    "This issue appears to be very similar to an existing ticket. Please refer to: {similar_ticket_link}\n"
)

# Placeholders for templates
PLACEHOLDERS = {
    'ticket_id': 'The Jira ticket ID (e.g., ABC-123).',
    'logs': 'Any relevant error logs or stack traces.',
    'root_cause_suggestion': 'A concise suggestion for the root cause.',
    'actionable_insights': 'Specific, short actions or next steps based on the analysis.',
    'problem_summary': 'A brief summary of the core problem.',
    'team_or_component': 'Suggested team or component responsible for the issue.',
    'similar_tickets': 'List of similar tickets with IDs and descriptions.',
    'similar_ticket_link': 'The Jira link of a highly similar ticket.'
}

# Prompt scenarios for different analysis types
PROMPT_SCENARIOS = {
    'root_cause_analysis': (
        BASE_INSTRUCTIONS + "\n\n"
        "Analyze the Jira ticket with the following details:\n"
        "- Description: '{description}'\n"
        "- Error Logs: '{logs}'\n\n"
        "Suggest a concise root cause for the issue and provide one or two short, actionable "
        "insights or next steps. If the issue is unclear, return: 'The issue is unclear.'"
    ),
    'initial_triage': (
        BASE_INSTRUCTIONS + "\n\n"
        "Summarize the core problem described in the Jira ticket with the following details:\n"
        "- Description: '{description}'\n\n"
        "Suggest the most likely team or component responsible. Keep it brief and to the point."
    ),
    'similarity_check': (
        BASE_INSTRUCTIONS + "\n\n"
        "Perform a similarity check for the new Jira ticket with ID '{new_ticket_id}' based on its summary and description. "
        "First, compare the summary: '{new_ticket_summary}'. "
        "Then, if needed, delve into the description: '{new_ticket_description}'. "
        "Compare this with the summaries and descriptions of existing tickets provided in the following format: "
        "'{existing_tickets_data}'. "
        "Exclude the ticket with ID '{new_ticket_id}' from the comparison to avoid matching the ticket with itself. "
        "Identify if a highly similar ticket exists (e.g., similarity score above 0.9 for summary, or above 0.7 for description if summary is not highly similar). "
        "If a highly similar ticket is found, output only its Jira link. "
        "If no highly similar ticket is found, list up to 3 most similar tickets with their IDs, summaries, and similarity scores."
    )
}

def get_root_cause_prompt(description: str, logs: str) -> str:
    """
    Constructs the prompt for root cause analysis.
    """
    return PROMPT_SCENARIOS['root_cause_analysis'].format(
        description=description,
        logs=logs if logs else "No error logs attached."
    )

def get_initial_triage_prompt(description: str) -> str:
    """
    Constructs the prompt for initial triage.
    """
    return PROMPT_SCENARIOS['initial_triage'].format(
        description=description
    )

def get_similarity_check_prompt(new_ticket_id: str, new_ticket_summary: str, new_ticket_description: str, existing_tickets_data: str) -> str:
    """
    Constructs the prompt for similarity check.
    `new_ticket_id` is the ID of the new ticket to exclude from comparison.
    `existing_tickets_data` should be a string representation of existing tickets,
    e.g., "TICKET-123: Summary - '...', Description - '...'; TICKET-456: Summary - '...', Description - '...'".
    """
    return PROMPT_SCENARIOS['similarity_check'].format(
        new_ticket_id=new_ticket_id,
        new_ticket_summary=new_ticket_summary,
        new_ticket_description=new_ticket_description,
        existing_tickets_data=existing_tickets_data
    )

def format_root_cause_response(ticket_id: str, logs: str, root_cause: str, insights: str) -> str:
    """
    Formats the root cause response using ROOT_CAUSE_TEMPLATE.
    """
    return ROOT_CAUSE_TEMPLATE.format(
        ticket_id=ticket_id,
        logs=logs if logs else "No error logs attached.",
        root_cause_suggestion=root_cause,
        actionable_insights=insights
    )

def format_initial_triage_response(ticket_id: str, problem_summary: str, team_or_component: str) -> str:
    """
    Formats the initial triage response using INITIAL_TRIAGE_TEMPLATE.
    """
    return INITIAL_TRIAGE_TEMPLATE.format(
        ticket_id=ticket_id,
        problem_summary=problem_summary,
        team_or_component=team_or_component
    )

def format_similar_tickets(similar_tickets: list, jira_base_url: str) -> str:
    """
    Formats the similar tickets section. If a highly similar ticket (e.g., similarity > 0.9)
    is found, it will output a concise link. Otherwise, it lists other similar tickets.
    """
    if not similar_tickets:
        return ""

    # Sort tickets by similarity in descending order
    sorted_similar_tickets = sorted(similar_tickets, key=lambda x: x['similarity'], reverse=True)

    # Check for a highly similar ticket (adjust threshold as needed)
    if sorted_similar_tickets and sorted_similar_tickets[0]['similarity'] > 0.9:
        highly_similar_ticket = sorted_similar_tickets[0]
        ticket_link = f"{jira_base_url}/browse/{highly_similar_ticket['ticket_id']}"
        return HIGHLY_SIMILAR_TICKET_TEMPLATE.format(similar_ticket_link=ticket_link)
    else:
        # List up to 3 most similar tickets if no highly similar one is found
        similar_tickets_text = []
        for t in sorted_similar_tickets[:3]: # Limit to top 3
            ticket_link = f"{jira_base_url}/browse/{t['ticket_id']}"
            similar_tickets_text.append(f"- [{t['ticket_id']}]({ticket_link}): {t['summary']} (Similarity: {t['similarity']:.2f})")
        return SIMILAR_TICKETS_TEMPLATE.format(similar_tickets="\n".join(similar_tickets_text))

def format_final_response(greeting: str, analysis: str, similar_tickets_section: str) -> str:
    """
    Combines greeting, analysis, and similar tickets into the final comment.
    """
    return f"{greeting}{analysis}{similar_tickets_section}"