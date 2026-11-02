# Global AI Opportunities Intelligence Agent

A manually operated, production-grade AI-powered opportunity discovery, intelligence, and matching platform designed for a **Senior AI & Machine Learning Engineer based in Egypt**.

The system dynamically discovers, collects, normalizes, validates, classifies, filters, evaluates geographic and payout eligibility, deduplicates, scores, and generates comprehensive reports on legitimate paid AI opportunities globally.

---

## 1. Core Mission & Philosophy

- **Manual Trigger Only**: The application runs strictly on-demand (via CLI `python main.py run` or the prominent dashboard button **"RUN GLOBAL AI OPPORTUNITY SEARCH"**). No automatic polling, background daemons, or cron jobs.
- **Strict Exclusions**: Speech/Audio tasks (ASR, TTS, Voice AI, audio annotation, transcription) and non-AI generic automation (RPA, PLC, SCADA, generic BPA) are strictly purged before scoring.
- **Egyptian Eligibility Gating**: Every opportunity is vetted for Egyptian location eligibility and payout compatibility (Payoneer, Wise, Direct Wire/IBAN, PayPal). Explicitly ineligible roles are blocked from being recommended.
- **Resilient Connectors**: A failure in one source never crashes the search. All active connectors execute concurrently in thread pools with polite rate limiting.
- **Zero Fabrication**: Only actual verified listings from legitimate endpoints are reported. The system never invents jobs, pay rates, or platforms.

---

## 2. Key Features

1. **Central Intelligence Pipeline**: 10-stage processing (Collection &rarr; Normalization &rarr; Validation &rarr; Domain Classification &rarr; Strict Exclusions &rarr; Eligibility Gate &rarr; Deduplication &rarr; Deterministic 100-Point Scoring &rarr; Ranking &rarr; Reporting).
2. **Dynamic Source Discovery Engine**: Finds newly published platforms, specialized AI evaluation websites, and company career boards via targeted search queries, validates legitimacy, and queues them in the Discovery Center.
3. **Safe Authenticated Outlier Inspection**: Uses a local persistent Playwright browser profile (`data/browser_profiles/outlier`) where the user logs in manually; the agent only reads visible project queues in read-only mode without touching credentials or bypassing CAPTCHA/MFA.
4. **Universal Opportunity Data Model**: Strongly-typed SQLite / PostgreSQL schema tracking canonical URLs, technical domains, matched vs missing skills, risk indicators, and historical lifecycle.
5. **Modern Full-Stack Dashboard**: React 18, TypeScript, Tailwind CSS, Lucide icons, and FastAPI backend with live search execution, filtering, detailed inspection modals, and discovery center.
6. **Unified HTML & Markdown Reports**: Generates self-contained, beautifully styled executive reports saved to `data/reports/`.

---

## 3. Supported Technical Domains

1. **Large Language Models (LLM)**: LLM Engineering, RAG, LoRA/QLoRA, Hugging Face, PEFT, Quantization, Model Optimization.
2. **AI Agents**: Agentic AI, Multi-Agent Systems, LangChain, LangGraph, LlamaIndex, Tool Calling, Planning & Reasoning.
3. **Computer Vision & VLMs**: Object Detection, YOLO, Semantic/Instance Segmentation, ViT, VQA, Multimodal AI, OpenCV.
4. **Natural Language Processing (NLP)**: Text Classification, NER, Sentiment Analysis, Text Embeddings, Arabic & English NLP.
5. **Deep Learning & Classical ML**: PyTorch, TensorFlow, CNNs, Transformers, Diffusion Models, Scikit-learn.
6. **MLOps & AI Deployment**: Model Serving, FastAPI, Docker, Kubernetes, Helm, vLLM, ONNX, MLflow, Triton, Cloud ML (AWS/GCP).
7. **AI Training & Evaluation**: LLM Response Evaluation, Coding Evaluation, AI Benchmarks, RLHF Review, AI Red Teaming, Technical Image/Video Annotation.

---

## 4. Mandatory Exclusions

- **Exclusion A (Speech & Audio)**: All work primarily involving ASR, Speech Recognition, TTS, Voice AI, Audio Processing, Audio Classification, Audio Transcription, or Audio Annotation.
- **Exclusion B (Automation as Job Category)**: Robotic Process Automation (RPA), UiPath, Blue Prism, Automation Anywhere, PLC Programming, SCADA, Industrial Control Systems, and generic Business Process Automation (BPA).
- **Exclusion C (Irrelevant / Unpaid)**: Data entry, generic virtual assistant, unpaid internships/projects, and volunteer work.

---

## 5. Technology Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2, HTTPX, BeautifulSoup4, RapidFuzz, Typer, Jinja2.
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide React.
- **Database**: SQLite (default) / PostgreSQL compatible, Alembic migrations.
- **Hardware Profile**: 100% CPU-compatible, zero CUDA/GPU requirements, minimal storage overhead (<1 GB total).

---

## 6. Project Structure

