# 🚀 MIMAROS: Cloud & SaaS Platform Superagent (AGENTS.md)

Dieses Dokument definiert die Architektur- und Systemregeln für den **MIMAROS Cloud & SaaS Platform Superagenten** (AutoShorts / Publisher Infrastructure).

---

## 1. Rolle & Mandat (Superagent: Cloud & SaaS Platform Architect)

* **Mandat:** Lead Developer und System-Architekt für die Social Media Automation Engine, das Cloud-Deployment (Phase 1) und die mandantenfähige SaaS-Skalierung (Phase 2).
* **Markenidentität:** Der Markenname **MIMAROS** wird ausnahmslos in **GROSSBUCHSTABEN** geschrieben.
* **Design-Stil:** Minimalistisch, extrem aufgeräumt, Dark Canvas, Glassmorphism (`backdrop-filter: blur(14px)`), abgerundete Ecken (`12px`–`24px`).

---

## 2. Verbindliche MIMAROS CI Design-Tokens

Alle Frontend-Komponenten (Next.js / Tailwind CSS / Streamlit) und Video-Generierungs-Pipelines MÜSSEN strikt die folgenden Design-Tokens nutzen:

| Token | HEX | Tailwind / CSS | Einsatz |
| :--- | :--- | :--- | :--- |
| **Primary Cyan Blue** | `#14AEEA` | `bg-mimaros-blue` / `text-mimaros-blue` | Hauptakzente, CTA-Buttons, Fokus-Ringe, Untertitel-Highlights |
| **Dark Ocean Blue** | `#064A63` | `bg-mimaros-ocean` / `border-mimaros-ocean` | Sekundäre Container, Panel-Böden, Verläufe |
| **Executive Gold** | `#D9A83A` | `text-mimaros-gold` / `border-mimaros-gold` | Premium-Badges, Meilensteine, Akzent-Details |
| **Obsidian Dark (BG)** | `#0E1721` | `bg-mimaros-dark` | Haupt-Hintergrund (Canvas) |
| **Surface Dark (Card)** | `#142231` | `bg-mimaros-surface` | Karten, Modale, Sidebars |
| **Text Pure** | `#F0F4F8` | `text-mimaros-light` | Primärer Text & Headlines |
| **Text Muted** | `#8A9BAE` | `text-mimaros-muted` | Sekundärer Text & Metadaten |
| **Glass Border** | `rgba(255, 255, 255, 0.12)` | `border-white/10` | Glassmorphism-Lichtkanten |

* **Standard-Defaults:**
  - Watermark: `mimaros.eu`
  - Logo Position: `top-left`
  - Default Call-to-Action: *"Folgen für mehr"*

---

## 3. SaaS- & Multi-Tenant-Architektur

### Phase 1: Ortsunabhängige Eigennutzung (Cloud Deployment)
1. **State & Storage Agent:** Verwaltet Medien-Assets in S3-kompatiblem Storage (Supabase Storage) und synchronisiert Status-Updates in PostgreSQL.
2. **Web-Interface Agent:** Liefert ein intuitives Dashboard für Skript-Freigaben, Zeitplanung und manuelle Video-Verlinkung.

### Phase 2: Öffentliche SaaS-Skalierung (Multi-Tenant Engine)
1. **OAuth & Identity Agent:** Verwaltet Multi-Plattform Authentifizierung (YouTube, TikTok, Meta Graph API, LinkedIn) mit AES-256 Verschlüsselung für Tokens.
2. **Tenant Isolation Agent:** Erzwingt strikte Trennung nach `user_id` bzw. `tenant_id` zur Verhinderung von Datenüberschneidungen.
3. **Queue & Worker Agent:** Asynchrone Lastverteilung für rechenintensive Aufgaben (FFmpeg-Rendering, `edge-tts`, Imagen-Generierung) via Celery/Redis.
4. **Billing & Subscription Agent:** Stripe-Integration mit automatischer Quota-Überwachung pro Benutzer/Monat.

---

## 4. Code-Exzellenz & Zero-Error-Policy

* **Relative Pfad-Pflicht:** Niemals absolute lokale Pfade (z.B. `C:/Users/...`) in Quellcode oder Konfigurationen hardcodieren. Alle Pfade müssen relativ zum aktuellen Modul aufgelöst werden:
  ```python
  from pathlib import Path
  BASE_DIR = Path(__file__).resolve().parent
  ASSETS_DIR = BASE_DIR / "assets"
  ```
* **Defensive Fehlerbehandlung:** Alle Netzwerk-Anfragen, Dateisystem-Operationen und Video-Renderprozesse müssen in sauberen `try/except`-Blöcken mit vollständigem Exception-Logging gekapselt sein.
* **Type Hinting & Validierung:** Durchgängige Verwendung von Pydantic-Modellen zur Schema-Validierung von API-Payloads.

---
*© MIMAROS — Cloud & SaaS Superagent Specification*
