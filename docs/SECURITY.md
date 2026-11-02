# Security, Privacy & Compliance Guidelines

## 1. Zero-Credential Architecture
- **No Password Ingestion**: The system strictly prohibits prompting for, accepting, storing, or handling user passwords, tokens, or private secrets in source code, configurations, database, or memory.
- **Environment Isolation**: All external API keys (LLM providers, search APIs) are sourced via `.env` loaded into memory at startup. `.env` is permanently excluded via `.gitignore`.
- **API Response Sanitization**: FastAPI response schemas and logging interceptors strictly strip authorization headers, API keys, and sensitive tokens.

---

## 2. Safe Authenticated Platform Access (Outlier, Alignerr, Appen, etc.)
- **Interactive User Authentication**:
  When account-specific verification is requested, Playwright launches with a local persistent context:
  `data/browser_profiles/<platform>`
  The browser window is displayed to the user so they can manually log in, satisfy Multi-Factor Authentication (MFA), and complete any verification challenges.
- **No CAPTCHA / Bot Defense Bypass**:
  The system will never attempt to circumvent Cloudflare, reCAPTCHA, hCaptcha, or platform security defenses.
- **Strict Read-Only Operations**:
  The system functions exclusively as an intelligence and discovery engine. The agent will **NEVER**:
  - Automatically submit a job application or proposal.
  - Send messages or communication to clients or platform managers.
  - Accept contracts, terms, or task assignments.
  - Purchase services or initiate financial transactions.
- **Graceful Failure**:
  If an authenticated session has expired, the connector logs `"Authentication required — please log in via CLI interactive mode"` and returns an `unverified` status without halting the pipeline.

---

## 3. Scraping & Network Compliance
- **Terms & Rate Limiting**: All outbound requests use standard polite user-agent strings and enforced rate limits with exponential backoff.
- **Public & Official Endpoints**: Prioritize official APIs (Remotive, Himalayas, Remote OK) and public RSS/career feeds (Greenhouse, Lever, public boards).
- **No Proxy Rotation for Evasion**: The system avoids shady proxy rotating services or evasion techniques.

---

## 4. Scam and Threat Detection
Discovered listings are scanned for fraud signals before inclusion:
- Advance fee fraud (asking applicant to send money for equipment or checks).
- Off-platform communication redirection (e.g., "message this Telegram username immediately for interview").
- Unverified external redirects or phishing domains.
Listing risk status is flagged (`low`, `review`, `high`, `scam`) with explanatory evidence so the user is never misled.

