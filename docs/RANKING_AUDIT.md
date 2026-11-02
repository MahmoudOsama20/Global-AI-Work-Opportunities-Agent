# RANKING & SENIORITY AUDIT: 100-POINT SCORING REFACTOR
**Global AI Opportunities Intelligence Agent**
*Date: November 2, 2026 | Focus: Elimination of Seniority False Positives & Project-Driven Matching*

---

## 1. Autopsy: Why "Engineering Manager, Infrastructure" Scored 90.2/100

### 1.1 The Anomaly
In the initial baseline pipeline run, the job posting:
> **Title:** Engineering Manager, Infrastructure  
> **Company:** Scale AI / Outlier  
> **Requirements:** 8+ years software experience, 3+ years managing engineering teams, Kubernetes, AWS, Terraform, Docker, Python, ML Infrastructure.  

received a final score of **90.2 / 100**, placing it in the **Top Recommended Opportunities** tier for an Individual Contributor (IC) AI Engineer candidate profile with 2–4 years of experience and zero people management background.

### 1.2 Mathematical Autopsy of the Previous Formula
In the previous implementation (`backend/app/intelligence/matcher.py`):
```python
# Old Score Breakdown for "Engineering Manager, Infrastructure"
1. Technical Skills:       30.0 / 30.0  (Matched: Python, Kubernetes, Docker, AWS, ML Infrastructure)
2. Experience Match:       20.0 / 20.0  (Triggered because desc contains "5+ years" or "staff/lead")
3. Opportunity Type:       10.0 / 10.0  (Tagged as remote contract)
4. Egypt Eligibility:      15.0 / 15.0  (Worldwide remote eligible)
5. Compensation:           10.0 / 10.0  (Competitive $60+/hr)
6. Project Quality:        10.0 / 10.0  (Detailed posting > 1000 chars)
7. Feasibility:             5.0 /  5.0  (Standard application)
---------------------------------------
Raw Subtotal:             100.0 / 100.0
Domain Factor Adj:         90.2 / 100.0 (Due to MLOps domain priority)
```

### 1.3 Why This Happened (The Architectural Flaws)
1. **Passive Regex Keyword Matching Instead of Role Alignment**: The engine tested `any(term in desc for term in ["senior", "lead", "architect", "5+ years"])`. Because the job posting required substantial experience, it ironically awarded the candidate maximum experience points, rather than checking if the candidate *met* that seniority level.
2. **Technical Skill Over-dominance**: Overlap in foundational infrastructure tools (Python, Docker, Kubernetes) masked the fact that the job was an *Engineering Manager* role where 80% of daily responsibilities involve team management, 1-on-1s, hiring, and budget allocation.
3. **Absence of Negative Penalty Gates**: There was no mechanism to deduct points when a mandatory qualification (e.g. people management or staff/principal status) was completely absent from the candidate profile.

---

## 2. Seniority & Experience Level Taxonomy

To resolve this permanently, the matching architecture implements a standardized 8-level seniority hierarchy:

| Level Index | Seniority Level | Definition & Job Indicators | Typical Experience Required | Candidate Profile Requirement |
|---|---|---|---|---|
| **0** | `intern` | Summer intern, student researcher, co-op | Enrolled student or recent graduate | Suitable for entry candidates; overqualified for senior |
| **1** | `entry` | Associate engineer, entry-level, junior AI annotator | 0–1 year | Candidate starting out |
| **2** | `junior` | Junior engineer, 1–2 years practical work | 1–2 years | Hands-on project implementation |
| **3** | `intermediate` | AI/ML Engineer, Computer Vision Engineer (Mid-level) | 2–5 years | Multiple production or production-ready projects |
| **4** | `senior` | Senior AI Engineer, Senior CV Specialist | 5–8 years | Complex architecture, end-to-end delivery |
| **5** | `lead` | Tech Lead, Team Lead, AI Squad Lead | 6–10 years + team coordination | Technical guidance, code review leadership |
| **6** | `manager` | Engineering Manager, AI Director, Team Manager | 3+ years people management | Direct reports, hiring, performance reviews, budgeting |
| **7** | `principal` | Principal Engineer, Staff Engineer, Distinguished AI Scientist | 10+ years industry-wide impact | Cross-organizational technical leadership |

---

## 3. Experience Source Classification & Differentiation

Years of experience must be attributed based on the **nature of the evidence**, not just date math:

1. **Professional Full-Time Employment (`EMPLOYMENT`)**:
   - High confidence (Weight: 1.0x).
   - Counts fully toward commercial seniority.
2. **Freelance & Contractor Projects (`FREELANCE`)**:
   - Verified paid client work (Weight: 0.85x).
   - Counts toward technical and delivery autonomy.
3. **Independent Production Projects (`PROJECT_PRODUCTION`)**:
   - Deployed systems, open-source repositories with users, live demo apps (Weight: 0.75x).
   - Demonstrates implementation capability, but does not substitute for people management.
4. **Academic & Research Projects (`ACADEMIC`)**:
   - Master's thesis, university lab research, benchmark papers (Weight: 0.6x).
   - Demonstrates algorithm depth; does not prove commercial MLOps or enterprise leadership.
5. **Internships (`INTERNSHIP`)**:
   - Supervised student work (Weight: 0.5x).

---

## 4. The Refactored 100-Point Scoring Model

The new scoring model balances 8 distinct factors with explicit penalties:

$$\text{Final Score} = \max\left(0, \min\left(100, \sum_{i=1}^{8} S_i - P_{\text{seniority}}\right)\right)$$

