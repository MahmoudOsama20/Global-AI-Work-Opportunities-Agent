# Global AI Opportunities Intelligence Agent — Architecture

## 1. System Vision & Architecture Overview

The **Global AI Opportunities Intelligence Agent** is a manually triggered, production-quality intelligence platform designed to discover, collect, validate, classify, verify, deduplicate, score, and report legitimate paid work opportunities in Artificial Intelligence for a Senior AI & ML Engineer based in Egypt.

### Core Philosophy
1. **Manual Trigger Only**: The platform executes on-demand (`python main.py --run` or clicking "RUN GLOBAL AI OPPORTUNITY SEARCH" in the dashboard). There are no background daemons, cron jobs, or unscheduled polling.
2. **Strict Exclusions**: Speech/Audio tasks (ASR, TTS, Voice AI, transcription, audio annotation) and non-AI generic automation (RPA, PLC, SCADA, generic BPA) are strictly filtered before ranking.
3. **Egyptian Eligibility Gating**: Opportunities are rigorously evaluated for Egyptian legal and payout eligibility (Payoneer, Wise, Wire/IBAN, PayPal). Ineligible opportunities are prevented from appearing as recommended applications.
4. **Resilient Connector Pipeline**: Individual connector failures never abort the overall search. Every source returns raw telemetry and normalized records independently.
5. **Dynamic Source Discovery**: Continuous web-based discovery finds new platforms and hiring boards, automatically validates legitimacy and country support, and queues them in a Discovery Registry for human review and inclusion.
6. **Safe Authenticated Inspection**: No automated credential capture or CAPTCHA bypass. For platforms like Outlier with account-specific availability, the platform utilizes local user-controlled Playwright browser profiles where the user logs in manually, and the agent only reads authorized project dashboards.

```
+---------------------------------------------------------------------------------------------------+
|                                 USER INTERFACE / CLI LAYER                                        |
|  - Modern React + TypeScript + Tailwind CSS Dashboard                                             |
|  - CLI Interface (python main.py --run, --source, --category, --health-check, --discover-sources) |
+-------------------------------------------------+-------------------------------------------------+
                                                  |
                                                  v
+-------------------------------------------------+-------------------------------------------------+
|                                    FASTAPI BACKEND SERVICE                                        |
|  - REST Endpoints (/api/pipeline, /api/opportunities, /api/sources, /api/discovery, /api/reports) |
|  - Real-time Pipeline Progress SSE / WebSockets                                                   |
+-------------------------------------------------+-------------------------------------------------+
                                                  |
                                                  v
+-------------------------------------------------+-------------------------------------------------+
|                                 CENTRAL INTELLIGENCE PIPELINE                                     |
|                                                                                                   |
|  Stage 1: Collection       --> Concurrent source execution (APIs, Feeds, Web, Browser Session)    |
|  Stage 2: Normalization    --> Map source data to Universal Opportunity Model                     |
|  Stage 3: Validation       --> Check URLs, paid status, AI relevance, expiration                 |
|  Stage 4: Classification   --> Map to 7 AI Domains (LLM, CV, NLP, Agents, DL/ML, MLOps, Eval)     |
|  Stage 5: Exclusion Filter --> Purge Speech/Audio & RPA/SCADA/BPA                                 |
|  Stage 6: Eligibility Gate --> Verify Egypt legal & payout compatibility (Payoneer, Wise, etc.)  |
|  Stage 7: Deduplication    --> Multi-strategy (Canonical URL, Title, Company, Cosine/Fuzzy)      |
|  Stage 8: AI Matching      --> 100-Point Deterministic Model + LLM Analysis Abstraction          |
|  Stage 9: Ranking & Gate   --> Assign category (Excellent, Strong, etc.), apply Egypt gate       |
|  Stage 10: Reporting       --> Generate comprehensive HTML & Markdown reports with evidence       |
+-------------------------------------------------+-------------------------------------------------+
             |                                    |                                    |
             v                                    v                                    v
+---------------------------+   +-------------------------------+   +-------------------------------+
|     CONNECTOR REGISTRY    |   |    SOURCE DISCOVERY ENGINE    |   |     PERSISTENCE & STORAGE     |
| - BaseConnector ABC       |   | - Web Search Providers        |   | - SQLite (aiosqlite)          |
| - Freelance Connectors    |   | - Query Generator             |   | - SQLAlchemy 2.0 Async        |
| - Evaluation Connectors   |   | - Source Validator            |   | - Alembic Migrations          |
| - Annotation Connectors   |   | - Candidate Registry          |   | - Historical Audit Logs       |
| - Outlier (Public+Auth)   |   | - Status Lifecycle Tracking   |   | - PostgreSQL Compatible       |
+---------------------------+   +-------------------------------+   +-------------------------------+
```

