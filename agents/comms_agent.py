import json
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

# 1. Definiere die gewünschte Struktur (für die Doku & Prompt)
class EmailAnalysis(BaseModel):
    category: str = Field(description="Kategorie: 'Support', 'Sales', 'Spam', 'Meeting', 'Intern'")
    urgency: str = Field(description="Dringlichkeit: 'Low', 'Medium', 'High'")
    sentiment: str = Field(description="Stimmung: 'Positive', 'Neutral', 'Negative', 'Angry'")
    summary: str = Field(description="Zusammenfassung des Anliegens in 1 Satz.")
    draft_reply: str = Field(description="Ein höflicher, professioneller Antwortentwurf auf Deutsch.")

# 2. Der Agent mit Ollama Backend
class CommsAgent:
    def __init__(self, model_name="gpt-oss:20b"):
        # WICHTIG: format="json" aktiviert den JSON-Mode von Ollama
        self.llm = ChatOllama(
            model=model_name,
            temperature=0,
            format="json" 
        )
        
        # Parser für LangChain
        self.parser = JsonOutputParser(pydantic_object=EmailAnalysis)

    def process_email(self, sender: str, content: str):
        print(f"🦙 Llama3 denkt nach über E-Mail von: {sender}...")
        
        # System-Prompt angepasst für JSON Mode
        system_prompt = """Du bist ein intelligenter E-Mail-Assistent für die Firma 'KI Konkret GmbH'.
        
        Deine Aufgabe:
        1. Analysiere die eingehende E-Mail.
        2. Extrahiere Metadaten (Kategorie, Dringlichkeit, Stimmung).
        3. Schreibe einen professionellen Antwortentwurf auf Deutsch.
        
        WICHTIG: Antworte AUSSCHLIESSLICH im JSON-Format. Keine Einleitung, kein Markdown, nur das JSON Objekt.
        Halte dich strikt an diese Struktur:
        {format_instructions}
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Absender: {sender}\n\nE-Mail Inhalt:\n{content}")
        ])

        # Chain: Prompt -> LLM -> JSON Parser
        chain = prompt | self.llm | self.parser
        
        try:
            # Invoke mit Format-Instruktionen
            result = chain.invoke({
                "sender": sender, 
                "content": content,
                "format_instructions": self.parser.get_format_instructions()
            })
            return result
        except Exception as e:
            return {"error": f"Fehler bei der Verarbeitung: {str(e)}"}

# Wrapper für einfachen Aufruf
def run_comms_agent(sender, content):
    agent = CommsAgent()
    return agent.process_email(sender, content)