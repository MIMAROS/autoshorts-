# Architektur- und Deployment-Spezifikation: Antigravity Autonomous Social Media Agent (Ssemble-Klon)

Diese Spezifikation beschreibt die Transformation eines lokalen Multi-Agenten-Skripts in eine ortsunabhängig nutzbare Applikation (Phase 1) sowie die spätere Skalierung zu einer Mandantenfähigen SaaS-Plattform (Phase 2).

---

## Phase 1: Ortsunabhängige Eigennutzung (Cloud Deployment)

Um die App von jedem Gerät (Laptop, Smartphone, Tablet) aus nutzen zu können, ohne eine lokale Entwicklungsumgebung zu benötigen, wird die Applikation in einer containerisierten Cloud-Umgebung gehostet.

### Architektur-Erweiterung für Phase 1:
1. **State & Storage Agent**: Verwaltet hochgeladene Medien (Videos, Bilder) in einem Cloud Object Storage (z. B. AWS S3 oder Supabase Storage) und speichert den Status der Agenten-Workflows (z. B. "Script generiert", "Video gerendert", "Post ausstehend") in einer leichtgewichtigen Datenbank (PostgreSQL/Supabase).
2. **Web-Interface Agent**: Stellt eine Benutzeroberfläche (z. B. via Streamlit oder FastHTML) bereit, die über einen Webbrowser aufgerufen werden kann. Sie dient als Kontrollzentrum, um Prompts einzugeben, Skripte zu bearbeiten und hochgeladene Medien anzusehen.

### Infrastruktur-Stack für Phase 1:
- **Backend/Agenten-Laufzeit**: Containerisiert via Docker, gehostet auf **Render.com**, **Railway.app** oder **Hugging Face Spaces** (günstig, schnell aufgesetzt, unterstützt Python nativ).
- **Datenbank & Storage**: **Supabase** (kostenloses Kontingent für PostgreSQL und S3-kompatiblen Dateispeicher).
- **Sicherheit**: Basis-Authentifizierung (Username/Passwort) über das Web-Interface, um unbefugten Zugriff auf deine APIs zu verhindern.

---

## Phase 2: Öffentliche Bereitstellung (SaaS / Multi-Tenant Skalierung)

Um die Anwendung jedem als Produkt (Software-as-a-Service) zur Verfügung zu stellen, muss das System mandantenfähig (Multi-Tenant) werden. Jeder Nutzer benötigt isolierte Datenbereiche und eigene API-Verknüpfungen.

### Neue dedizierte Agenten für Phase 2:
1. **OAuth & Identity Agent**:
   - Verwaltet die Benutzerregistrierung und das Login (z. B. via Supabase Auth oder Clerk).
   - Übernimmt den sicheren OAuth2-Flow, damit *Kunden* ihre eigenen Social-Media-Accounts (YouTube, TikTok, LinkedIn, Instagram) per Klick autorisieren können, ohne ihre Passwörter preiszugeben.
   - Verschlüsselt und speichert die Access- und Refresh-Tokens der Kunden in der Datenbank.
2. **Tenant Isolation Agent**:
   - Stellt sicher, dass Agenten-Tasks strikt nach Benutzer-ID (User-ID) getrennt ausgeführt werden.
   - Verhindert Cross-Contamination (dass Daten von Nutzer A bei Nutzer B landen).
3. **Billing & Subscription Agent**:
   - Integriert einen Zahlungsabwickler (z. B. **Stripe**).
   - Überwacht das Kontingent (z. B. Anzahl der Video-Generierungen oder Uploads pro Monat) basierend auf dem gewählten Abonnement des Nutzers.
4. **Queue & Worker Agent**:
   - Da Videorendering (MoviePy/FFmpeg) und Agenten-Ketten rechenintensiv sind und asynchron laufen müssen, verwaltet dieser Agent eine Aufgaben-Warteschlange (z. B. mit **Celery** + **Redis** oder **Supabase Edge Functions**). Er verteilt die Last auf skalierbare Worker-Knoten.

---

