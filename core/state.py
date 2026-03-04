from typing import TypedDict, Optional


class AgentState(TypedDict):
    """Globaler State, der durch den LangGraph gereicht wird."""
    input: str                    # Ursprüngliche Eingabe des Users
    input_type: str               # Kanaltyp: 'email' | 'calendar' | 'invoice' | 'audio' | 'text_proposal'
    agent_decision: str           # Welcher Agent wurde gewählt
    agent_output: dict            # Ausgabe des gewählten Agents
    metadata: dict                # Zusätzliche Metadaten (Dateipfade, Timing etc.)
    error: Optional[str]          # Fehlermessage falls etwas schiefläuft