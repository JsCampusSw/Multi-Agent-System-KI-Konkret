import json
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import Optional, List
from tools.ocr_tool import extract_text_from_pdf


# 1. Pydantic-Modell für strukturierte Rechnungsdaten
class LineItem(BaseModel):
    description: str = Field(description="Beschreibung der Position")
    quantity: Optional[str] = Field(description="Menge/Anzahl", default="1")
    unit_price: Optional[str] = Field(description="Einzelpreis", default="")
    total: Optional[str] = Field(description="Positionsbetrag", default="")

class InvoiceData(BaseModel):
    creditor: str = Field(description="Name des Rechnungsstellers / Kreditors")
    invoice_number: str = Field(description="Rechnungsnummer", default="")
    date: str = Field(description="Rechnungsdatum im Format YYYY-MM-DD oder DD.MM.YYYY")
    due_date: str = Field(description="Fälligkeitsdatum, leer falls nicht vorhanden", default="")
    amount_net: str = Field(description="Nettobetrag als String, z.B. '1190.00'")
    amount_gross: str = Field(description="Bruttobetrag als String, z.B. '1416.10'")
    currency: str = Field(description="Währungskürzel, z.B. 'EUR'", default="EUR")
    vat_rate: str = Field(description="Mehrwertsteuersatz, z.B. '19%'", default="19%")
    vat_amount: str = Field(description="Mehrwertsteuerbetrag als String", default="")
    line_items: List[LineItem] = Field(description="Liste der Rechnungspositionen", default=[])
    account_suggestion: str = Field(
        description=(
            "Vorgeschlagenes DATEV-Konto für die Vorkontierung, "
            "z.B. '4980 - Sonstige betriebliche Aufwendungen' oder '0410 - Maschinen'"
        )
    )
    datev_export: dict = Field(
        description="Strukturierter DATEV-kompatibler JSON-Export", default={}
    )


# 2. Einfache Kontenrahmen-Zuordnung (SKR04-Logik)
ACCOUNT_RULES = {
    "software": ("4940", "Werkzeuge, EDV-Software"),
    "cloud": ("4940", "Werkzeuge, EDV-Software"),
    "hosting": ("4940", "Werkzeuge, EDV-Software"),
    "server": ("4940", "Werkzeuge, EDV-Software"),
    "maschine": ("0410", "Maschinen"),
    "transport": ("4720", "Transportkosten"),
    "logistik": ("4720", "Transportkosten"),
    "büro": ("4930", "Büromaterial"),
    "papier": ("4930", "Büromaterial"),
    "beratung": ("4810", "Beratungskosten"),
    "consulting": ("4810", "Beratungskosten"),
    "marketing": ("4600", "Werbekosten"),
    "reise": ("4670", "Reisekosten"),
    "default": ("4980", "Sonstige betriebliche Aufwendungen"),
}

def _suggest_account(creditor: str, line_items: list) -> str:
    text = (creditor + " ".join([i.get("description", "") for i in line_items])).lower()
    for keyword, (account_num, account_name) in ACCOUNT_RULES.items():
        if keyword in text:
            return f"{account_num} – {account_name}"
    return f"{ACCOUNT_RULES['default'][0]} – {ACCOUNT_RULES['default'][1]}"


