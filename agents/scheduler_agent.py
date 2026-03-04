import datetime
import json
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from tools.calendar_tool import CalendarTool

# 1. Output Struktur für Llama 3
class CalendarIntent(BaseModel):
    action: str = Field(description="Was soll getan werden? 'list_events' oder 'create_event'")
    summary: str = Field(description="Titel des Termins als String (nur falls action='create_event')", default="")
    start_time: str = Field(description="ISO-8601 Startzeit (z.B. '2024-05-20T14:00:00').", default="")
    duration: int = Field(description="Dauer in Minuten", default=60)
    response_text: str = Field(description="Antwort an den User.")

class SchedulerAgent:
    def __init__(self, model_name="llama3.2:latest"):
        # temperature=0 ist wichtig für strikte Logik!
        self.llm = ChatOllama(model=model_name, format="json", temperature=0)
        self.parser = JsonOutputParser(pydantic_object=CalendarIntent)
        self.calendar = CalendarTool()

    def process_request(self, user_input: str):
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        weekday = datetime.datetime.now().strftime("%A")

        # --- VERBESSERTER PROMPT ---
        system_prompt = f"""Du bist ein strikter Kalender-Assistent.
        HEUTE ist: {weekday}, der {now_str}.
        
        Aufgabe: Extrahiere Termindaten aus dem User-Input.
        
        REGELN FÜR JSON:
        1. Antworte AUSSCHLIESSLICH mit validem JSON.
        2. Setze ALLE Strings in doppelte Anführungszeichen "". 
           Falsch: {{ "summary": Stakeholder-Meeting }}
           Richtig: {{ "summary": "Stakeholder-Meeting" }}
        3. Keine Kommentare, kein Markdown vor oder nach dem JSON.
        
        Beispiel Datum Berechnung:
        Heute = 2023-10-01. User: "Morgen 10 Uhr" -> "2023-10-02T10:00:00"
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "User Input: '{input}'\n\nFormat Instructions:\n{format_instructions}")
        ])

        chain = prompt | self.llm | self.parser

        try:
            print(f"🤖 Scheduler Agent verarbeitet: '{user_input}'...")
            
            intent = chain.invoke({
                "input": user_input,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            # --- Tool Ausführung ---
            result_data = ""
            
            if intent.get('action') == 'list_events':
                result_data = self.calendar.list_upcoming_events()
            
            elif intent.get('action') == 'create_event':
                if intent.get('start_time'):
                    result_data = self.calendar.create_event(
                        summary=intent.get('summary', 'Termin'),
                        start_time_iso=intent['start_time'],
                        duration_minutes=intent.get('duration', 60)
                    )
                else:
                    result_data = "Fehler: Konnte keine Startzeit berechnen."
            
            return {
                "ai_response": intent.get('response_text', 'Erledigt.'),
                "tool_result": result_data,
                "action": intent.get('action')
            }

        except Exception as e:
            # Fehler abfangen und anzeigen, damit die Demo nicht crasht
            print(f"❌ JSON Parsing Fehler: {str(e)}")
            return {
                "ai_response": "Entschuldigung, ich konnte die Anfrage aufgrund eines Formatierungsfehlers nicht verarbeiten.",
                "tool_result": f"Technischer Fehler: {str(e)}",
                "action": "error"
            }

def run_scheduler(user_input):
    agent = SchedulerAgent()
    return agent.process_request(user_input)