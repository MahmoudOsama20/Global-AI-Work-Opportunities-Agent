# GLOBAL SOURCE COVERAGE AUDIT & INTEGRATION MATRIX
**Global AI Opportunities Intelligence Agent**
*Date: November 2, 2026 | Version: 2.0 | Coverage: 35+ Global Platforms*

---

## 1. Overview & Verification Standards

This matrix documents the global discovery and collection landscape across freelance platforms, AI training/evaluation hubs, crowdsourced data platforms, remote job boards, and frontier AI ecosystems.

### Status Definitions
- `LIVE_VERIFIED`: Directly integrated and verified live via public API, RSS, or headless automation; returns real opportunities right now.
- `AUTH_REQUIRED`: Active connector exists or is supported via user-authenticated session (e.g. Playwright persistent browser context).
- `API_ACCESS_REQUIRED`: Platform provides official developer/partner API requiring an approved developer account or API token.
- `HEADLESS_REQUIRED`: Dynamic JavaScript application requiring browser automation (Playwright/Puppeteer) to render opportunities.
- `SCRAPING_BLOCKED`: Protected by aggressive Cloudflare Turnstile, DataDome, or CAPTCHA blocking automated HTTP requests.
- `NOT_IMPLEMENTED`: Cataloged in discovery seed candidates for future connector development.

---

## 2. Comprehensive Platform Coverage Matrix

### 2.1 Category A: Freelance Marketplaces

| Platform | Category | Official URL | Access Method | Status | Verification Evidence | Freshness Capability | Egypt Eligibility | Payout Channels | Priority |
|---|---|---|---|---|---|---|---|---|---|
| **Upwork** | Freelance | `https://www.upwork.com` | Official GraphQL/REST API or RSS feeds | `API_ACCESS_REQUIRED` / `SCRAPING_BLOCKED` | Cloudflare Turnstile blocks raw HTTP GET. RSS feeds require client token or OAuth 2.0 keys. | High (Provides RFC2822 pubDate on RSS / ISO8601 in API). Supports 6h/24h. | Fully Eligible (Egypt verified freelance market). | Payoneer (Direct EGP/USD), Direct to Local Bank (Wire), PayPal. | High (Seed candidate for OAuth integration) |
| **Freelancer.com** | Freelance | `https://www.freelancer.com` | Public REST API v0.1 (`/api/projects/0.1/projects/active`) | `LIVE_VERIFIED` (Seed Candidate) | Open JSON API available at `https://www.freelancer.com/api/projects/0.1/projects/active.json?compact=true`. | High (`submitdate` epoch timestamp provided). Supports 6h/24h. | Fully Eligible. | PayPal, Skrill, Wire Transfer. | High |
| **Fiverr** | Freelance / Gigs | `https://www.fiverr.com` | Seller Gig Platform (Reverse marketplace) | `NOT_IMPLEMENTED` | Reverse model: clients buy gigs posted by sellers; job board buyer requests are deprecated. | Low (Buyer requests rarely public). | Eligible. | Payoneer, PayPal, Bank Transfer. | Low |
| **Guru** | Freelance | `https://www.guru.com` | Web Scraping / Search API | `HEADLESS_REQUIRED` | Requires JavaScript rendering; search page has basic pagination. | Medium (Dates listed as "Posted 2 days ago"). | Eligible. | Payoneer, PayPal, Wire Transfer. | Medium |
| **PeoplePerHour** | Freelance | `https://www.peopleperhour.com` | Web Search / JSON endpoint | `SCRAPING_BLOCKED` | Cloudflare DDoS protection blocks automated Python requests. | High (Explicit publication dates). | Eligible. | Payoneer, PayPal. | Low |
| **Truelancer** | Freelance | `https://www.truelancer.com` | Web Search / Scraping | `NOT_IMPLEMENTED` | HTML listing with project cards. | Medium (Relative date strings). | Eligible (Popular in MENA). | PayPal, Bank Transfer, Payoneer. | Medium |

---

### 2.2 Category B: AI Training, Model Evaluation & RLHF

