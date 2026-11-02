# OPPORTUNITY FRESHNESS INTELLIGENCE ENGINE
**Global AI Opportunities Intelligence Agent**
*Date: November 2, 2026 | Version: 2.0 | Status: Production Hardened*

---

## 1. Executive Summary & Design Mission

In global AI freelancing and contracting, opportunities move extremely quickly: the highest-value contracts ($40–$100+/hr) and new RLHF project batches often receive qualified applicants within hours of posting. 

A critical flaw in generic job aggregators is displaying stale 30-day-old listings as "new" simply because the crawler visited the page today. The **Advanced Opportunity Freshness Intelligence Engine** enforces strict distinction between original publication dates (`posted_at`) and scraping discovery timestamps (`first_seen_at`), enabling rolling window filtering down to the last 6 hours.

---

## 2. Core Timestamp Model

| Field Name | Type | Definition & Integrity Guarantee |
|---|---|---|
| `posted_at` | `DateTime (UTC)` | **Original publication timestamp** provided by the origin ATS or API. Indexed in SQLite. If unknown, strictly stored as `NULL` — never fabricated. |
| `updated_at` | `DateTime (UTC)` | Timestamp of most recent listing edit or status change on the source platform. |
| `first_seen_at` | `DateTime (UTC)` | When the application's collector first encountered this opportunity record. |
| `last_seen_at` | `DateTime (UTC)` | When the opportunity was most recently verified still present and active during a collection run. |
| `last_verified_at` | `DateTime (UTC)` | When availability verification (HTTP status or page check) was executed. |
| `collected_at` | `DateTime (UTC)` | Exact execution time of the current retrieval batch. |

> **Critical Rule:** `first_seen_at` or `collected_at` must **never** be used as a substitute for `posted_at`. A 25-day-old job discovered today is classified as **stale**, not new.

---

## 3. Freshness Status Taxonomy

Every opportunity is assigned a deterministic `freshness_status`:

1. **`fresh_verified`**:
   - Opportunity has a verified, exact publication timestamp (`posted_at`) falling within the active rolling window.
2. **`fresh_relative`**:
   - Opportunity publication date was derived from an explicit relative string (e.g. "2 hours ago", "yesterday", "3d ago").
3. **`updated_recently`**:
   - The original publication date is older than 7 days, but the source was updated or renewed within the last 7 days.
4. **`stale`**:
   - Publication date is older than 30 days.
5. **`unknown_date`**:
   - Origin source provides no publication timestamp (e.g. some landing pages). Clearly badged in the UI as `[Date Unknown]` and excluded from strict rolling time windows unless the user explicitly toggles `include_unknown_dates=true`.
6. **`expired`**:
   - Opportunity has been closed, filled, or returns HTTP 404.

---

## 4. Freshness Scoring Formula (0–100 Score, 10 Pts of 100)

Freshness directly contributes up to **10 points** to the final opportunity ranking score:

$$\text{Freshness Points} = \frac{\text{Freshness Score}}{100} \times 10.0$$

| Publication Age | Freshness Score | Points Awarded | Recommended Action |
|---|---:|---:|---|
| **$\le$ 6 Hours** | 100.0 | 10.0 pts | Apply immediately; early applicant advantage |
| **$\le$ 24 Hours** | 95.0 | 9.5 pts | High priority application |
| **$\le$ 3 Days (72h)** | 85.0 | 8.5 pts | Active listing; apply today |
| **$\le$ 4 Days (96h)** | 80.0 | 8.0 pts | Fresh listing |
| **$\le$ 7 Days (168h)** | 65.0 | 6.5 pts | Standard weekly window (Default filter) |
| **$\le$ 30 Days (720h)** | 40.0 | 4.0 pts | Older listing; verify status |
| **> 30 Days (Stale)** | 15.0 | 1.5 pts | Low priority |
| **Unknown Publication Date** | 0.0 | 0.0 pts | Gated; requires manual review |

---

## 5. Supported Rolling Windows & Backend Filtering

The backend API (`GET /api/opportunities`) supports the following parameters:

```http
GET /api/opportunities?freshness=24h&include_unknown_dates=false
```

| Parameter Value | Rolling Cutoff Window |
|---|---|
| `freshness=6h` | `posted_at >= now - 6 hours` |
| `freshness=12h` | `posted_at >= now - 12 hours` |
| `freshness=24h` | `posted_at >= now - 24 hours` |
| `freshness=3d` | `posted_at >= now - 72 hours` |
| `freshness=4d` | `posted_at >= now - 96 hours` |
| `freshness=7d` | `posted_at >= now - 7 days` (Default) |
| `freshness=30d` | `posted_at >= now - 30 days` |
| `freshness=custom` | `posted_from <= posted_at <= posted_to` |
| `freshness=all` | All records, preserving unknown dates |

---

## 6. Timezone Architecture

- **Internal Storage & Calculations**: 100% timezone-aware UTC (`datetime.now(timezone.utc)`).
- **Display Layer**: Formatted in `Africa/Cairo` (UTC+2 / UTC+3 DST aware).
- **Naive Datetime Elimination**: Naive datetimes are automatically cast to UTC on ingestion to avoid comparison runtime crashes.

