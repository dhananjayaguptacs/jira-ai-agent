"""
Main entry point for the Jira AI Bot.
"""

import os
from jira_agent import JiraAIBot

def main():
    JIRA_URL = os.getenv("JIRA_URL", "https://your-jira-instance.atlassian.net")
    USERNAME = os.getenv("JIRA_USERNAME", "your_email@example.com")
    API_TOKEN = os.getenv("JIRA_API_TOKEN", "your_api_token")
    JQL_FILTER = os.getenv("JQL_FILTER", 'project = YOUR_PROJECT AND issuetype in (Bug, Support) AND status = "To Do"')

    bot = JiraAIBot(jira_url=JIRA_URL, username=USERNAME, api_token=API_TOKEN, jql_filter=JQL_FILTER)

    # Start polling for new tickets
    bot.run(poll_interval=60)

if __name__ == "__main__":
    main()