---

## 2. Source Discovery Engine Architecture

The Source Discovery Engine does not rely on an uncontrolled crawler. Instead, it operates through a deterministic 4-stage pipeline:

1. **Profile-Driven Query Generation**:
   Generates targeted search queries based on the user's active domains and Egyptian location (e.g., `"remote LLM evaluation contractor Egypt"`, `"computer vision freelance projects paid"`, `"AI red teaming platform hiring worldwide"`).
2. **Multi-Provider Web Search Abstraction**:
   Integrates pluggable search engines (DuckDuckGo HTML/API, SearXNG, Serper, Google Custom Search, or fallback web queries) to identify candidate URLs.
3. **Automated Source Legitimacy Validation**:
   Inspects each candidate URL:
   - Validates domain registration and accessibility via HTTP HEAD/GET.
   - Parses security headers, SSL certificate, official career or vendor page indicators.
   - Evaluates country eligibility policies and payment method disclosures.
   - Detects scam indicators (requests for upfront fees, fake checks, suspicious contact channels).
4. **Registry Lifecycle Management**:
   Categorizes each source into one of 6 states:
   - `candidate`: Discovered via search, waiting for evaluation.
   - `verified`: Meets legitimacy criteria, offers paid AI work, tested collection mechanism.
   - `unverified`: Insufficient public data on payout or company identity.
   - `restricted`: Legitimate, but requires client API credentials or special approval (e.g., Upwork API).
   - `broken`: Target endpoint inaccessible or changed structure.
   - `deprecated`: Platform shut down or no longer offering relevant AI roles.
   New sources are presented in the **Discovery Center** for user review and approval before inclusion in active collection runs.

---

## 3. Safe Authenticated Sources Architecture

Platforms like Outlier, Alignerr, and Appen frequently have private worker dashboards displaying real-time task allocations distinct from public career pages. The application handles these safely without violating credentials, terms, or security:

1. **User-Controlled Local Browser Profiles**:
   Uses Playwright with a persistent directory (`data/browser_profiles/<platform>`).
2. **Zero Credential Ingestion**:
   The agent **never** prompts for, accepts, or stores passwords, MFA tokens, or secrets.
3. **Interactive Login Workflow**:
   When inspection is requested (`python main.py --inspect-account outlier`):
   - A real browser window opens to the official login URL.
   - The user completes login, 2FA, and CAPTCHA manually.
   - The persistent cookies and session tokens remain securely on the user's local disk inside the user data directory.
4. **Read-Only Telemetry Extraction**:
   The connector launches Playwright attached to that persistent context in read-only mode to extract:
   - Current project queue / allocation name.
   - Stated pay rate and project requirements.
   - Country and account verification notices.
5. **No Autonomous Actions**:
   The agent **never** clicks "Submit Application", accepts contracts, or sends messages.
   If the session has expired or authentication fails, the agent reports `"Unable to verify — authentication required"` without fabricating data.

---

## 4. Hardware and Performance Optimization

- **Zero GPU / CUDA Dependency**: CPU-only algorithms for text matching, fuzzy similarity (RapidFuzz/thefuzz), and tokenization.
- **Lightweight Dependencies**: Fast parsing with `selectolax` / `beautifulsoup4`, asynchronous networking with `httpx`, minimal memory footprint.
- **Controlled Storage**: Virtual environment, browser caches, and SQLite database fit well within available disk headroom (<1 GB total).
