# PRODUCTION AUDIT & SYSTEM ARCHITECTURAL ASSESSMENT
**Global AI Opportunities Intelligence Agent**
*Date: November 2, 2026 | Version: 2.0 Upgrade Audit | Status: Production Hardening*

---

## 1. Executive Summary & Audit Context

The **Global AI Opportunities Intelligence Agent** is a manually triggered, local intelligence platform designed to discover, normalize, classify, gate, match, and rank global paid work opportunities for an AI Engineer based in Egypt.

This audit evaluates the system following its Phase 0–5 baseline completion (commit `71cbd6f`) and defines the architecture for the two major new systems mandated by the Master Upgrade Directive:
1. **Advanced Opportunity Freshness Intelligence Engine** (Rolling windows from 6 hours to 30 days, strict original publication timestamp verification).
2. **Deep CV Intelligence & Personalized Opportunity Matching Engine** (Structured PDF/DOCX multi-page CV extraction, project-level evidence attribution, transferable skill graph, and strict seniority compatibility gating).

---

## 2. Current Implementation State

### 2.1 Component Assessment Matrix

| Subsystem | Existing Implementation Status | Strengths | Gaps & Deficiencies Identified | Upgrade Action |
|---|---|---|---|---|
| **Data Layer & Persistence** | Synchronous SQLAlchemy 2.0 with SQLite (`opportunities.db`), repository pattern (`OpportunityRepository`, `SourceRepository`, `RunRepository`). | Microsecond latency, zero thread lock contention under Windows, clean separation of repositories. | Schema lacks explicit publication timestamp separation (`posted_at`, `updated_at`, `collected_at`); no dedicated `CVProfileModel` for storing structured parsed resumes. | Add `posted_at`, `updated_at`, `collected_at`, `freshness_status`, `freshness_score` to `opportunities`. Add `CVProfileModel` with project evidence storage and versioning. |
| **Source Connectors** | 7 active connectors in `backend/app/connectors/`: `RemotiveConnector`, `RemoteOKConnector`, `HimalayasConnector`, `WeWorkRemotelyConnector`, `OutlierPublicConnector`, `AlignerrPublicConnector`, `OutlierAccountConnector`. | ThreadPool parallel collection, robust error isolation (individual connector failure never halts run), verified live ATS endpoints for Scale AI/Outlier and Labelbox/Alignerr. | Connectors populate `first_seen_at` upon scraping instead of extracting true source publication dates (`posted_at`). Some platforms lack relative date parsing. | Enhance all connectors to extract and normalize true publication timestamps into UTC. Map missing timestamps to `UNKNOWN_DATE` status. |
| **Exclusion & Filtering Engine** | Rule-based regex engine in `backend/app/intelligence/exclusions.py` driven by `config/exclusions.yaml`. | 100% negative test coverage purging Speech/Audio (ASR, TTS, transcription, voice actor) and generic Non-AI Automation (RPA, PLC, Zapier, UiPath). | None. Performs deterministically with zero false negatives on prohibited domains. | Maintain zero tolerance for speech/audio and generic RPA. |
| **Domain Classification** | 7 technical AI domains classified with keyword and regex pattern matching in `backend/app/intelligence/classifier.py`. | Highly accurate multi-label assignment across LLMs, Computer Vision, NLP, AI Agents, Deep Learning, MLOps, and AI Training/Evaluation. | Does not yet link classified domains to project-proven skills from uploaded CV. | Integrate CV project evidence into domain relevance scoring. |
| **Geographic Eligibility** | Egypt eligibility evaluator in `backend/app/intelligence/eligibility.py`. | Strict detection of worldwide eligibility, Egypt explicit whitelist, and US/EU-only geofencing with risk scoring. | Currently binary (eligible vs ineligible); lacks awareness of payout channel viability for Egypt (Payoneer, Wise, SWIFT). | Add payout channel feasibility checking to eligibility analysis. |
| **Deduplication Engine** | Hybrid deduplicator in `backend/app/intelligence/deduplicator.py` using canonical URLs, content hash, and fuzzy title+company matching. | Resilient against cross-source duplicates and re-indexed URLs. | Deduplication merges metadata but needs to preserve earliest `posted_at` and latest `last_seen_at`. | Update deduplication to retain the true original publication date. |
| **Matching & Ranking System** | 100-point multi-factor model in `backend/app/intelligence/matcher.py`. | Fast deterministic scoring across skills, experience, employment type, eligibility, compensation, and risk. | **Critical Flaw**: Engineering Manager/Principal roles scored 90.2/100 because high technical skill overlap compensated for missing leadership experience. Lacks CV project evidence weighting and freshness scoring. | Redesign scoring into an 8-factor 100-point model with strict seniority penalties (up to -25 pt deduction for unverified leadership) and freshness points (0-10 pts). |
| **Discovery Engine** | Automated query generator and DuckDuckGo search provider in `backend/app/discovery/`. | Discovers novel seed platforms, checks robots.txt, validates safety, and scores relevance before adding to candidates. | Search results occasionally surface duplicate domains or low-relevance blog aggregators. | Add domain canonicalization and platform pattern heuristics. |
| **API & Backend Layer** | FastAPI with synchronous endpoints, Pydantic schemas, dependency injection, and static file serving. | Clean RESTful design, runs reliably on Windows without Proactor loop hangs, fully typed. | Missing endpoints for CV upload (`POST /api/cv/upload`), CV profile management (`GET/PUT/DELETE /api/cv`), and freshness filtering query params. | Implement full CV REST API and freshness query parameter filters. |
| **Frontend Dashboard** | React 18 + TypeScript + Tailwind CSS SPA, Vite build, served at `/` via FastAPI. | Complete tabbed UI (Overview, Opportunities, Sources, Discovery, Profile, Reports), modal dialogs, status badges. | Lacks freshness filter dropdown (6h, 12h, 24h, 3d, 4d, 7d, 30d, custom) and dedicated "My CV & Professional Profile" interactive analysis/approval interface. | Add Freshness dropdown selector to Opportunities explorer; build dedicated CV Review page with dropzone, project cards, and approval workflow. |
| **Report Generation** | Standalone HTML and Markdown generators in `backend/app/reports/`. | Clean visual hierarchy, zero external CDN dependencies, self-contained CSS styling. | Missing Freshness Breakdown section, Top CV Matches section, and Outlier account status summary. | Upgrade report templates to reflect freshness tiers and CV-matched project highlights. |
| **Automated Testing** | Pytest suite in `backend/tests/` (44 tests passing). | Tests cover config, connectors, database repositories, discovery engine, intelligence pipeline, security sanitization, and 10 negative cases. | Lacks tests for rolling freshness windows, multi-page CV extraction, seniority penalty enforcement, and CV profile editing. | Implement comprehensive test suites: `test_freshness.py`, `test_cv.py`, `test_ranking.py`. |