| Dimension | Max Points | Scoring Logic & Evidence Requirements |
|---|---:|---|
| **1. CV Technical Skill Match** | **25 pts** | Evaluates required and preferred skills against the candidate's CV. Skills backed by **Project Evidence** receive **2.0x weight**; skills backed by employment history receive **1.5x weight**; skills listed only in a keyword block receive **1.0x weight**; transferable skills receive **0.5x weight**. |
| **2. Seniority & Experience Compatibility** | **15 pts** | Compares role seniority level with candidate profile seniority. Perfect alignment = 15 pts; 1 level gap (e.g. intermediate vs senior) = 11 pts; 2 levels gap = 6 pts; 3+ levels gap = 0 pts. |
| **3. Egypt Eligibility & Gate** | **15 pts** | Worldwide remote or explicit Egypt confirmation = 15 pts; EMEA/Timezone compatible = 10 pts; Unspecified/Unknown = 6 pts with risk flag; US/EU-only geofenced = 0 pts (and filtered from top recommendations). |
| **4. Freshness Score** | **10 pts** | Published $\le$ 6h: 10 pts; $\le$ 24h: 9.5 pts; $\le$ 3d: 8.5 pts; $\le$ 4d: 8.0 pts; $\le$ 7d: 6.5 pts; $\le$ 30d: 4.0 pts; Older: 1.5 pts; Unknown publication date: 0.0 pts. |
| **5. Compensation Quality** | **10 pts** | Hourly rate $\ge$ \$40/hr or fixed $\ge$ \$1000 = 10 pts; \$25–\$40/hr = 8.5 pts; \$15–\$25/hr = 7.0 pts; Undisclosed but reputable = 6.0 pts; Under \$15/hr = 3.0 pts. |
| **6. Opportunity Type Preference** | **10 pts** | Remote contract, freelance gig, or paid AI evaluation task = 10 pts; Full-time remote engineering = 8 pts; On-site/hybrid = 0 pts. |
| **7. Project Quality & Clarity** | **10 pts** | Clear scope, concrete deliverables, reputable organization = 10 pts; Brief or vague description = 5 pts; High-risk / scam signals = 0 pts. |
| **8. Application Feasibility** | **5 pts** | Direct application link or simple ATS form = 5 pts; Complex assessment or video pitch required = 3 pts. |

---

## 5. Strict Negative Penalty Gates

If a significant mismatch is detected, the engine deducts points directly from the total score:

1. **Management & Leadership Mismatch Penalty ($-25.0$ pts)**:
   - Condition: Opportunity requires `manager`, `director`, `vp`, or `head_of` with people management responsibilities, AND candidate CV has no verified management track record.
   - Result: Scores for roles like "Engineering Manager, Infrastructure" drop from **90.2** to **< 55.0**, ensuring they never appear as top recommendations.
   - Flag: `seniority_compatibility = "incompatible_leadership"`.
   - Reason: *"Role requires extensive people management (3+ years managing engineering teams), which is not demonstrated in candidate CV."*
2. **Principal / Staff Mismatch Penalty ($-15.0$ pts)**:
   - Condition: Opportunity requires `principal` or `staff` engineer (8–10+ years industry leadership) and candidate is intermediate (2–4 years).
   - Flag: `seniority_compatibility = "insufficient_seniority"`.
3. **Overqualification Penalty ($-10.0$ pts)**:
   - Condition: Opportunity is an unpaid internship or entry-level annotator role and candidate has 3+ years experience.

---

## 6. Transferable Skill Graph

The matching engine employs a controlled, directed relationship graph with transferability confidence:

| Source Skill (in CV) | Transferable Target Skill | Confidence | Rationale |
|---|---|---:|---|
| `PyTorch` + `FastAPI` | `Model Serving / ML Deployment` | 0.85 | Candidate can wrap neural network inference in high-performance REST APIs. |
| `YOLO` + `OpenCV` | `Video Analytics / Edge Vision` | 0.80 | Detection models directly apply to video streaming and object tracking pipelines. |
| `Docker` + `FastAPI` | `Containerized Microservices` | 0.75 | Direct containerization of backend ML services. |
| `Transformers` + `Embeddings` | `RAG / Semantic Search` | 0.85 | Foundational NLP components directly map to retrieval-augmented generation. |
| `LangChain` / `LlamaIndex` | `AI Agents / Function Calling` | 0.80 | Agentic workflows build on orchestration frameworks. |

> **Constraint:** A transferable skill cannot substitute for a hard prerequisite (e.g. Docker knowledge does NOT grant Kubernetes cluster administration mastery).

---

## 7. Match Output Structure with Evidence Breakdown

Every opportunity evaluation will output a structured match explanation:
```json
{
  "total_score": 86.5,
  "seniority_compatibility": "compatible",
  "seniority_level_role": "senior",
  "seniority_level_cv": "intermediate_to_senior",
  "breakdown": {
    "skill_score": 23.5,
    "seniority_score": 13.0,
    "eligibility_score": 15.0,
    "freshness_score": 9.5,
    "compensation_score": 8.5,
    "type_score": 10.0,
    "quality_score": 9.0,
    "feasibility_score": 5.0,
    "seniority_penalty": 0.0
  },
  "project_evidence": [
    "PyTorch demonstrated in 'Defect Detection Pipeline' project",
    "YOLO demonstrated in 'Real-Time Edge Vision' project"
  ],
  "transferable_skills": [
    "FastAPI + Docker provides transferable capability for Model Deployment"
  ],
  "missing_skills": ["Triton Inference Server"],
  "positive_reasons": [
    "Published within the last 24 hours (Fresh Verified)",
    "High project evidence overlap in Computer Vision and YOLO",
    "Worldwide remote contract eligible for Egypt with USD payment"
  ],
  "negative_reasons": [
    "Preferred skill 'Triton Inference Server' not present in CV"
  ]
}
```