## Zusammenfassung des Masterplans (Roadmap)

```
[ Phase 1: Eigenbedarf ]                      [ Phase 2: SaaS-Plattform ]
- Einzelner User-Kontext                      - Multi-Tenant Isolation
- Feste API-Keys in .env                      - Dynamischer OAuth2-Flow für User
- Einfaches Web-UI (Streamlit)                - Registrierung, Stripe-Billing
- Hosting auf Render/Railway                  - Skalierbare Worker-Queues (Celery)
```

---

# Antigravity Blueprint: Implementation Guide

Kopiere den folgenden Block und füge ihn direkt in Antigravity ein, um die Implementierung der Agenten-Strukturen und des Deployments zu starten.

```text
================================================================================
ANTIGRAVITY SYSTEM INSTRUCTIONS: CLOUD DEPLOYMENT & MULTI-TENANCY EXPANSION
================================================================================

OBJECTIVE:
Transform the core Ssemble-like Social Media Automation Agent into a production-ready, cloud-hosted application (Phase 1) and extend its architecture into a multi-tenant SaaS platform (Phase 2).

--------------------------------------------------------------------------------
STEP 1: ARCHITECTURE DEFINITION FOR PHASE 1 (Cloud Deployment)
--------------------------------------------------------------------------------
Define and implement the following agents inside the Antigravity workspace:

1. WebInterfaceAgent:
   - Framework: Streamlit or FastHTML (Python-native).
   - Input: Text prompts, video scripts, raw media files via browser upload.
   - Output: Visual dashboard tracking agent status, script previews, approval buttons.
   - Security: Implement a secure login mechanism (session-based) to restrict access to the owner.

2. StateStorageAgent:
   - Database: Connect to a remote PostgreSQL database (Supabase).
   - Storage: Integrate S3-compatible storage (Supabase Storage) for keeping track of raw assets, generated audio, and final rendered MP4 files.
   - Schema: Design tables for `posts`, `assets`, `agent_logs`, and `api_configurations`.

--------------------------------------------------------------------------------
STEP 2: ARCHITECTURE DEFINITION FOR PHASE 2 (Multi-Tenant SaaS Scaling)
--------------------------------------------------------------------------------
Generate the blueprint and programmatic logic for the following Enterprise/SaaS agents:

1. OAuthIdentityAgent:
   - Handle OAuth2 redirection and callback handling for LinkedIn, YouTube (Google OAuth), TikTok, and Meta Graph API.
   - Securely encrypt user tokens (AES-256) before passing them to the StateStorageAgent.
   - Automatically handle Token Refresh logic natively via Python requests when a publishing task is triggered.

2. TenantIsolationAgent:
   - Inject `user_id` context into every agent execution step.
   - Validate that the executing agent cannot access assets, scripts, or API tokens belonging to another `user_id`.

3. QueueWorkerAgent:
   - Implement an asynchronous task queue wrapper (e.g., Celery/Redis architecture simulated in Python).
   - Ensure heavy media tasks (video rendering via MoviePy/FFmpeg, text-to-speech generation) run in background threads without blocking the WebInterfaceAgent.

4. BillingSubscriptionAgent:
   - Integrate Stripe webhook listeners.
   - Create a metering system that counts the number of videos processed per `user_id` and blocks execution if the tier limit is reached.

--------------------------------------------------------------------------------
STEP 3: DEPLOYMENT CONFIGURATION GENERATION
--------------------------------------------------------------------------------
Provide the complete setup files required for running the application anywhere:
1. Dockerfile: Multi-stage build optimized for Python, including FFmpeg installation (required for moviepy video processing).
2. docker-compose.yml: Local development environment connecting the App, Redis (Queue), and PostgreSQL.
3. Render.com / Railway.app Blueprint: A configuration file (render.yaml or railway.json) defining the web service, background worker, and environment variable requirements.

EXECUTION INSTRUCTION:
Generate the comprehensive Python class architecture for these agents, ensure clean separation of concerns, and provide the complete configuration files listed in Step 3.
================================================================================
```