---

## 3. Assessment of Existing Ranking Flaw (The 90.2/100 Engineering Manager Issue)

### 3.1 Root Cause Analysis
During baseline integration testing, an opportunity titled `Engineering Manager, Infrastructure` scored **90.2 out of 100**.
Inspection of `backend/app/intelligence/matcher.py` (lines 62-72) revealed:
```python
# 2. Experience Match (max 20 pts)
desc_lower = description.lower()
if any(term in desc_lower for term in ["senior", "lead", "architect", "expert", "5+ years", "staff"]):
    exp_subscore = 20.0
elif any(term in desc_lower for term in ["mid-level", "3+ years", "experienced"]):
    exp_subscore = 17.0
...
```
Because the candidate's profile contained strong technical skills in PyTorch, Kubernetes, Docker, and AWS, the opportunity achieved:
- Technical Skills Match: **30.0 / 30.0**
- Experience Match: **20.0 / 20.0** (because the job text mentioned "senior" and "5+ years")
- Opportunity Type: **10.0 / 10.0** (remote contract)
- Egypt Eligibility: **15.0 / 15.0** (worldwide remote)
- Compensation: **10.0 / 10.0** ($50+/hr)
- Project Quality: **10.0 / 10.0** (clear description)
- Feasibility: **5.0 / 5.0**
- **Total: 100.0 (normalized with domain factor to 90.2)**

