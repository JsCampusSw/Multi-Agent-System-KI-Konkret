import os
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# 1. Whisper Audio → Text
def transcribe_audio(audio_path: str, model_size: str = "turbo") -> str:
    """
    Transkribiert eine Audio-Datei mit OpenAI Whisper (lokal, CPU).
    Unterstützte Formate: WAV, MP3, M4A, OGG, FLAC
    """
    if not os.path.exists(audio_path):
        return f"[Fehler: Datei nicht gefunden: {audio_path}]"

    try:
        import whisper
        print(f"🎙️  Whisper: Lade Modell '{model_size}'...")
        model = whisper.load_model(model_size)
        print(f"   Transkribiere '{os.path.basename(audio_path)}'...")
        result = model.transcribe(audio_path, language="de")
        text = result["text"].strip()
        print(f"   ✅ Transkription ({len(text)} Zeichen): {text[:80]}...")
        return text
    except ImportError:
        return "[Fehler: openai-whisper nicht installiert. Bitte 'pip install openai-whisper' ausführen.]"
    except Exception as e:
        return f"[Whisper Fehler: {str(e)}]"


# 2. Sales Agent Klasse
class SalesAgent:
    def __init__(self, model_name: str = "llama3.2:latest"):
        self.llm = ChatOllama(model=model_name, temperature=0.3)
        self.parser = StrOutputParser()

    def generate_proposal(self, bullet_points: str) -> str:
        """
        Erstellt ein formatiertes Angebot aus Stichpunkten.
        Typischer Input: Diktat oder Notizen nach Kundentermin.
        """
        print("📝 Sales Agent: Generiere Angebot aus Stichpunkten...")

        system_prompt = """Du bist ein erfahrener Vertriebsassistent der Firma 'KI Konkret GmbH'.

Deine Aufgabe: Erstelle aus den folgenden Stichpunkten (Diktat nach Kundentermin) ein professionelles, 
strukturiertes Angebot auf Deutsch im Corporate Design.

FORMAT DES ANGEBOTS:
---
**KI Konkret GmbH**  
Angebot Nr.: [generiere z.B. ANG-2026-001]  
Datum: [heutiges Datum]  
An: [Kundenname aus Stichpunkten]

**Betreff:** Angebot für [Projekt/Produkt aus Stichpunkten]

---

Sehr geehrte Damen und Herren,

[Einleitung: Bezug auf das Gespräch, professionell]

**Leistungsumfang:**

| Pos. | Beschreibung | Menge | Einzelpreis | Gesamtpreis |
|------|-------------|-------|-------------|-------------|
[Tabelle aus Stichpunkten ableiten]

**Zahlungsbedingungen:** [aus Stichpunkten oder Standard: 14 Tage netto]

**Projektlaufzeit:** [aus Stichpunkten]

[Abschluss: Gesprächsbereitschaft signalisieren]

Mit freundlichen Grüßen,  
[Vertriebsmitarbeiter Name aus Stichpunkten oder 'Das KI Konkret Team']
---

WICHTIG: 
- Fülle alle Felder sinnvoll aus den Stichpunkten.
- Erfinde keine Preise, nutze Platzhalter wie [Preis nach Vereinbarung] wenn nötig.
- Schreibe professionell und klar.
"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Stichpunkte aus dem Kundentermin:\n\n{bullet_points}")
        ])

        chain = prompt | self.llm | self.parser

        try:
            result = chain.invoke({"bullet_points": bullet_points})
            print(f"   ✅ Angebot generiert ({len(result)} Zeichen).")
            return result
        except Exception as e:
            return f"[Fehler bei Angebotsgenerierung: {str(e)}]"

    def polish_proposal(self, proposal_text: str) -> str:
        """
        Überarbeitet einen bestehenden Angebotstext stilistisch.
        Verbessert: Formulierungen, Formalität, Klarheit, Corporate Design.
        """
        print("✨ Sales Agent: Polishing läuft...")

        system_prompt = """Du bist ein professioneller Lektor und Kommunikationsexperte für B2B-Texte.

Deine Aufgabe: Überarbeite das folgende Angebot stilistisch und sprachlich.

VERBESSERUNGEN:
1. Formulierungen professioneller und überzeugender gestalten
2. Grammatik und Rechtschreibung korrigieren  
3. Fluss und Lesbarkeit verbessern
4. Fachbegriffe korrekt einsetzen
5. Den professionellen, vertrauenswürdigen Ton der Firma KI Konkret GmbH stärken
6. Keine inhaltlichen Änderungen – nur Stil und Sprache

Gib NUR den überarbeiteten Text zurück, keine Erklärungen.
"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Originaler Angebotstext:\n\n{proposal_text}")
        ])

        chain = prompt | self.llm | self.parser

        try:
            result = chain.invoke({"proposal_text": proposal_text})
            print(f"   ✅ Polishing abgeschlossen.")
            return result
        except Exception as e:
            return f"[Fehler beim Polishing: {str(e)}]"


# 3. Öffentliche Wrapper-Funktionen
def run_sales_agent(source: str, mode: str = "text") -> dict:
    """
    Einstiegspunkt für den Sales Agent.

    Args:
        source: Entweder Dateipfad (mode='audio') oder Stichpunkt-Text (mode='text').
        mode: 'audio' → Whisper Transkription + Angebot | 'text' → direkt Angebot
    
    Returns:
        dict mit 'transcript', 'proposal', 'mode'
    """
    agent = SalesAgent()
    transcript = ""

    if mode == "audio":
        transcript = transcribe_audio(source)
        if transcript.startswith("[Fehler") or transcript.startswith("[Whisper"):
            return {"error": transcript, "mode": mode}
        bullet_points = transcript
    else:
        bullet_points = source
        transcript = source

    proposal = agent.generate_proposal(bullet_points)

    return {
        "transcript": transcript,
        "proposal": proposal,
        "mode": mode,
    }


def run_polish(proposal_text: str) -> str:
    """Polishes einen Angebotstext und gibt den überarbeiteten Text zurück."""
    agent = SalesAgent()
    return agent.polish_proposal(proposal_text)
