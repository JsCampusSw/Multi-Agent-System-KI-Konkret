import base64
import io
import os
from pathlib import Path

def _pdf_to_images(pdf_path: str) -> list[bytes]:
    """Konvertiert PDF-Seiten in PNG-Bytes (via pymupdf / fitz)."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        images = []
        for page in doc:
            pix = page.get_pixmap(dpi=200)
            images.append(pix.tobytes("png"))
        doc.close()
        return images
    except ImportError:
        raise ImportError("PyMuPDF nicht installiert. Bitte 'pip install pymupdf' ausführen.")


def _ocr_with_vision_llm(image_bytes: bytes, model: str = "llava") -> str:
    """Nutzt Ollama Vision-Modell (LLaVA) zur Texterkennung."""
    try:
        import ollama
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        response = ollama.chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Du bist ein OCR-Experte. Extrahiere den GESAMTEN Text aus diesem "
                        "Rechnungsbild. Gib nur den extrahierten Text zurück, keine Erläuterungen."
                    ),
                    "images": [b64],
                }
            ],
        )
        return response["message"]["content"]
    except Exception as e:
        return f"[Vision OCR Fehler: {str(e)}]"


def _ocr_with_tesseract(image_bytes: bytes) -> str:
    """Fallback: Tesseract OCR."""
    try:
        from PIL import Image
        import pytesseract
        img = Image.open(io.BytesIO(image_bytes))
        return pytesseract.image_to_string(img, lang="deu+eng")
    except ImportError:
        return "[Fehler: Weder LLaVA noch Tesseract verfügbar.]"
    except Exception as e:
        return f"[Tesseract Fehler: {str(e)}]"


def extract_text_from_pdf(pdf_path: str, prefer_vision: bool = True) -> str:
    """
    Hauptfunktion: Extrahiert Text aus einer PDF-Rechnung.
    
    1. Konvertiert die erste Seite des PDFs in ein PNG.
    2. Versucht LLaVA Vision OCR (bevorzugt).
    3. Fällt auf Tesseract zurück.
    
    Returns: Extrahierter Text als String.
    """
    if not os.path.exists(pdf_path):
        return f"[Fehler: Datei nicht gefunden: {pdf_path}]"

    print(f"📄 OCR Tool: Verarbeite '{Path(pdf_path).name}'...")

    try:
        images = _pdf_to_images(pdf_path)
    except Exception as e:
        return f"[Fehler bei PDF-Konvertierung: {str(e)}]"

    if not images:
        return "[Fehler: Keine Seiten im PDF gefunden.]"

    # Nur erste Seite für Demo
    first_page = images[0]

    if prefer_vision:
        print("   🔭 Versuche LLaVA Vision OCR...")
        text = _ocr_with_vision_llm(first_page)
        if not text.startswith("[Vision OCR Fehler"):
            print("   ✅ Vision OCR erfolgreich.")
            return text
        print(f"   ⚠️  Vision fehlgeschlagen, nutze Tesseract Fallback...")

    return _ocr_with_tesseract(first_page)