### 3.2 The Flaw
1. The engine evaluated the **presence of senior keywords in the job description**, rather than comparing the **job's seniority requirements against the candidate's actual CV qualifications**.
2. An Individual Contributor (IC) AI Engineer without management experience was awarded full points on a People Management role.
3. No penalty was assessed for a severe seniority gap.

### 3.3 Solution Architecture
The upgraded `MatchingEngine` introduces:
- A standardized 8-level seniority hierarchy: `intern` (0), `entry` (1), `junior` (2), `intermediate` (3), `senior` (4), `lead` (5), `manager` (6), `principal` (7).
- Seniority extraction from both job posting and CV evidence.
- A **Strict Seniority Compatibility Gate**:
  - If a role requires `manager`, `director`, or `vp` and the candidate's approved CV profile has no verified leadership/management history, apply a **-25.0 point penalty** and flag `seniority_compatibility = "incompatible_leadership"`.
  - If a role requires `principal` or `staff` (>8 years required) and the candidate has intermediate experience (2-4 years), apply a **-15.0 point penalty**.
  - If a candidate is overqualified (e.g. senior applying to intern), apply a **-10.0 point penalty**.

---

## 4. Assessment of Required Database Changes

To support Freshness Intelligence and CV Intelligence without breaking existing data:

### 4.1 Schema Additions to `OpportunityModel` (`backend/app/database/models/opportunity.py`)
```python
# Exact timestamp tracking
posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
collected_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

# Freshness classification & score
freshness_status: Mapped[str] = mapped_column(String(32), default="unknown_date", index=True)
freshness_score: Mapped[float] = mapped_column(Float, default=0.0)

# Seniority & CV matching breakdown
seniority_compatibility: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
seniority_mismatch_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
cv_match_breakdown: Mapped[dict] = mapped_column(JSON, default=dict)
```

### 4.2 New Table: `CVProfileModel` (`backend/app/database/models/cv_profile.py`)
```python
class CVProfileModel(Base):
    __tablename__ = "cv_profiles"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    filename: Mapped[str] = mapped_column(String(256), nullable=False)
    file_type: Mapped[str] = mapped_column(String(32), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    professional_headline: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    career_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    years_of_experience: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    seniority_level: Mapped[str] = mapped_column(String(64), default="intermediate")
    technical_skills: Mapped[list] = mapped_column(JSON, default=list)
    projects: Mapped[list] = mapped_column(JSON, default=list)
    skill_evidence: Mapped[list] = mapped_column(JSON, default=list)
    education: Mapped[list] = mapped_column(JSON, default=list)
    certifications: Mapped[list] = mapped_column(JSON, default=list)
    languages: Mapped[list] = mapped_column(JSON, default=list)
    employment_history: Mapped[list] = mapped_column(JSON, default=list)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
```

---

## 5. Implementation Plan: Freshness Intelligence Engine

### 5.1 Architecture & Components
1. **Module `backend/app/intelligence/freshness.py`**:
   - `FreshnessClassifier`: Parses ISO8601 strings, RFC2822 dates, Unix timestamps, and relative expressions ("4 hours ago", "yesterday", "3 days ago").
   - Timezone localization: All comparisons in timezone-aware UTC, with display localization to `Africa/Cairo` (UTC+2 / UTC+3 DST aware).
   - Rolling Window Evaluator:
     - `6h`: `posted_at >= now - 6 hours`
     - `12h`: `posted_at >= now - 12 hours`
     - `24h`: `posted_at >= now - 24 hours`
     - `3d`: `posted_at >= now - 72 hours`
     - `4d`: `posted_at >= now - 96 hours`
     - `7d`: `posted_at >= now - 7 days` (Default)
     - `30d`: `posted_at >= now - 30 days`
     - `custom`: `posted_from <= posted_at <= posted_to`
     - `all`: All records, segregating `unknown_date`.
