# Global AI Opportunities Intelligence Agent
**Version 2.0 Production Hardened**

A manually operated, production-grade AI opportunity discovery, intelligence, and matching platform designed for an **AI Engineer based in Egypt**.

The system dynamically discovers, collects, normalizes, validates, classifies, filters, evaluates geographic and payout eligibility, deduplicates, scores, and generates comprehensive reports on legitimate paid AI opportunities globally.

---

## 1. Core Mission & Philosophy

- **Manual Trigger Only**: The application runs strictly on-demand (via CLI `python main.py run` or the dashboard button **"RUN GLOBAL AI OPPORTUNITY SEARCH"**). No background daemons, cron jobs, or automatic polling.
- **Deep CV Intelligence**: Ingests your real resume (PDF, DOCX, or TXT), extracts functional project deliverables, links skills to tangible evidence, and estimates seniority.
- **Strict Seniority Compatibility**: Eliminates false-positive recommendations on senior leadership roles (e.g. Engineering Manager roles are penalized by -25.0 points if the candidate has an Individual Contributor background).
- **Opportunity Freshness Intelligence**: Distinguishes original publication dates (`posted_at`) from crawler discovery times (`first_seen_at`), enabling rolling window filtering from 6 hours to 30 days.
- **Strict Exclusions**: Speech/Audio tasks (ASR, TTS, Voice AI, audio annotation, transcription) and generic automation (RPA, PLC, SCADA, Zapier) are strictly purged before scoring.
- **Egyptian Eligibility Gating**: Every opportunity is vetted for Egyptian location eligibility and payout compatibility (Payoneer, Direct Wire/SWIFT, PayPal, Wise).
- **Zero Fabrication**: Only actual verified listings from legitimate endpoints are reported. The system never invents jobs, pay rates, or platforms.

---

## 2. Key Architecture & Features

```
[Uploaded Resume: PDF / DOCX] ──> [Deep CV Intelligence Engine] ──> [Approved Skill & Project Evidence]
                                                                                │
[Global Verified Connectors]   ──> [True Publication Timestamp Extraction] ───┼──> [100-Point Match & Seniority Engine]
(Outlier, Alignerr, Remotive,      (posted_at: 6h / 24h / 4d / 7d / 30d)        │    (8 Factors, -25pt Manager Penalty)
 RemoteOK, Himalayas, WWR)                                                      │                  │
                                                                                ▼                  ▼
                                                                [Strict Negative Exclusions] ──> [HTML & Markdown Reports]
                                                                (Speech/Audio & Generic RPA)    [React 18 Dashboard SPA]
```

### 2.1 Advanced Freshness Engine
- Tracks `posted_at`, `updated_at`, `first_seen_at`, `last_seen_at`, `last_verified_at`, and `collected_at`.
- Six freshness statuses: `fresh_verified`, `fresh_relative`, `updated_recently`, `stale`, `unknown_date`, `expired`.
- Rolling time windows: `6h`, `12h`, `24h`, `3d`, `4d`, `7d` (default), `30d`, `custom`, `all`.
- Timezone handling: Timezone-aware UTC with localized `Africa/Cairo` display formatting.

### 2.2 Deep CV Intelligence Engine
- Ingests multi-page resumes in PDF (`pypdf`), DOCX (`python-docx`), or TXT.
- Parses projects with quantifiable metrics (FPS, mAP, latency, throughput).
- Skill evidence attribution: `project` (2.0x), `employment` (1.5x), `skills_list` (1.0x), `inferred` (0.5x).
- Standardized 8-level seniority taxonomy: `intern`, `entry`, `junior`, `intermediate`, `senior`, `lead`, `manager`, `principal`.

### 2.3 Refactored 100-Point Scoring Model
$$\text{Score} = \max\left(0, \min\left(100, \sum_{i=1}^8 S_i - P_{\text{seniority}}\right)\right)$$

| Dimension | Max Points | Description |
|---|---:|---|
| **CV Technical Skill Match** | 25 pts | Project-backed skills (2.0x) vs keyword list (1.0x) |
| **Seniority Compatibility** | 15 pts | Role requirements matched against CV experience |
| **Egypt Eligibility** | 15 pts | Worldwide remote or verified Egypt contracts |
| **Publication Freshness** | 10 pts | Published $\le$ 6h: 10 pts, $\le$ 24h: 9.5 pts, $\le$ 7d: 6.5 pts |
| **Compensation Quality** | 10 pts | Hourly rate or fixed milestone attractiveness |
| **Opportunity Type** | 10 pts | Remote contract, freelance, or per-task AI evaluation |
| **Project Quality & Clarity** | 10 pts | Clear scope, concrete deliverables, low risk |
| **Application Feasibility** | 5 pts | Direct application link and low barrier |
| **Management Penalty Gate** | **-25 pts** | Deducted when role requires unverified people management |

---

## 3. Quick Start & Execution

### 3.1 Initialize Database
```powershell
python main.py init-db
```

### 3.2 Ingest & Approve Your CV
```powershell
python main.py upload-cv data/sample_cv.txt --approve
python main.py show-cv
```

### 3.3 Execute On-Demand Search Run
```powershell
python main.py run
```

### 3.4 Start the Web Dashboard
```powershell
python main.py serve
```
Open your browser to: **`http://127.0.0.1:8000`**

### 3.5 Run Full Test Suite
```powershell
.venv\Scripts\python.exe -m pytest backend/tests -v
```
*(60/60 tests passing with zero warnings)*

---

## 4. Documentation Index

- `docs/PRODUCTION_AUDIT.md`: System architectural assessment and component status.
- `docs/SOURCE_COVERAGE_MATRIX.md`: 35+ platform audit and integration matrix.
- `docs/RANKING_AUDIT.md`: Autopsy and resolution of the 90.2/100 Engineering Manager issue.
- `docs/EGYPT_ELIGIBILITY_AUDIT.md`: Cross-border contract models and Egypt payout rails.
- `docs/FRESHNESS_ENGINE.md`: Rolling windows and exact publication timestamp architecture.
- `docs/CV_INTELLIGENCE.md`: Deep resume parsing, project deliverables, and evidence attribution.
- `PROJECT_STATUS.md`: Comprehensive delivery status, test evidence, and operational commands.
