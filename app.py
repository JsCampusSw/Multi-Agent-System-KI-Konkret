import streamlit as st
import time
import json
import os
import tempfile
from agents.comms_agent import run_comms_agent
from agents.scheduler_agent import run_scheduler
from agents.finance_agent import run_finance_agent
from agents.sales_agent import run_sales_agent, run_polish


# ─────────────────────────────────────────────
# HELPER: Routing Flow Visualisierung
# ─────────────────────────────────────────────
def _routing_flow(active_start: str, active_end: str):
    """Zeigt den Routing-Pfad als kleine Badge-Kette an."""
    nodes = {
        "router":    "🔀 Router",
        "comms":     "📧 Comms",
        "scheduler": "📅 Scheduler",
        "finance":   "💰 Finance",
        "sales":     "💼 Sales",
    }
    html = ""
    path = ["router", active_end]
    for i, node in enumerate(path):
        css_class = "flow-node flow-active" if node in [active_start, active_end] else "flow-node"
        html += f'<span class="{css_class}">{nodes.get(node, node)}</span>'
        if i < len(path) - 1:
            html += '<span class="flow-arrow"> → </span>'
    st.markdown(f'<div style="margin-bottom:12px">{html}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="KI Konkret – Enterprise Agent Demo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .main-header h1 { color: #e0e0e0; margin: 0; font-size: 2rem; }
    .main-header p  { color: #a0aec0; margin: 0.3rem 0 0; }

    /* Agent Cards */
    .agent-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.6rem;
        transition: border-color 0.3s;
    }
    .agent-card:hover { border-color: rgba(99,179,237,0.4); }
    .agent-badge {
        display: inline-flex; align-items: center; gap: 6px;
        background: #2d3748; border-radius: 20px; padding: 4px 12px;
        font-size: 0.78rem; color: #63b3ed;
    }

    /* Result boxes */
    .result-box {
        background: #1a202c;
        border: 1px solid #2d3748;
        border-radius: 10px;
        padding: 1.2rem;
    }

    /* Flow nodes */
    .flow-node {
        display: inline-block;
        background: #2d3748; color: #e2e8f0;
        border-radius: 8px; padding: 5px 14px;
        font-size: 0.82rem; font-weight: 600;
        border: 1px solid #4a5568;
    }
    .flow-active {
        background: #2b6cb0; color: #fff;
        border-color: #63b3ed;
        box-shadow: 0 0 10px rgba(99,179,237,0.4);
    }
    .flow-arrow { color: #4a5568; font-size: 1.2rem; padding: 0 4px; }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background: #1a202c;
        border: 1px solid #2d3748;
        border-radius: 10px;
        padding: 12px 16px;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 KI Konkret")
    st.markdown("**Enterprise Agent Demo**")
    st.markdown("---")
    st.markdown("### 🟢 System Status")

    agents_status = [
        ("📧", "Comms Agent",    "E-Mail Analyse",      True),
        ("📅", "Scheduler Agent","Google Calendar",     True),
        ("💰", "Finance Agent",  "OCR + DATEV",         True),
        ("💼", "Sales Agent",    "Whisper + Angebot",   True),
        ("🔀", "Orchestrator",   "LangGraph Router",    True),
    ]
    for icon, name, desc, online in agents_status:
        status_color = "#48bb78" if online else "#fc8181"
        st.markdown(
            f"""<div class="agent-card">
            <span style="color:{status_color}; font-size:1.1rem;">●</span>
            <strong> {icon} {name}</strong><br/>
            <span style="color:#718096; font-size:0.8rem;">{desc}</span>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.write("### ⚙️ Debug")
    show_raw_json = st.checkbox("Raw JSON anzeigen", value=False)
    show_ocr_text = st.checkbox("OCR-Text anzeigen", value=False)

    st.markdown("---")
    st.caption("📍 KI Konkret @ Campus Schwarzwald")

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🤖 Enterprise Multi-Agent Orchestrator</h1>
    <p>Showcase für automatisierte Unternehmensprozesse · KI Konkret Demo</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab_email, tab_calendar, tab_finance, tab_sales = st.tabs([
    "📧  E-Mail Verarbeitung",
    "📅  Termin Koordination",
    "💰  Rechnung (OCR)",
    "💼  Angebot (Sales)",
])

# ══════════════════════════════════════════════
# TAB 1: COMMS AGENT
# ══════════════════════════════════════════════
with tab_email:
    col1, col2 = st.columns([1, 1.6])

    with col1:
        st.subheader("📥 Eingehende E-Mail")
        _routing_flow("router", "comms")
        with st.form("email_form"):
            sender = st.text_input("Absender", value="Hans Müller (Müller CNC Frästechnik)")
            email_content = st.text_area(
                "Nachricht",
                height=220,
                value=(
                    "Hallo Team,\n\ndie Maschine, die ihr letzte Woche geliefert habt, "
                    "macht schon wieder Probleme! Der Sensor fällt dauernd aus. "
                    "Ich brauche SOFORT jemanden hier, sonst steht die Produktion still.\n"
                    "Das ist inakzeptabel!\n\nGruß, Hans"
                ),
            )
            email_submit = st.form_submit_button("🚀 Comms Agent starten", type="primary")

    with col2:
        st.subheader("🧠 Agent Output")
        if email_submit:
            with st.status("🔍 Analysiere E-Mail...", expanded=True) as status:
                st.write("→ Routing an **Comms Agent**")
                st.write("→ Sentiment & Intent Analyse (Ollama)...")
                t0 = time.time()
                result = run_comms_agent(sender, email_content)
                elapsed = time.time() - t0
                status.update(label=f"✅ Fertig in {elapsed:.2f}s", state="complete", expanded=False)

            if isinstance(result, dict) and "error" not in result:
                m1, m2, m3 = st.columns(3)
                m1.metric("Kategorie",    result.get("category", "–"))
                m2.metric("Dringlichkeit", result.get("urgency", "–"))
                sentiment = result.get("sentiment", "Neutral")
                icons = {"Positive": "😊", "Negative": "😟", "Angry": "😡", "Neutral": "😐"}
                icon = next((v for k, v in icons.items() if k in sentiment), "😐")
                m3.metric("Stimmung", f"{icon} {sentiment}")

                st.markdown("---")
                st.info(f"**Zusammenfassung:** {result.get('summary', '–')}")
                st.subheader("✉️ Antwort-Entwurf")
                draft = st.text_area("Generierter Entwurf:", value=result.get("draft_reply", ""), height=220)

                if show_raw_json:
                    st.json(result)
            else:
                st.error(f"Fehler: {result}")
        else:
            st.info("Fülle links das Formular aus und klicke auf **Comms Agent starten**.")

# ══════════════════════════════════════════════
# TAB 2: SCHEDULER AGENT
# ══════════════════════════════════════════════
with tab_calendar:
    col1, col2 = st.columns([1, 1.6])

    with col1:
        st.subheader("📅 Terminanfrage")
        _routing_flow("router", "scheduler")
        with st.form("calendar_form"):
            st.caption("Beispiel: *Buche ein Strategie-Meeting mit Frau Schmidt für morgen um 10 Uhr.*")
            cal_input = st.text_area("Anweisung an Assistent", height=180)
            cal_submit = st.form_submit_button("📅 Scheduler starten", type="primary")

    with col2:
        st.subheader("🧠 Agent Output")
        if cal_submit:
            with st.status("📅 Prüfe Kalender...", expanded=True) as status:
                st.write("→ Routing an **Scheduler Agent**")
                st.write("→ Intent-Extraktion (Ollama)...")
                st.write("→ Verbinde mit Google Calendar API...")
                t0 = time.time()
                result = run_scheduler(cal_input)
                elapsed = time.time() - t0
                status.update(label=f"✅ Erledigt in {elapsed:.2f}s", state="complete", expanded=False)

            if isinstance(result, dict) and "error" not in result:
                st.success(f"🤖 **KI Antwort:** {result.get('ai_response')}")
                st.markdown("### 🛠 Tool Output (Google Calendar API)")
                action = result.get("action", "")
                if action == "create_event":
                    st.markdown(f"✅ **{result.get('tool_result')}**")
                    st.caption("Prüfe deinen Google Kalender – der Termin ist jetzt eingetragen!")
                else:
                    st.code(result.get("tool_result", ""), language="text")
                if show_raw_json:
                    st.json(result)
            else:
                st.error(f"Fehler: {result}")
        else:
            st.info("Stelle eine Terminanfrage und klicke auf **Scheduler starten**.")

# ══════════════════════════════════════════════
# TAB 3: FINANCE AGENT
# ══════════════════════════════════════════════
with tab_finance:
    col1, col2 = st.columns([1, 1.6])

    with col1:
        st.subheader("📄 PDF-Rechnung einreichen")
        _routing_flow("router", "finance")
        with st.form("finance_form"):
            uploaded_pdf = st.file_uploader(
                "Rechnung hochladen (PDF)",
                type=["pdf"],
                help="PDF-Rechnung hochladen – OCR + KI-Extraktion läuft automatisch.",
            )
            fin_submit = st.form_submit_button("💰 Finance Agent starten", type="primary")

    with col2:
        st.subheader("🧠 Agent Output")
        if fin_submit:
            if uploaded_pdf is None:
                st.warning("Bitte zuerst eine PDF-Datei hochladen.")
            else:
                # PDF temporär speichern
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_pdf.read())
                    pdf_path = tmp.name

                with st.status("💰 Verarbeite Rechnung...", expanded=True) as status:
                    st.write(f"→ Routing an **Finance Agent**")
                    st.write(f"→ OCR läuft (LLaVA Vision / Tesseract)...")
                    st.write(f"→ LLM extrahiert Rechnungsdaten...")
                    t0 = time.time()
                    result = run_finance_agent(pdf_path)
                    elapsed = time.time() - t0
                    status.update(label=f"✅ Fertig in {elapsed:.2f}s", state="complete", expanded=False)

                os.unlink(pdf_path)  # temp file löschen

                if "error" in result and result.get("error"):
                    st.error(f"Fehler: {result['error']}")
                else:
                    inv = result.get("invoice_data", {})

                    # Kernmetriken
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Kreditor",      inv.get("creditor", "–"))
                    m2.metric("Bruttobetrag",  f"{inv.get('amount_gross','–')} {inv.get('currency','EUR')}")
                    m3.metric("Datum",         inv.get("date", "–"))

                    st.markdown("---")
                    # Rechnungsdetails Tabelle
                    st.markdown("### 📋 Extrahierte Daten")
                    details = {
                        "Rechnungsnummer":  inv.get("invoice_number", "–"),
                        "Rechnungsdatum":   inv.get("date", "–"),
                        "Fälligkeitsdatum": inv.get("due_date", "–") or "–",
                        "Nettobetrag":      inv.get("amount_net", "–"),
                        "Bruttobetrag":     inv.get("amount_gross", "–"),
                        "MwSt-Satz":        inv.get("vat_rate", "–"),
                        "MwSt-Betrag":      inv.get("vat_amount", "–") or "–",
                        "Konto (Vorschlag)":inv.get("account_suggestion", "–"),
                    }
                    for k, v in details.items():
                        col_k, col_v = st.columns([1, 2])
                        col_k.write(f"**{k}**")
                        col_v.write(v)

                    # Positionen
                    line_items = inv.get("line_items", [])
                    if line_items:
                        st.markdown("### 🧾 Rechnungspositionen")
                        rows = []
                        for item in line_items:
                            if isinstance(item, dict):
                                rows.append(item)
                        if rows:
                            import pandas as pd
                            st.dataframe(
                                pd.DataFrame(rows).rename(columns={
                                    "description": "Beschreibung",
                                    "quantity": "Menge",
                                    "unit_price": "Einzelpreis",
                                    "total": "Gesamt",
                                }),
                                use_container_width=True,
                            )

                    # DATEV Export
                    st.markdown("### 📤 DATEV JSON Export")
                    datev = result.get("datev_json", {})
                    st.json(datev)
                    datev_str = json.dumps(datev, ensure_ascii=False, indent=2)
                    st.download_button(
                        "⬇️ DATEV JSON herunterladen",
                        data=datev_str,
                        file_name=f"datev_{inv.get('invoice_number','export')}.json",
                        mime="application/json",
                    )

                    if show_ocr_text:
                        with st.expander("🔍 OCR-Rohtext"):
                            st.text(result.get("ocr_text", ""))

                    if show_raw_json:
                        st.json(result)
        else:
            st.info("Lade eine PDF-Rechnung hoch und klicke auf **Finance Agent starten**.")

# ══════════════════════════════════════════════
# TAB 4: SALES AGENT
# ══════════════════════════════════════════════
with tab_sales:
    col1, col2 = st.columns([1, 1.6])

    with col1:
        st.subheader("💼 Angebot erstellen")
        _routing_flow("router", "sales")

        input_mode = st.radio(
            "Eingabe-Modus:",
            ["✍️ Stichpunkte (Text)", "🎙️ Sprachmemo (Audio)"],
            horizontal=True,
        )

        with st.form("sales_form"):
            if "Text" in input_mode:
                sales_input = st.text_area(
                    "Stichpunkte nach Kundentermin (Diktat)",
                    height=220,
                    value=(
                        "Kunde: Mayer GmbH, Ansprechpartner Herr Fischer\n"
                        "Produkt: KI-Automatisierungslösung für Buchhaltung\n"
                        "5 User-Lizenzen\n"
                        "Implementierung 3 Monate\n"
                        "Training + Support inklusive\n"
                        "Preis: ca. 25.000 EUR netto\n"
                        "Liefertermin: Q2 2026"
                    ),
                )
                audio_file = None
            else:
                sales_input = ""
                audio_file = st.audio_input(
                    "🎙️ Sprachmemo aufnehmen",
                    key="sales_audio_rec",
                )

            sales_submit = st.form_submit_button("💼 Angebot generieren", type="primary")

    with col2:
        st.subheader("🧠 Agent Output")

        if "sales_proposal" not in st.session_state:
            st.session_state.sales_proposal = ""
        if "sales_result" not in st.session_state:
            st.session_state.sales_result = None

        if sales_submit:
            mode = "text" if "Text" in input_mode else "audio"

            if mode == "audio" and audio_file is None:
                st.warning("Bitte zuerst eine Sprachaufnahme machen.")
            else:
                if mode == "audio":
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                        tmp.write(audio_file.read())
                        audio_path = tmp.name
                    source = audio_path
                else:
                    source = sales_input
                    audio_path = None

                steps = ["→ Routing an **Sales Agent**"]
                if mode == "audio":
                    steps.append("→ Whisper Transkription läuft (large-v3-turbo)...")
                steps.append("→ Ollama generiert Angebot...")

                with st.status("💼 Erstelle Angebot...", expanded=True) as status:
                    for s in steps:
                        st.write(s)
                    t0 = time.time()
                    result = run_sales_agent(source, mode=mode)
                    elapsed = time.time() - t0
                    status.update(label=f"✅ Fertig in {elapsed:.2f}s", state="complete", expanded=False)

                if audio_path:
                    os.unlink(audio_path)

                if "error" in result:
                    st.error(f"Fehler: {result['error']}")
                else:
                    st.session_state.sales_proposal = result.get("proposal", "")
                    st.session_state.sales_result = result

                    if mode == "audio":
                        with st.expander("🎙️ Whisper Transkript", expanded=True):
                            st.info(result.get("transcript", ""))

        if st.session_state.sales_proposal:
            result = st.session_state.sales_result
            st.markdown("### 📄 Generiertes Angebot")
            edited = st.text_area(
                "Angebot (bearbeitbar):",
                value=st.session_state.sales_proposal,
                height=380,
                key="proposal_editor",
            )

            pcol1, pcol2 = st.columns(2)
            with pcol1:
                if st.button("✨ Polishing starten", type="secondary"):
                    with st.spinner("✨ Stilüberarbeitung läuft..."):
                        polished = run_polish(edited)
                    st.session_state.sales_proposal = polished
                    st.rerun()

            with pcol2:
                st.download_button(
                    "⬇️ Angebot als TXT",
                    data=edited,
                    file_name="angebot_ki_konkret.txt",
                    mime="text/plain",
                )

            if show_raw_json and result:
                st.json(result)
        else:
            if not sales_submit:
                st.info("Gib Stichpunkte ein oder lade ein Sprachmemo hoch und klicke auf **Angebot generieren**.")