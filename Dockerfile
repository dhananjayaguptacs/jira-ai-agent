FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://ollama.com/install.sh | sh

COPY *.py ./
COPY requirements.txt .
COPY entrypoint.sh .

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x entrypoint.sh

ENV JIRA_URL=https://your-jira-instance.atlassian.net
ENV JIRA_USERNAME=your_email@example.com
ENV JIRA_API_TOKEN=your_api_token
ENV JQL_FILTER='project = YOUR_PROJECT AND issuetype in (Bug, Support) AND status = "To Do"'

ENTRYPOINT ["./entrypoint.sh"]