from dotenv import load_dotenv
from agents.comms_agent import run_comms_agent

# Lade API Keys
load_dotenv()

# Test-Szenario 1: Ein wütender Kunde (typisch für Manufacturing Demo)
sender = "Hans Müller (Müller CNC Frästechnik)"
email_text = """
Hallo Team,
die Maschine, die ihr letzte Woche geliefert habt, macht schon wieder Probleme!
Der Sensor fällt dauernd aus. Ich brauche SOFORT jemanden hier, sonst steht die Produktion still.
Das ist inakzeptabel!
"""

print(f"--- Eingehende E-Mail von {sender} ---\n")
print(f"Inhalt: {email_text}\n")
print("🤖 Agent denkt nach...\n")

result = run_comms_agent(sender, email_text)

# Ergebnis prüfen und ausgeben
if isinstance(result, dict) and "error" not in result:
    # WICHTIG: Zugriff jetzt mit ['key'] statt .key
    print(f"📂 Kategorie:   {result.get('category', 'N/A')}")
    print(f"🔥 Dringlichkeit: {result.get('urgency', 'N/A')}")
    print(f"🧠 Sentiment:   {result.get('sentiment', 'N/A')}")
    print(f"📝 Zusammenfassung: {result.get('summary', 'N/A')}")
    print("-" * 30)
    print(f"✉️  ENTWORFENE ANTWORT:\n{result.get('draft_reply', 'Kein Entwurf generiert')}")
else:
    print(f"Fehler bei der Verarbeitung: {result}")