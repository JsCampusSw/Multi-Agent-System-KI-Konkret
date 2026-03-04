from agents.comms_agent import run_comms_agent
import time

# Beispiel: Eine Anfrage zur KI Konkret Veranstaltung
sender = "Prof. Dr. Weber (Hochschule)"
email_text = """
Sehr geehrte Damen und Herren,

ich würde gerne mit einer Studentengruppe am KI Konkret Event teilnehmen.
Gibt es noch freie Plätze für den Workshop um 14 Uhr?
Außerdem benötigen wir eine Rechnung vorab.

Mit freundlichen Grüßen,
Weber
"""

print(f"--- 📨 Neue E-Mail von {sender} ---\n")

start_time = time.time()
result = run_comms_agent(sender, email_text)
end_time = time.time()

print(f"\n⏱️  Verarbeitungszeit: {end_time - start_time:.2f} Sekunden")

if "error" in result:
    print(f"❌ Fehler: {result['error']}")
else:
    print("-" * 40)
    print(f"📂 Kategorie:   {result.get('category')}")
    print(f"🔥 Dringlichkeit: {result.get('urgency')}")
    print(f"🧠 Sentiment:   {result.get('sentiment')}")
    print("-" * 40)
    print(f"📝 Entwurf:\n{result.get('draft_reply')}")
    print("-" * 40)