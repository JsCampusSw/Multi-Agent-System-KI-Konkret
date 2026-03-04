"""
Test: Finance Agent
Testet OCR + LLM-Extraktion + DATEV Export mit einer Demo-Rechnung.
"""
import json
import sys
import os

# Ensure we're in the right working directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

from agents.finance_agent import run_finance_agent

# ── Demo: Direkt einen Text-Mock testen (ohne echtes PDF) ──────────────────
# Wir testen die Kernlogik mit dem bereits implementierten _extract_from_text
from agents.finance_agent import FinanceAgent

print("=" * 60)
print("💰 Finance Agent – Test")
print("=" * 60)

# Schritt 1: OCR-Text simulieren (wie nach einem echten PDF-Scan)
mock_ocr_text = """
RECHNUNG

Rechnungsaussteller: TechSupply GmbH
Musterstraße 42, 70173 Stuttgart

Rechnungsnummer: RE-2026-0042
Rechnungsdatum: 15.02.2026
Fälligkeitsdatum: 01.03.2026

Rechnungsempfänger: KI Konkret GmbH

Leistungsübersicht:
Pos. 1 – Cloud-Hosting-Paket (Business)    1x   890,00 €
Pos. 2 – KI-Software Lizenz (Jahresabo)   1x   700,00 €
Pos. 3 – Technischer Support (10h)        10x    42,00 €  Gesamt: 420,00 €

Nettobetrag:    2.010,00 €
MwSt. 19%:       381,90 €
Bruttobetrag:  2.391,90 €

IBAN: DE89 3704 0044 0532 0130 00
USt-IdNr.: DE 123 456 789
"""

print("\n📄 Teste LLM-Extraktion mit simuliertem OCR-Text...")
agent = FinanceAgent()
result = agent._extract_from_text(mock_ocr_text)

if "error" in result:
    print(f"❌ Fehler: {result['error']}")
    sys.exit(1)

print("\n✅ Extraktion erfolgreich!")
print(f"   Kreditor:     {result.get('creditor')}")
print(f"   Rech.-Nr.:    {result.get('invoice_number')}")
print(f"   Datum:        {result.get('date')}")
print(f"   Netto:        {result.get('amount_net')} {result.get('currency')}")
print(f"   Brutto:       {result.get('amount_gross')} {result.get('currency')}")
print(f"   MwSt:         {result.get('vat_rate')} ({result.get('vat_amount')})")
print(f"   Konto:        {result.get('account_suggestion')}")

items = result.get("line_items", [])
if items:
    # Nur echte Dict-Items anzeigen (LLM-Artefakte filtern)
    real_items = [i for i in items if isinstance(i, dict)]
    if real_items:
        print(f"\n   Positionen ({len(real_items)}):")
        for i, item in enumerate(real_items, 1):
            print(f"   {i}. {item.get('description')} | {item.get('total')}")
    else:
        print(f"\n   Positionen: keine strukturierten Positionen extrahiert.")

# DATEV Export
datev = agent._build_datev_export(result)
print("\n📤 DATEV JSON Export:")
print(json.dumps(datev, ensure_ascii=False, indent=2))

# ── Schritt 2: Echter PDF-Test (falls vorhanden) ───────────────────────────
pdf_test_path = "data/inputs/test_rechnung.pdf"
if os.path.exists(pdf_test_path):
    print(f"\n\n{'=' * 60}")
    print(f"📄 Teste echtes PDF: {pdf_test_path}")
    full_result = run_finance_agent(pdf_test_path)
    if "error" in full_result:
        print(f"❌ Fehler: {full_result['error']}")
    else:
        inv = full_result.get("invoice_data", {})
        print(f"✅ Kreditor: {inv.get('creditor')} – {inv.get('amount_gross')} {inv.get('currency')}")
else:
    print(f"\nℹ️  Kein Test-PDF unter '{pdf_test_path}' – PDF-OCR-Test übersprungen.")
    print("   Lege eine Rechnung als 'data/inputs/test_rechnung.pdf' ab um zu testen.")

print("\n✅ Finance Agent Test abgeschlossen!")