2. **Freshness Scoring Model (10 pts of 100)**:
   - Within 6h: 10.0 pts (100% freshness score)
   - Within 24h: 9.5 pts (95% freshness score)
   - Within 3 days: 8.5 pts (85% freshness score)
   - Within 4 days: 8.0 pts (80% freshness score)
   - Within 7 days: 6.5 pts (65% freshness score)
   - Within 30 days: 4.0 pts (40% freshness score)
   - Older: 1.5 pts (15% freshness score)
   - Unknown date: 0.0 pts (0% freshness score)
3. **Connector Timestamp Upgrades**:
   - `RemotiveConnector`: Extract `job.get("publication_date")`.
   - `RemoteOKConnector`: Extract `job.get("date")`.
   - `HimalayasConnector`: Extract `job.get("pub_date")`.
   - `WeWorkRemotelyConnector`: Extract RSS `<pubDate>`.
   - `OutlierPublicConnector` & `AlignerrPublicConnector`: Extract `updated_at` / `created_at`.

---

## 6. Implementation Plan: Deep CV Intelligence Engine

### 6.1 Processing Pipeline
1. **Document Ingestion**:
   - Supported formats: `.pdf` (via `pymupdf` / `pypdf`), `.docx` (via `python-docx`), `.txt`.
   - Multi-page extraction preserving text order and line breaks.
   - Clean boundary extraction for sections: Summary, Technical Skills, Projects, Experience/Employment, Education, Certifications.
2. **Entity & Evidence Extraction**:
   - Skill extraction with canonical normalization (e.g., `K8s` -> `Kubernetes`, `Deep Learning` -> `Deep Learning`).
   - Project parser: Extracts Title, Domain, Technologies, Description, and Quantifiable Metrics.
   - **Evidence Attribution**:
     - `PROJECT_DEMONSTRATED`: Skill is explicitly used in a named project with functional context (Weight: 2.0x).
     - `EMPLOYMENT_DEMONSTRATED`: Skill is mentioned in job responsibilities (Weight: 1.5x).
     - `SKILL_LIST_ONLY`: Skill only appears in a bulleted skills list (Weight: 1.0x).
     - `INFERRED`: Skill inferred from ecosystem (e.g. PyTorch + FastAPI -> Model Deployment) (Weight: 0.5x).
3. **Interactive Review & Approval**:
   - Extracted CV profile is stored in `cv_profiles` table with `approved = False`.
   - User reviews parsed skills, projects, and seniority on the frontend `/cv` page.
   - User edits or adds corrections and clicks "Approve Profile".
   - Only approved profiles are used as the active matching baseline.
4. **Local Privacy Guarantee**:
   - Files are processed strictly locally in memory or in `data/cv/`.
   - Zero external cloud transmission of personal CV data unless user explicitly configures an LLM API key.

---

## 7. Potential Breaking Changes & Mitigations

1. **Database Schema Evolution**:
   - *Risk*: Adding columns to `opportunities` might fail on existing SQLite database.
   - *Mitigation*: Use SQLite `ALTER TABLE ADD COLUMN` migration scripts or safe column verification in `init_db()`.
2. **Matching Score Shifts**:
   - *Risk*: Existing stored opportunities will have score changes under the new 8-factor 100-point model.
   - *Mitigation*: Re-score existing opportunities upon pipeline run or provide backward-compatible defaults.
3. **Filter Restrictiveness**:
   - *Risk*: Strict 24h filter will return fewer results if sources post infrequently.
   - *Mitigation*: Default filter is `7d` (Last 7 Days) with clear counters showing how many listings fall into each freshness tier.

---

## 8. Audit Verification Sign-Off

The system architecture is sound, modular, and ready for incremental implementation of Phase 2 through Phase 8. All changes preserve existing working connectors, database repositories, and test coverage.