# 3. Finance Agent Klasse
class FinanceAgent:
    def __init__(self, model_name: str = "llama3.2:latest"):
        self.llm = ChatOllama(model=model_name, temperature=0, format="json")
        self.parser = JsonOutputParser(pydantic_object=InvoiceData)

    def _extract_from_text(self, ocr_text: str) -> dict:
        """Nutzt LLM um strukturierte Daten aus dem OCR-Text zu extrahieren."""
        system_prompt = """Du bist ein präziser Buchhaltungs-Assistent.
        
Deine Aufgabe: Extrahiere Rechnungsdaten aus dem folgenden OCR-Text und gib sie als valides JSON zurück.

REGELN:
1. Antworte AUSSCHLIESSLICH mit validem JSON – kein Markdown, keine Erklärungen.
2. Beträge immer als String mit Punkt als Dezimaltrennzeichen, z.B. "1190.00".
3. Datum im Format DD.MM.YYYY beibehalten oder in YYYY-MM-DD umwandeln.
4. Falls ein Wert nicht gefunden wird, nutze einen leeren String "".
5. Halte dich strikt an das vorgegebene Format:

{format_instructions}
"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Rechnungstext (OCR):\n\n{ocr_text}")
        ])

        chain = prompt | self.llm | self.parser

        try:
            result = chain.invoke({
                "ocr_text": ocr_text,
                "format_instructions": self.parser.get_format_instructions()
            })
            return result
        except Exception as e:
            return {"error": f"LLM-Extraktion fehlgeschlagen: {str(e)}"}

    def _build_datev_export(self, data: dict) -> dict:
        """Erstellt einen DATEV-kompatiblen JSON-Export."""
        return {
            "Buchungstyp": "Eingangsrechnung",
            "Kreditor": data.get("creditor", ""),
            "Rechnungsnummer": data.get("invoice_number", ""),
            "Belegdatum": data.get("date", ""),
            "Faelligkeitsdatum": data.get("due_date", ""),
            "Bruttobetrag": data.get("amount_gross", ""),
            "Nettobetrag": data.get("amount_net", ""),
            "Steuersatz": data.get("vat_rate", "19%"),
            "Steuerbetrag": data.get("vat_amount", ""),
            "Waehrung": data.get("currency", "EUR"),
            "Gegenkonto": data.get("account_suggestion", "4980 – Sonstige betr. Aufwendungen"),
            "Buchungstext": f"ER {data.get('creditor', '')} {data.get('date', '')}",
        }

    def process_invoice(self, pdf_path: str) -> dict:
        """
        Vollständiger Verarbeitungsweg:
        1. OCR aus PDF
        2. LLM-Extraktion der Rechnungsdaten
        3. Vorkontierung
        4. DATEV JSON Export
        """
        print(f"💰 Finance Agent: Starte Verarbeitung für '{pdf_path}'...")

        # Schritt 1: OCR
        ocr_text = extract_text_from_pdf(pdf_path)
        if ocr_text.startswith("[Fehler"):
            return {"error": ocr_text, "ocr_text": ""}

        print("   🧠 LLM extrahiert Rechnungsdaten...")

        # Schritt 2: LLM-Extraktion
        extracted = self._extract_from_text(ocr_text)
        if "error" in extracted:
            return {"error": extracted["error"], "ocr_text": ocr_text}

        # Schritt 3: Kontenvorschlag verbessern (regelbasiert ergänzen)
        raw_items = extracted.get("line_items", [])
        line_items_raw = []
        for item in raw_items:
            if isinstance(item, dict):
                line_items_raw.append(item)
            elif hasattr(item, "model_dump"):
                line_items_raw.append(item.model_dump())
            elif hasattr(item, "dict"):
                line_items_raw.append(item.dict())
            # Strings/Primitives (LLM-Artefakte) werden ignoriert
        extracted["line_items"] = line_items_raw

        if not extracted.get("account_suggestion"):
            extracted["account_suggestion"] = _suggest_account(
                extracted.get("creditor", ""), line_items_raw
            )

        # Schritt 4: DATEV Export
        extracted["datev_export"] = self._build_datev_export(extracted)

        print(f"   ✅ Extraktion abgeschlossen: {extracted.get('creditor')} – {extracted.get('amount_gross')} {extracted.get('currency')}")

        return {
            "ocr_text": ocr_text,
            "invoice_data": extracted,
            "datev_json": extracted["datev_export"],
        }


# Wrapper für einfachen Aufruf
def run_finance_agent(pdf_path: str) -> dict:
    agent = FinanceAgent()
    return agent.process_invoice(pdf_path)