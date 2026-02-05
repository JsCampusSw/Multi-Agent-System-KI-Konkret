# 🤖 Enterprise Multi-Agent Orchestrator (EMAO)
### Showcase für das Event "KI Konkret" @ Campus Schwarzwald

![Event](https://img.shields.io/badge/Event-KI_Konkret-blue)
![Host](https://img.shields.io/badge/Location-Campus_Schwarzwald-green)
![Status](https://img.shields.io/badge/Demo-Live_Case-orange)
![Framework](https://img.shields.io/badge/Tech-LangGraph_&_Unsloth-purple)

## 💡 Über dieses Projekt

Dieses Repository enthält den **Live-Democase**, der im Rahmen des Events **"KI Konkret"** am Campus Schwarzwald vorgestellt wird. 

Es demonstriert, wie moderne **Multi-Agenten-Systeme (MAS)** komplexe Unternehmensprozesse automatisieren können, indem sie Aufgaben intelligent verteilen, anstatt sie monolithisch zu bearbeiten. Der Fokus liegt auf der praktischen Anwendbarkeit von KI im Mittelstand.

**Kernfrage der Demo:** *Wie kann ein einziges System E-Mails, Buchhaltungsbelege, Sprachnotizen und Kundenchats gleichzeitig managen?*

---

## 🏗 Architektur der Demo

Das System nutzt eine **Hub-and-Spoke-Architektur**. Ein zentraler "Router" (Orchestrator) analysiert den Input und aktiviert den passenden Experten-Agenten.

```mermaid
graph TD
    User((User / Input)) --> Router[🤖 Orchestrator]
    Router -->|E-Mail Entwürfe| Comms[📧 Comms Agent]
    Router -->|Angebots-Erstellung| Sales[💼 Sales Agent]
    Router -->|Beleg-Erfassung| Finance[💰 Finance Agent]
    Router -->|Termin-Koordination| Sched[📅 Scheduler Agent]
    Router -->|Web-Chat| Web[💬 Web Concierge]
    
    Comms <--> DB[(Shared Context)]
    Sales <--> DB
    Web <--> DB