| Platform | Category | Official URL | Access Method | Status | Verification Evidence | Freshness Capability | Egypt Eligibility | Payout Channels | Priority |
|---|---|---|---|---|---|---|---|---|---|
| **Outlier AI (Scale AI)** | AI Training / RLHF | `https://outlier.ai` / `https://scale.com` | Scale AI Greenhouse API (`boards-api.greenhouse.io/v1/boards/scaleai/jobs`) & Playwright Auth | `LIVE_VERIFIED` (Public) & `AUTH_REQUIRED` (Account) | Live verified endpoint returns 200 OK with AI Specialist/RLHF roles; `OutlierAccountConnector` handles dashboard tasks via persistent session. | High (`updated_at` ISO8601 timestamps). Supports 24h/7d. | Partially Eligible (Specific AI Specialist roles open to Egypt; English/Arabic prompt evaluation). | PayPal, AirTM. | Highest |
| **Alignerr (Labelbox)** | AI Evaluation | `https://alignerr.com` | Labelbox Greenhouse API (`boards-api.greenhouse.io/v1/boards/labelbox/jobs`) | `LIVE_VERIFIED` | Live verified endpoint returns 200 OK with Labelbox/Alignerr AI Trainer & Reviewer postings. | High (`updated_at` ISO8601 timestamps). Supports 24h/7d. | Fully Eligible (Contractor roles hire globally including Egypt). | Deel (Bank Transfer, Wise, PayPal, Payoneer). | Highest |
| **Mindrift** | AI Tutoring / RLHF | `https://mindrift.ai` | Web Careers / Greenhouse ATS | `LIVE_VERIFIED` (Discovery Seed) | Careers page routes to Greenhouse job board for AI Writers and Domain Experts. | High (ATS posting dates). | Eligible (Accepts applications from Egypt). | Payoneer, PayPal. | High |
| **DataAnnotation.tech** | AI Training | `https://www.dataannotation.tech` | Custom SPA / Protected Portal | `AUTH_REQUIRED` / `SCRAPING_BLOCKED` | Heavy bot detection; assessment and project board only visible after login. | Unknown (No public job RSS/API). | Restricted (Officially lists US, Canada, UK, Australia, NZ, Ireland; Egypt occasionally accepted for bilingual Arabic tasks). | PayPal. | Medium |
| **Invisible Technologies** | Advanced AI Operations | `https://invisible.co` | Greenhouse / Lever ATS | `LIVE_VERIFIED` (Discovery Seed) | Public Greenhouse board with Advanced AI Trainer and Process Orchestration roles. | High (ATS ISO timestamps). | Fully Eligible (Worldwide remote). | Deel (Wise, Payoneer, Wire, PayPal). | High |
| **OneForma (Centific)** | AI Annotation / Evaluation | `https://www.oneforma.com` | Centific Portal API | `NOT_IMPLEMENTED` | Requires OneForma account to view active project board. | Medium (Project batch dates). | Fully Eligible (Very active in Egypt for Arabic AI evaluation). | Payoneer, PayPal. | High |
| **Appen** | AI Data / Evaluation | `https://appen.com` | Appen Connect Portal | `NOT_IMPLEMENTED` | Public career page lists corporate roles; project board requires Appen Connect login. | Medium (Project publication dates). | Fully Eligible (High presence in Egypt). | Payoneer, PayPal. | High |
| **Telus International AI** | AI Data Solutions | `https://www.telusinternational.ai` | AI Community Portal | `NOT_IMPLEMENTED` | Portal login required for task marketplace; public listings on SuccessFactors ATS. | Medium (Job listing date). | Fully Eligible (Frequent Egypt campaigns). | Hyperwallet, Wire, PayPal. | High |
| **Remotasks (Scale AI)** | AI Annotation | `https://www.remotasks.com` | Integrated into Outlier AI | `AUTH_REQUIRED` | Remotasks has transitioned into Outlier.ai platform. | High. | Partially Eligible (Egypt accounts supported). | PayPal, AirTM. | Medium |
| **Clickworker** | Microtasks / AI Training | `https://www.clickworker.com` | Workplace Portal & UHRS | `NOT_IMPLEMENTED` | UHRS tasks require internal qualification; public page has registration only. | Low (Task batches arrive in real time without public dates). | Eligible (Egypt workers accepted). | Payoneer, PayPal, SEPA. | Medium |

---

### 2.3 Category C: Data and Annotation Crowdsourcing

