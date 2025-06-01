
# Jira AI Bot

## Overview
The Jira AI Bot is a Python-based application that automates ticket creation and analysis in Jira. It uses the `gemma3:1b` language model (via `langchain-ollama`) to perform ticket triage, root cause analysis, and similarity checks for Jira tickets. The bot runs in a Docker container, polls for new tickets, and adds analysis comments. It supports creating tickets of various types (e.g., Bug, Support, Task) and integrates with Jira’s API for seamless ticket management.

## Features
- **Ticket Creation**: Create Jira tickets with specified types (e.g., Bug, Support, Task).
- **Ticket Analysis**: Performs initial triage for short or non-Bug/Support tickets and root cause analysis for detailed Bug/Support tickets.
- **Similarity Check**: Identifies similar tickets using `gemma3:1b`
- **Attachment Handling**: Fetches and analyzes text-based attachments (e.g., `.log`, `.txt`) for root cause analysis.
- **Polling**: Continuously monitors Jira for new tickets matching a specified JQL filter.

## Prerequisites
- **Docker**: Installed to build and run the container.
- **Gemma3**: Running with the `gemma3:1b`
- **Jira Account**: Access to a Jira instance with an API token and project key.
- **Python 3.10**: If running outside Docker (not recommended).

## Installation
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd jira-ai-bot
   ```

2. **Set Up Environment Variables**:
   Create a `.env` file in the project root with the following:
   ```
   JIRA_URL=https://your-jira-instance.atlassian.net
   JIRA_USERNAME=your-email@example.com
   JIRA_API_TOKEN=your-api-token
   JQL_FILTER=project = IDUN AND issuetype in (Bug, Support) AND status = "To Do"
   ```
   Replace values with your Jira instance details. Generate an API token from Jira settings.

3. **Build and Run the Docker Container**:
   ```bash
   docker build -t jira-ai-bot .
   docker run --env-file .env jira-ai-bot
   ```

## Project Structure
- `agent_template.py`: Defines response templates and prompts for ticket analysis and similarity checks.
- `ticket_analyzer.py`: Uses `gemma3:1b` to analyze tickets (triage or root cause) and format responses.
- `jira_client.py`: Handles Jira API interactions for ticket creation, retrieval, and commenting.
- `similarity_checker.py`: Performs similarity checks using `gemma3:1b`.
- `jira_agent.py`: Core bot logic for creating and processing tickets.
- `main.py`: Entry point with example ticket creation and polling setup.
- `Dockerfile`: Defines the Docker container setup.
- `requirements.txt`: Lists Python dependencies (`jira`, `langchain-ollama`).

## Usage

Modify `ticket_type` (e.g., "Support", "Task") and `project_key` as needed.

### Polling for New Tickets
The bot polls Jira every 60 seconds for new tickets matching the JQL filter, analyzes them, and adds comments. Configure `JQL_FILTER` in `.env` to change the scope.

### Similarity Checks
The bot uses `gemma3:1b` to compare new tickets against existing ones. It identifies highly similar tickets (similarity > 0.9 for summary or > 0.7 for description) or lists up to 3 similar tickets with scores.

## Configuration
- **Jira Project Key**: Set `project_key` in `create_ticket` calls to match your Jira project (e.g., `IDUN`).
- **Ticket Types**: Use valid Jira issue types (e.g., Bug, Support, Task) in `create_ticket`.
- **Similarity Thresholds**: Adjust thresholds in `agent_template.py` (`PROMPT_SCENARIOS['similarity_check']`) if needed:
  - Summary similarity: 0.9
  - Description similarity: 0.7
- **Polling Interval**: Change `poll_interval` in `main.py` or `jira_agent.py` (default: 60 seconds).

## Troubleshooting
- **Jira API Issues**: Verify `JIRA_URL`, `JIRA_USERNAME`, and `JIRA_API_TOKEN`. Ensure the project key and issue types are valid.
- **Similarity Check Failures**: If cloned tickets aren’t detected, lower similarity thresholds in `agent_template.py` or provide sample tickets for prompt tuning.
- **Docker Issues**: Ensure Docker is running and the `.env` file is correctly formatted.

## Dependencies
- `jira==3.8.0`: For Jira API interactions.
- `langchain-ollama==0.1.0`: For `gemma3:1b` LLM integration.

## Notes
- The bot uses `gemma3:1b` for all analysis and similarity checks, ensuring lightweight operation.
- Cloned tickets should be detected by the LLM’s contextual comparison. If issues persist, provide sample ticket data for further prompt optimization.
- For production, secure the `.env` file and consider increasing the polling interval to reduce API load.

## License
MIT License (modify as per your project’s requirements).
