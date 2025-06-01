"""
Handles similarity checks for Jira tickets using gemma3:1b LLM.
"""

from typing import List, Dict
from agent_template import get_similarity_check_prompt, format_similar_tickets
from langchain_ollama import OllamaLLM

class SimilarityChecker:
    def __init__(self):
        self.llm = OllamaLLM(model="gemma3:1b", temperature=0.7)
        self.tickets = []

    def add_ticket(self, ticket: Dict):
        """Add a ticket to the internal store for similarity checks."""
        self.tickets.append(ticket)

    def find_similar_tickets(self, new_ticket: Dict, jira_base_url: str) -> List[Dict]:
        """
        Find similar tickets using gemma3:1b LLM.
        """
        new_ticket_id = new_ticket.get("ticket_id")
        new_summary = new_ticket.get("summary", "")
        new_description = new_ticket.get("description", "")

        # Prepare existing tickets data for LLM prompt, excluding the new ticket
        existing_tickets_data = "; ".join(
            f"{ticket['ticket_id']}: Summary - '{ticket['summary']}', Description - '{ticket['description']}'"
            for ticket in self.tickets if ticket['ticket_id'] != new_ticket_id
        )

        # Use LLM for similarity check
        prompt = get_similarity_check_prompt(
            new_ticket_id=new_ticket_id,
            new_ticket_summary=new_summary,
            new_ticket_description=new_description,
            existing_tickets_data=existing_tickets_data
        )
        try:
            response = self.llm.invoke(prompt).strip()
            # Parse LLM response
            if response.startswith("http"):
                ticket_id = response.split("/")[-1]
                return [{
                    "ticket_id": ticket_id,
                    "summary": "Highly similar ticket",
                    "similarity": 0.95
                }]
            else:
                similar_tickets = []
                for line in response.split("\n"):
                    if line.startswith("-"):
                        try:
                            parts = line.split(":")
                            ticket_id = parts[0].strip("- []").strip()
                            summary_score = parts[1].split("(Similarity:")
                            summary = summary_score[0].strip()
                            similarity = float(summary_score[1].strip(")").strip())
                            similar_tickets.append({
                                "ticket_id": ticket_id,
                                "summary": summary,
                                "similarity": similarity
                            })
                        except (IndexError, ValueError) as e:
                            print(f"Error parsing similarity response: {line}, {e}")
                            continue
                return similar_tickets
        except Exception as e:
            print(f"Error in similarity check for ticket {new_ticket_id}: {e}")
            return []