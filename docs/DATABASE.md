# Database Design & Persistence Specification

## 1. Storage Strategy & ORM
- **Engine**: SQLite via asynchronous `aiosqlite` with sync fallback for Alembic migrations.
- **ORM**: SQLAlchemy 2.0 (Declarative Base with Mapped and mapped_column typing).
- **Portability**: Schema adheres strictly to standard ANSI SQL data types (String, Text, Float, Integer, Boolean, DateTime, JSON) to ensure seamless portability to PostgreSQL with zero redesign.
- **Historical Tracking**: Records are never overwritten destructively; `first_seen_at`, `last_seen_at`, and `last_verified_at` preserve lifecycle history.

---

## 2. Relational Schema & Models

### `sources`
Stores registered platforms, marketplaces, and boards.
- `id` (VARCHAR(64), Primary Key) — e.g., `"outlier"`, `"remotive"`.
- `name` (VARCHAR(128), Not Null).
- `category` (VARCHAR(64), Indexed) — `ai_training_and_evaluation`, `remote_job_board`, `freelance_marketplace`, `ai_data_and_annotation`, `ai_expert_network`.
- `official_website` (VARCHAR(512), Not Null).
- `careers_url` (VARCHAR(512), Nullable).
- `api_url` (VARCHAR(512), Nullable).
- `collection_method` (VARCHAR(32), Not Null) — `api`, `rss`, `public_web`, `browser_session`.
- `status` (VARCHAR(32), Indexed, Default `'verified'`) — `verified`, `candidate`, `unverified`, `restricted`, `broken`, `deprecated`.
- `requires_auth` (BOOLEAN, Default False).
- `supports_account_inspection` (BOOLEAN, Default False).
- `supports_egypt` (VARCHAR(32), Default `'unknown'`) — `verified`, `likely`, `unverified`, `restricted`, `ineligible`.
- `payment_methods` (JSON, Nullable) — List of supported payout channels.
- `enabled` (BOOLEAN, Default True).
- `last_health_check_at` (DATETIME, Nullable).
- `last_success_at` (DATETIME, Nullable).
- `consecutive_failures` (INTEGER, Default 0).
- `created_at` (DATETIME, Default UTC now).
- `updated_at` (DATETIME, Default UTC now).

---