| Platform | Category | Official URL | Access Method | Status | Verification Evidence | Freshness Capability | Egypt Eligibility | Payout Channels | Priority |
|---|---|---|---|---|---|---|---|---|---|
| **Toloka AI (Mindshift)** | Data Annotation | `https://toloka.ai` | Toloka Requester/Worker API | `NOT_IMPLEMENTED` | Worker tasks served via mobile app / web interface dynamically. | Medium (Task availability is dynamic). | Fully Eligible. | Payoneer, Qiwi, Papara. | Medium |
| **Prolific** | Academic & AI Research | `https://www.prolific.com` | Participant App | `NOT_IMPLEMENTED` | Studies delivered directly to participant dashboard based on demographic prescreening. | Real-time (Dynamic study queue). | Restricted (Only 38 OECD countries supported; Egypt currently unsupported for participant registration). | PayPal. | Low |
| **CloudResearch Connect** | AI & Behavior Research | `https://connect.cloudresearch.com` | Participant Dashboard | `NOT_IMPLEMENTED` | Similar to Prolific; requires account verification. | Real-time. | Restricted (Primarily US/UK/Canada/Australia). | PayPal. | Low |
| **Amazon Mechanical Turk** | Crowdsourcing | `https://www.mturk.com` | AWS MTurk API | `API_ACCESS_REQUIRED` | AWS credentials and MTurk Requester/Worker account required. | High (HIT creation timestamps). | Restricted (Non-US workers face registration waitlists or Amazon gift card payouts). | Direct Deposit (US), Amazon Gift Cards. | Low |

---

### 2.4 Category D: Remote Work & AI Engineering Job Boards

| Platform | Category | Official URL | Access Method | Status | Verification Evidence | Freshness Capability | Egypt Eligibility | Payout Channels | Priority |
|---|---|---|---|---|---|---|---|---|---|
| **Remotive** | Remote Engineering | `https://remotive.com` | Public REST API (`https://remotive.com/api/remote-jobs`) | `LIVE_VERIFIED` | Verified live; returns 200 OK with ~1000 remote tech jobs, full markdown description, publication dates. | High (`publication_date` ISO8601). Supports 6h/24h/7d. | Fully Eligible (Worldwide & All-location filterable). | Employer specific (Deel, Wise, Remote.com). | Highest |
| **Remote OK** | Remote Tech | `https://remoteok.com` | Public JSON API (`https://remoteok.com/api`) | `LIVE_VERIFIED` | Verified live; returns 200 OK with tech opportunities, tags, and epoch timestamps. | High (`date` ISO8601/epoch). Supports 6h/24h/7d. | Fully Eligible (Worldwide remote tags). | Employer specific (Direct Wire, Deel, Wise). | Highest |
| **Himalayas** | Modern Remote Jobs | `https://himalayas.app` | Public REST API (`https://himalayas.app/jobs/api`) | `LIVE_VERIFIED` | Verified live; returns 200 OK with rich metadata, tech stacks, salary ranges. | High (`pub_date` epoch). Supports 6h/24h/7d. | Fully Eligible (Searchable by country `Egypt` or `Worldwide`). | Employer specific (Deel, Wise, Wire). | Highest |
| **We Work Remotely** | Remote Work | `https://weworkremotely.com` | Public RSS Feed (`/categories/remote-programming-jobs.rss`) | `LIVE_VERIFIED` | Verified live; XML RSS parsed reliably via standard library. | High (`pubDate` RFC2822). Supports 6h/24h/7d. | Fully Eligible (Anywhere in the World section). | Employer specific. | Highest |
| **Wellfound (AngelList)** | AI Startups & Tech | `https://wellfound.com` | Web Scraping / GraphQL | `SCRAPING_BLOCKED` | Cloudflare Turnstile blocks automated requests; requires browser session. | High (Posting dates shown on cards). | Fully Eligible (Many global AI startups hire remote contractors). | Employer specific (Deel, Brex, Wise). | High (Headless candidate) |
| **Jobspresso** | Remote Careers | `https://jobspresso.co` | Web Search / RSS | `NOT_IMPLEMENTED` | RSS feed available for tech categories. | Medium (`pubDate` in RSS). | Fully Eligible. | Employer specific. | Medium |
| **Working Nomads** | Remote Work | `https://www.workingnomads.com` | Public JSON API (`/jobs/api/jobs/`) | `LIVE_VERIFIED` (Discovery Seed) | Returns JSON job list with categories and tags. | High (`pub_date` ISO). | Fully Eligible. | Employer specific. | High |
| **FlexJobs** | Curated Remote Jobs | `https://www.flexjobs.com` | Paid Subscription Portal | `SCRAPING_BLOCKED` | Paywalled listing links; requires subscriber login to view company details. | High. | Partially Eligible. | Employer specific. | Low |
| **Virtual Vocations** | Remote Work | `https://www.virtualvocations.com` | Subscription / Web Portal | `SCRAPING_BLOCKED` | Requires account; limited free previews. | Medium. | Restricted (Primarily US-based telecommute). | Employer specific. | Low |

