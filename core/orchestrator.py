import os
import time
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from core.state import AgentState


# ─────────────────────────────────────────────
# NODE 1: Router – klassifiziert den Input-Typ
# ─────────────────────────────────────────────
def router_node(state: AgentState) -> AgentState:
    """
    Klassifiziert den eingehenden Input und entscheidet,
    welcher Agent aufgerufen wird.
    """
    input_type = state.get("input_type", "").lower()

    # Direktes Mapping wenn input_type bereits gesetzt (z.B. von UI)
    known_types = {
        "email": "comms",
        "calendar": "scheduler",
        "invoice": "finance",
        "audio": "sales",
        "text_proposal": "sales",
    }

    if input_type in known_types:
        decision = known_types[input_type]
        print(f"🔀 Router: input_type='{input_type}' → Agent '{decision}'")
        return {**state, "agent_decision": decision}

    # Fallback: LLM-basierte Klassifikation
    llm = ChatOllama(model="llama3.2:latest", temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "Klassifiziere die folgende Nutzereingabe in eine dieser Kategorien und antworte NUR mit dem Schlüsselwort:\n"
            "- 'comms' (E-Mail, Kundenanfrage, Beschwerde)\n"
            "- 'scheduler' (Termin, Meeting, Kalender, Datum)\n"
            "- 'finance' (Rechnung, Buchhaltung, Zahlung, OCR)\n"
            "- 'sales' (Angebot, Stichpunkte, Diktat, Verkauf)\n"
            "Antworte ausschliesslich mit einem der Schlüsselwörter."
        )),
        ("human", "{input}")
    ])
    chain = prompt | llm | StrOutputParser()
    try:
        decision = chain.invoke({"input": state["input"]}).strip().lower()
        if decision not in ["comms", "scheduler", "finance", "sales"]:
            decision = "comms"  # Sicherer Default
        print(f"🔀 Router (LLM): → Agent '{decision}'")
    except Exception:
        decision = "comms"

    return {**state, "agent_decision": decision}


# ─────────────────────────────────────────────
# NODE 2: Comms Agent
# ─────────────────────────────────────────────
def comms_node(state: AgentState) -> AgentState:
    from agents.comms_agent import run_comms_agent
    meta = state.get("metadata", {})
    sender = meta.get("sender", "Unbekannter Absender")
    result = run_comms_agent(sender, state["input"])
    return {**state, "agent_output": result}


# ─────────────────────────────────────────────
# NODE 3: Scheduler Agent
# ─────────────────────────────────────────────
def scheduler_node(state: AgentState) -> AgentState:
    from agents.scheduler_agent import run_scheduler
    result = run_scheduler(state["input"])
    return {**state, "agent_output": result}


# ─────────────────────────────────────────────
# NODE 4: Finance Agent
# ─────────────────────────────────────────────
def finance_node(state: AgentState) -> AgentState:
    from agents.finance_agent import run_finance_agent
    meta = state.get("metadata", {})
    pdf_path = meta.get("pdf_path", state["input"])
    result = run_finance_agent(pdf_path)
    return {**state, "agent_output": result}


# ─────────────────────────────────────────────
# NODE 5: Sales Agent
# ─────────────────────────────────────────────
def sales_node(state: AgentState) -> AgentState:
    from agents.sales_agent import run_sales_agent
    meta = state.get("metadata", {})
    mode = state.get("input_type", "text_proposal")
    
    if mode == "audio":
        audio_path = meta.get("audio_path", state["input"])
        result = run_sales_agent(audio_path, mode="audio")
    else:
        result = run_sales_agent(state["input"], mode="text")

    return {**state, "agent_output": result}


# ─────────────────────────────────────────────
# CONDITIONAL EDGE: entscheidet den nächsten Knoten
# ─────────────────────────────────────────────
def route_to_agent(state: AgentState) -> str:
    return state.get("agent_decision", "comms")


# ─────────────────────────────────────────────
# GRAPH AUFBAU
# ─────────────────────────────────────────────
def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    # Knoten hinzufügen
    graph.add_node("router", router_node)
    graph.add_node("comms", comms_node)
    graph.add_node("scheduler", scheduler_node)
    graph.add_node("finance", finance_node)
    graph.add_node("sales", sales_node)

    # Einstieg
    graph.set_entry_point("router")

    # Router → jeweiliger Agent (bedingte Kante)
    graph.add_conditional_edges(
        "router",
        route_to_agent,
        {
            "comms": "comms",
            "scheduler": "scheduler",
            "finance": "finance",
            "sales": "sales",
        }
    )

    # Alle Agents → END
    graph.add_edge("comms", END)
    graph.add_edge("scheduler", END)
    graph.add_edge("finance", END)
    graph.add_edge("sales", END)

    return graph.compile()


# Singleton Graph für Wiederverwendung
_graph = None

def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


# ─────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────
def run_orchestrator(
    query: str,
    input_type: str = "",
    metadata: dict | None = None,
) -> dict:
    """
    Führt den kompletten Orchestrator-Workflow aus.

    Args:
        query:      Eingabetext oder Dateipfad
        input_type: Optional bekannter Kanaltyp ('email','calendar','invoice','audio','text_proposal')
        metadata:   Zusätzliche Daten (sender, pdf_path, audio_path)
    
    Returns:
        dict mit agent_decision und agent_output
    """
    state: AgentState = {
        "input": query,
        "input_type": input_type,
        "agent_decision": "",
        "agent_output": {},
        "metadata": metadata if metadata is not None else {},
        "error": None,
    }

    start = time.time()
    try:
        graph = get_graph()
        result = graph.invoke(state)
        elapsed = time.time() - start
        print(f"\n✅ Orchestrator fertig in {elapsed:.2f}s | Agent: {result['agent_decision']}")
        return result
    except Exception as e:
        return {**state, "error": str(e), "agent_output": {"error": str(e)}}