### `opportunities`
Normalized universal opportunity data model.
- `id` (VARCHAR(64), Primary Key) — Deterministic SHA256 of canonical URL or source+external_id.
- `source_id` (VARCHAR(64), Foreign Key `sources.id`, Indexed).
- `source_name` (VARCHAR(128)).
- `source_type` (VARCHAR(64)).
- `title` (VARCHAR(256), Indexed, Not Null).
- `company` (VARCHAR(128), Indexed, Nullable).
- `description` (TEXT, Not Null).
- `original_url` (VARCHAR(1024), Not Null).
- `canonical_url` (VARCHAR(1024), Indexed, Not Null).
- `category` (VARCHAR(64), Indexed).
- `technical_domains` (JSON) — e.g. `["large_language_models", "ai_agents"]`.
- `required_skills` (JSON) — List of extracted skills.
- `preferred_skills` (JSON).
- `experience_level` (VARCHAR(64)) — `Junior`, `Mid`, `Senior`, `Lead`, `Expert`.
- `employment_type` (VARCHAR(64)) — `freelance`, `contract`, `hourly`, `fixed_price`, `per_task`.
- `payment_model` (VARCHAR(64)) — `hourly`, `fixed`, `per_task`, `milestone`, `not_disclosed`.
- `hourly_rate_min` (FLOAT, Nullable).
- `hourly_rate_max` (FLOAT, Nullable).
- `fixed_budget_min` (FLOAT, Nullable).
- `fixed_budget_max` (FLOAT, Nullable).
- `currency` (VARCHAR(8), Default `'USD'`).
- `payment_details` (TEXT, Nullable).
- `location` (VARCHAR(256), Nullable).
- `remote_status` (VARCHAR(32)) — `remote`, `hybrid`, `onsite`.
- `eligible_countries` (JSON) — Extracted country list or `["Worldwide"]`.
- `egypt_eligibility` (VARCHAR(32), Indexed) — `eligible`, `likely_eligible`, `unverified`, `not_eligible`, `restricted`.
- `payment_methods` (JSON).
- `application_requirements` (TEXT, Nullable).
- `assessment_required` (BOOLEAN, Default False).
- `posted_at` (DATETIME, Nullable).
- `deadline` (DATETIME, Nullable).
- `first_seen_at` (DATETIME, Not Null).
- `last_seen_at` (DATETIME, Not Null).
- `last_verified_at` (DATETIME, Not Null).
- `listing_status` (VARCHAR(32), Default `'active'`) — `active`, `expired`, `removed`.
- `verification_status` (VARCHAR(32), Default `'unverified'`) — `verified`, `unverified`, `disputed`.
- `skill_match_score` (FLOAT, Default 0.0).
- `eligibility_score` (FLOAT, Default 0.0).
- `overall_score` (FLOAT, Indexed, Default 0.0).
- `match_explanation` (TEXT, Nullable).
- `missing_skills` (JSON).
- `recommendation` (VARCHAR(64)) — `Excellent Match`, `Strong Match`, `Good Match`, `Moderate Match`, `Low Match`, `Not Recommended / Ineligible`.
- `duplicate_group_id` (VARCHAR(64), Nullable, Indexed).
- `raw_data_reference` (TEXT, Nullable).
- `risk_level` (VARCHAR(32), Default `'low'`) — `low`, `review`, `high`, `scam`.
- `risk_explanation` (TEXT, Nullable).
- `created_at` (DATETIME, Default UTC now).
- `updated_at` (DATETIME, Default UTC now).

---

### `source_candidates`
Discovered URLs and potential platforms waiting for validation.
- `id` (INTEGER, Primary Key, Autoincrement).
- `domain` (VARCHAR(256), Unique, Indexed).
- `platform_name` (VARCHAR(128)).
- `source_url` (VARCHAR(1024), Not Null).
- `category` (VARCHAR(64)).
- `discovered_via_query` (VARCHAR(256)).
- `validation_status` (VARCHAR(32)) — `pending`, `approved`, `rejected`, `unsupported`.
- `legitimacy_score` (FLOAT, Default 0.0).
- `supports_egypt` (VARCHAR(32)).
- `payment_models_found` (JSON).
- `detection_notes` (TEXT).
- `created_at` (DATETIME, Default UTC now).
- `reviewed_at` (DATETIME, Nullable).

---

### `collection_runs`
Audit history of every manual run.
- `id` (VARCHAR(64), Primary Key) — e.g. `run_20261102_125000`.
- `trigger_type` (VARCHAR(32)) — `manual_cli`, `manual_ui`.
- `started_at` (DATETIME, Not Null).
- `finished_at` (DATETIME, Nullable).
- `status` (VARCHAR(32)) — `running`, `completed`, `failed`, `partial`.
- `sources_attempted` (INTEGER, Default 0).
- `sources_succeeded` (INTEGER, Default 0).
- `sources_failed` (INTEGER, Default 0).
- `total_collected` (INTEGER, Default 0).
- `new_count` (INTEGER, Default 0).
- `duplicate_count` (INTEGER, Default 0).
- `excluded_count` (INTEGER, Default 0).
- `relevant_count` (INTEGER, Default 0).
- `report_html_path` (VARCHAR(512), Nullable).
- `report_md_path` (VARCHAR(512), Nullable).
- `summary_json` (JSON, Nullable).

---

### `duplicate_groups`
Tracks cross-source clusters of the same opportunity.
- `id` (VARCHAR(64), Primary Key).
- `canonical_opportunity_id` (VARCHAR(64), Foreign Key `opportunities.id`).
- `merged_count` (INTEGER, Default 1).
- `created_at` (DATETIME, Default UTC now).