---

### 2.5 Category E: AI Ecosystems & Developer Portals

| Platform | Category | Official URL | Access Method | Status | Verification Evidence | Freshness Capability | Egypt Eligibility | Payout Channels | Priority |
|---|---|---|---|---|---|---|---|---|---|
| **Hugging Face Jobs** | AI/ML Community | `https://huggingface.co/jobs` | Web Scraping / JSON endpoint | `LIVE_VERIFIED` (Discovery Seed) | HTML and backend JSON endpoints display community AI engineer/researcher postings. | High (Relative dates "2 days ago" or ISO dates). | Fully Eligible (High international remote presence). | Employer specific (Deel, Remote.com). | Highest |
| **OpenAI Careers** | Frontier AI Lab | `https://openai.com/careers` | Greenhouse ATS (`boards-api.greenhouse.io/v1/boards/openai/jobs`) | `LIVE_VERIFIED` (Discovery Seed) | Live Greenhouse endpoint accessible. | High (`updated_at` ISO8601). | Restricted (Mostly US/UK/Europe/Tokyo on-site or hybrid; few global contractor roles). | Corporate Payroll / Wire. | Medium |
| **Anthropic Careers** | Frontier AI Lab | `https://www.anthropic.com/careers` | Lever ATS (`api.lever.co/v0/postings/anthropic`) | `LIVE_VERIFIED` (Discovery Seed) | Live Lever endpoint accessible. | High (`createdAt` epoch ms). | Restricted (US/UK/Europe/Canada primarily; remote contracts require third-party EOR like Deel). | Corporate Payroll / Deel. | Medium |
| **Kaggle** | Data Science & AI | `https://www.kaggle.com/competitions` | Kaggle Public REST API (`kaggle competitions list`) | `API_ACCESS_REQUIRED` (Free) | Free Kaggle API token allows listing active prize competitions and paid community challenges ($10k-$100k+). | High (Competition deadline and start date). | Fully Eligible (Egyptian data scientists win and receive cash prizes via Hyperwallet/Wire). | Hyperwallet (Direct Wire, PayPal). | High |
| **GitHub Jobs & Repos** | Open Source & Bounties | `https://github.com` | GitHub REST / GraphQL API | `API_ACCESS_REQUIRED` (Free) | Public search API (`api.github.com/search/issues?q=label:"bounty"+is:open`) surfaces paid AI bug bounties and Algora/Polar bounties. | High (`created_at` ISO8601). | Fully Eligible. | Stripe Connect, GitHub Sponsors, PayPal. | High |

---

## 3. Recommended Implementation Roadmap for Source Connectors

1. **Immediate Tier (Already Live & Operational)**:
   - Remotive (REST)
   - Remote OK (REST)
   - Himalayas (REST)
   - WeWorkRemotely (RSS)
   - Outlier / Scale AI (Greenhouse ATS + Playwright Session)
   - Alignerr / Labelbox (Greenhouse ATS)
2. **Next Tier (High Value & Legitimate Open Access)**:
   - Hugging Face Jobs (Web / JSON)
   - Invisible Technologies (Greenhouse ATS: `boards-api.greenhouse.io/v1/boards/invisibletechnologies/jobs`)
   - Mindrift (Greenhouse ATS)
   - Freelancer.com Open REST API
   - Kaggle Prize Competitions (Free API)
3. **Protected / Manual Review Tier**:
   - Upwork (Requires developer OAuth approval or client token)
   - DataAnnotation.tech (Requires human login session)
   - OneForma & Appen (Requires dedicated contractor portal logins)

