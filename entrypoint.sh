#!/bin/bash
# Start Ollama server in the background
ollama serve &

# Wait for Ollama server to be ready
sleep 10

# Pull gemma3:1b model if not already present
ollama pull gemma3:1b

# Run the Jira AI bot
python main.py