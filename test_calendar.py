from agents.scheduler_agent import run_scheduler

print("--- 📅 Scheduler Test ---")
print("Bitte Browser-Fenster beachten für Google Login (nur beim ersten Mal)!")

# Test 1: Abfrage
# print("Test 1: Termine abrufen...")
# res = run_scheduler("Was steht heute an?")
# print(res)

# Test 2: Buchen
input_text = "Buche ein Meeting mit Herrn Müller für morgen um 15 Uhr. Mit dem Titel Stakeholder Meeting und einer Dauer von 75 Minuten."
print(f"\nUser: {input_text}")

res = run_scheduler(input_text)
print("\n--- Ergebnis ---")
print(f"KI sagt: {res.get('ai_response')}")
print(f"Tool sagt: {res.get('tool_result')}")