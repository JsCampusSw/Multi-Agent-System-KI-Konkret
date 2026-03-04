"""
Test: Sales Agent
Testet Angebotsgenerierung aus Stichpunkten und Polishing-Funktion.
"""
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

from agents.sales_agent import run_sales_agent, run_polish

print("=" * 60)
print("💼 Sales Agent – Test")
print("=" * 60)

# ── Test 1: Angebot aus Stichpunkten ──────────────────────────────────────
print("\n📝 Test 1: Angebot aus Stichpunkten generieren...")

bullet_points = """
Kunde: Mayer GmbH, Ansprechpartner Herr Fischer
Produkt: KI-Automatisierungslösung für Buchhaltung
5 User-Lizenzen, SaaS-Modell
Implementierung: 3 Monate (inkl. Onboarding)
Training + Support inklusive (1 Jahr)
Preis: ca. 25.000 EUR netto Setup + 1.200 EUR/Monat
Liefertermin: Q2 2026
Besprochen: Referenzprojekte zeigen, Demo-Zugang für 30 Tage
"""

result = run_sales_agent(bullet_points, mode="text")

if "error" in result:
    print(f"❌ Fehler: {result['error']}")
    sys.exit(1)

proposal = result.get("proposal", "")
print(f"\n✅ Angebot generiert ({len(proposal)} Zeichen):")
print("-" * 50)
print(proposal[:600] + ("..." if len(proposal) > 600 else ""))
print("-" * 50)

# ── Test 2: Polishing ──────────────────────────────────────────────────────
print("\n✨ Test 2: Polishing des generierten Angebots...")
polished = run_polish(proposal)
print(f"✅ Polishing abgeschlossen ({len(polished)} Zeichen).")

# Vergleich: vorher/nachher
print(f"\n   Original (erste 200 Zeichen):  {proposal[:200]}")
print(f"   Polished (erste 200 Zeichen): {polished[:200]}")

# ── Test 3: Audio (optional) ───────────────────────────────────────────────
audio_test_path = "data/inputs/test_audio.wav"
if os.path.exists(audio_test_path):
    print(f"\n\n{'=' * 60}")
    print(f"🎙️  Test 3: Whisper Transkription von '{audio_test_path}'...")
    audio_result = run_sales_agent(audio_test_path, mode="audio")
    if "error" in audio_result:
        print(f"❌ Fehler: {audio_result['error']}")
    else:
        print(f"✅ Transkript: {audio_result.get('transcript', '')[:200]}")
        print(f"✅ Angebot aus Audio generiert ({len(audio_result.get('proposal',''))} Zeichen).")
else:
    print(f"\nℹ️  Kein Test-Audio unter '{audio_test_path}' – Audio-Test übersprungen.")
    print("   Lege eine WAV-Datei als 'data/inputs/test_audio.wav' ab um zu testen.")

print("\n✅ Sales Agent Test abgeschlossen!")