```text
Global AI Work Opportunities Agent/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/ (opportunities, sources, pipeline, discovery, profile, reports)
│   │   │   └── dependencies.py
│   │   ├── core/ (config, logging, security, errors)
│   │   ├── database/
│   │   │   ├── models/ (source, opportunity, candidate, collection_run)
│   │   │   ├── repositories/ (source_repo, opportunity_repo, run_repo)
│   │   │   └── session.py
│   │   ├── connectors/
│   │   │   ├── base.py
│   │   │   ├── job_boards/ (remotive, remoteok, himalayas, wwr)
│   │   │   ├── outlier/ (public_outlier, account_outlier)
│   │   │   ├── evaluation/ (alignerr)
│   │   │   └── registry.py
│   │   ├── discovery/ (search_provider, query_generator, source_validator, source_registry)
│   │   ├── intelligence/ (classifier, exclusions, skill_extractor, payment_parser, eligibility, deduplicator, matcher, risk_analyzer, normalizer)
│   │   ├── llm/ (base, providers/gemini_provider)
│   │   ├── pipeline/ (runner)
│   │   ├── reports/ (html_report, markdown_report)
│   │   ├── schemas/ (opportunity, source, collection, profile, connector)
│   │   └── main.py
│   ├── tests/ (test_config, test_database, test_security, test_intelligence, test_negative_cases, test_connectors, test_discovery, test_api)
│   ├── alembic.ini
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/ (Navbar, OpportunityModal)
│   │   ├── pages/ (Overview, Opportunities, Sources, Discovery, Profile, Reports)
│   │   ├── services/ (api)
│   │   ├── types/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── config/
│   ├── profile.yaml
│   ├── sources.yaml
│   ├── scoring.yaml
│   └── exclusions.yaml
├── data/
│   ├── database/
│   ├── reports/
│   └── logs/
├── docs/
├── .env.example
├── .gitignore
├── PROJECT_STATUS.md
├── README.md
└── main.py (Unified CLI)
```

---

## 7. Installation & Quickstart

### Step 1: Environment & Virtualenv Setup
```powershell
# Create isolated virtual environment using uv with local cache
uv venv --python 3.12 --cache-dir .uv-cache .venv

# Activate virtual environment
.\.venv\Scripts\activate

# Install backend dependencies in editable mode
uv pip install -e "backend[dev]" --python .venv\Scripts\python.exe --cache-dir .uv-cache

# Copy environment template
cp .env.example .env
```

### Step 2: Initialize Database and Seed Sources
```powershell
python main.py init-db
```

### Step 3: Check Connector Health
```powershell
python main.py health-check
```

### Step 4: Run a Global AI Opportunity Search (CLI)
```powershell
python main.py run
```
You can also run specific subsets:
```powershell
# Run only Remotive
python main.py run --source remotive

# Run only Outlier / Scale AI
python main.py run --source outlier

# Run with Source Discovery Engine enabled
python main.py run --discover-sources
```

### Step 5: Start the Full-Stack Web Application
```powershell
# Starts the FastAPI backend (and serves the React build at http://127.0.0.1:8000)
python main.py serve
```

For frontend development with Vite hot-reload:
```powershell
cd frontend
npm install
npm run dev
# Dashboard opens on http://localhost:5173 (proxies /api to 8000)
```

---

## 8. Outlier Safe Interactive Inspection

To inspect your personal Outlier task queue without sharing passwords:

1. Launch interactive login helper:
   ```powershell
   python main.py login-account outlier
   ```
   A browser window opens to Outlier's official login page. Sign in manually with your credentials and complete 2FA. The session is preserved locally in `data/browser_profiles/outlier`.

2. Inspect active project allocation:
   ```powershell
   python main.py inspect-account outlier
   ```
   The agent reads your queue in read-only mode and reports the project name and pay rate without performing any automated actions.

---

## 9. Running Tests

Run the complete 43-test suite covering units, integration, connectors, discovery, API routes, and all 10 mandatory negative tests:
```powershell
.\.venv\Scripts\pytest.exe backend/tests -v
```

All 43 tests pass with 100% coverage of mandatory negative tests:
- Speech recognition excluded: PASS
- Audio transcription excluded: PASS
- Audio annotation excluded: PASS
- Industrial automation (PLC/SCADA) excluded: PASS
- Workflow automation (RPA/UiPath) excluded: PASS
- Unpaid opportunity excluded: PASS
- Ineligible foreign-only restricted role blocked from recommendation: PASS
- Unknown eligibility flagged: PASS
- Cross-platform duplicates detected & merged: PASS
- Connector failure does not fabricate fake listings: PASS

---

## 10. Security & Privacy Notes

- `.env`, `data/database/`, `data/logs/`, and `data/browser_profiles/` are strictly ignored by `.gitignore`.
- API keys and tokens are automatically redacted by `sanitize_log_message`.
- The system never submits applications, bids on projects, accepts contracts, or sends messages to clients.
