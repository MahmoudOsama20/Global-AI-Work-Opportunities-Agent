import io
import re
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from pypdf import PdfReader
from docx import Document

class CVParser:
    """
    Lightweight, production-grade CV intelligence parser.
    Extracts structured professional profile, multi-page text, skill evidence,
    project deliverables, and seniority level from PDF, DOCX, and TXT resumes.
    """

    SKILL_CANONICAL_MAP = {
        # Large Language Models & GenAI
        "rag": "Retrieval-Augmented Generation (RAG)",
        "retrieval augmented generation": "Retrieval-Augmented Generation (RAG)",
        "advanced rag": "Advanced RAG",
        "langchain": "LangChain",
        "langgraph": "LangGraph",
        "llamaindex": "LlamaIndex",
        "llama index": "LlamaIndex",
        "hugging face": "Hugging Face",
        "huggingface": "Hugging Face",
        "transformers": "Transformers",
        "lora": "LoRA",
        "qlora": "QLoRA",
        "fine-tuning": "Model Fine-tuning",
        "prompt engineering": "Prompt Engineering",
        "vector database": "Vector Databases",
        "vector databases": "Vector Databases",
        "chromadb": "ChromaDB",
        "pinecone": "Pinecone",
        "qdrant": "Qdrant",
        "weaviate": "Weaviate",
        "faiss": "FAISS",
        "embeddings": "Embeddings",
        "semantic search": "Semantic Search",
        "vllm": "vLLM",
        "quantization": "Model Quantization",
        "diffusion models": "Diffusion Models",
        "stable diffusion": "Diffusion Models",
        "gan": "GANs",
        "gans": "GANs",
        "vision-language models": "Vision-Language Models",
        "vlm": "Vision-Language Models",
        "vlms": "Vision-Language Models",

        # Computer Vision
        "computer vision": "Computer Vision",
        "cv": "Computer Vision",
        "opencv": "OpenCV",
        "yolo": "YOLO",
        "yolov8": "YOLO",
        "yolov9": "YOLO",
        "yolov10": "YOLO",
        "yolov11": "YOLO",
        "object detection": "Object Detection",
        "image classification": "Image Classification",
        "semantic segmentation": "Semantic Segmentation",
        "instance segmentation": "Instance Segmentation",
        "u-net": "U-Net",
        "unet": "U-Net",
        "deeplabv3+": "DeepLabV3+",
        "deeplab": "DeepLabV3+",
        "vision transformer": "Vision Transformers",
        "vision transformers": "Vision Transformers",
        "vit": "Vision Transformers",
        "video understanding": "Video Understanding",
        "image processing": "Image Processing",

        # NLP
        "natural language processing": "Natural Language Processing",
        "nlp": "Natural Language Processing",
        "named entity recognition": "Named Entity Recognition",
        "ner": "Named Entity Recognition",
        "text classification": "Text Classification",
        "sentiment analysis": "Sentiment Analysis",
        "arabic nlp": "Arabic NLP",
        "multilingual nlp": "Multilingual NLP",

        # AI Agents
        "ai agent": "AI Agents",
        "ai agents": "AI Agents",
        "agentic ai": "AI Agents",
        "multi-agent": "Multi-Agent Systems",
        "multi-agent systems": "Multi-Agent Systems",
        "tool calling": "Tool Calling",
        "function calling": "Function Calling",

        # Frameworks & Libraries
        "pytorch": "PyTorch",
        "tensorflow": "TensorFlow",
        "keras": "Keras",
        "scikit-learn": "Scikit-Learn",
        "sklearn": "Scikit-Learn",
        "pandas": "Pandas",
        "numpy": "NumPy",

        # MLOps & Deployment
        "fastapi": "FastAPI",
        "flask": "Flask",
        "docker": "Docker",
        "docker compose": "Docker Compose",
        "kubernetes": "Kubernetes",
        "k8s": "Kubernetes",
        "helm": "Helm",
        "mlflow": "MLflow",
        "onnx": "ONNX",
        "triton": "Triton Inference Server",
        "aws": "AWS",
        "gcp": "GCP",
        "azure": "Azure",
        "ci/cd": "CI/CD",
        "model deployment": "Model Deployment",
        "mlops": "MLOps",

        # AI Evaluation & Training
        "rlhf": "RLHF",
        "human feedback": "Human Feedback for LLMs",
        "model evaluation": "AI Model Evaluation",
        "red teaming": "AI Red Teaming",
        "data annotation": "Data Annotation",
        "dataset curation": "Dataset Curation",
    }

    def extract_text(self, file_bytes: bytes, filename: str) -> str:
        """
        Extracts raw textual content from PDF, DOCX, or TXT format.
        Preserves page sequences and line breaks.
        """
        ext = filename.lower().split(".")[-1]

        if ext == "pdf":
            try:
                reader = PdfReader(io.BytesIO(file_bytes))
                pages_text = []
                for page in reader.pages:
                    txt = page.extract_text() or ""
                    pages_text.append(txt)
                full_text = "\n\n".join(pages_text).strip()
                if len(full_text) < 30:
                    raise ValueError(
                        "Uploaded PDF has no extractable text. Scanned or image-only documents require OCR."
                    )
                return full_text
            except Exception as e:
                if "OCR" in str(e):
                    raise
                raise ValueError(f"Failed to read PDF document: {e}")

        elif ext == "docx":
            try:
                doc = Document(io.BytesIO(file_bytes))
                lines = []
                for p in doc.paragraphs:
                    if p.text.strip():
                        lines.append(p.text.strip())
                for table in doc.tables:
                    for row in table.rows:
                        row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                        if row_text:
                            lines.append(row_text)
                full_text = "\n".join(lines).strip()
                if len(full_text) < 30:
                    raise ValueError("Uploaded DOCX appears to be empty or unreadable.")
                return full_text
            except Exception as e:
                raise ValueError(f"Failed to read DOCX document: {e}")

        elif ext == "txt":
            try:
                return file_bytes.decode("utf-8").strip()
            except UnicodeDecodeError:
                return file_bytes.decode("latin-1", errors="ignore").strip()

        else:
            raise ValueError(f"Unsupported file format '.{ext}'. Supported formats are: PDF, DOCX, TXT.")

    def segment_sections(self, text: str) -> Dict[str, str]:
        """
        Detects common section headers and segments the CV into functional blocks.
        """
        section_patterns = {
            "summary": r"(?i)^(?:professional\s+summary|summary|profile|about\s+me|career\s+objective)\b",
            "skills": r"(?i)^(?:technical\s+skills|core\s+competencies|skills\s+and\s+tools|skills|technologies)\b",
            "projects": r"(?i)^(?:key\s+projects|selected\s+projects|projects|portfolio)\b",
            "experience": r"(?i)^(?:work\s+experience|professional\s+experience|employment\s+history|experience)\b",
            "education": r"(?i)^(?:education|academic\s+background|degrees)\b",
            "certifications": r"(?i)^(?:certifications?|licenses|courses)\b",
            "languages": r"(?i)^(?:languages?|spoken\s+languages)\b",
        }

        lines = text.split("\n")
        sections: Dict[str, List[str]] = {
            "header": [],
            "summary": [],
            "skills": [],
            "projects": [],
            "experience": [],
            "education": [],
            "certifications": [],
            "languages": [],
            "other": [],
        }

        current_sec = "header"

        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                continue

            # Check if this line looks like a header
            matched_sec = None
            for sec_name, pattern in section_patterns.items():
                if re.match(pattern, trimmed) and len(trimmed) < 40:
                    matched_sec = sec_name
                    break

            if matched_sec:
                current_sec = matched_sec
                continue

            sections[current_sec].append(trimmed)

        return {k: "\n".join(v) for k, v in sections.items()}

    def extract_skills_with_evidence(
        self,
        full_text: str,
        segmented: Dict[str, str],
        projects: List[Dict[str, Any]],
        experience: List[Dict[str, Any]],
    ) -> Tuple[List[str], List[str], List[Dict[str, Any]]]:
        """
        Extracts skills and attributes evidence sources (project, employment, skills_list, inferred).
        """
        extracted_skills = set()
        normalized_skills = set()
        skill_evidence = []

        full_lower = full_text.lower()
        skills_sec_lower = segmented.get("skills", "").lower()
        projects_sec_lower = segmented.get("projects", "").lower()
        exp_sec_lower = segmented.get("experience", "").lower()

        # Check project-level mentions first
        for proj in projects:
            proj_text = f"{proj.get('title', '')} {proj.get('description', '')} {' '.join(proj.get('technologies', []))}".lower()
            for raw_alias, canonical in self.SKILL_CANONICAL_MAP.items():
                pattern = r"\b" + re.escape(raw_alias) + r"\b"
                if re.search(pattern, proj_text):
                    extracted_skills.add(raw_alias.capitalize())
                    normalized_skills.add(canonical)
                    skill_evidence.append({
                        "skill_name": raw_alias.capitalize(),
                        "normalized_name": canonical,
                        "evidence_source": "project",
                        "associated_project": proj.get("title"),
                        "context_snippet": proj.get("description", "")[:120],
                        "confidence": 0.95,
                    })

        # Check employment-level mentions
        for exp in experience:
            exp_text = f"{exp.get('title', '')} {' '.join(exp.get('responsibilities', []))}".lower()
            for raw_alias, canonical in self.SKILL_CANONICAL_MAP.items():
                pattern = r"\b" + re.escape(raw_alias) + r"\b"
                if re.search(pattern, exp_text) and canonical not in normalized_skills:
                    extracted_skills.add(raw_alias.capitalize())
                    normalized_skills.add(canonical)
                    skill_evidence.append({
                        "skill_name": raw_alias.capitalize(),
                        "normalized_name": canonical,
                        "evidence_source": "employment",
                        "associated_project": exp.get("company"),
                        "context_snippet": f"Role: {exp.get('title')}",
                        "confidence": 0.85,
                    })

        # Check general skills section
        for raw_alias, canonical in self.SKILL_CANONICAL_MAP.items():
            pattern = r"\b" + re.escape(raw_alias) + r"\b"
            if re.search(pattern, skills_sec_lower) and canonical not in normalized_skills:
                extracted_skills.add(raw_alias.capitalize())
                normalized_skills.add(canonical)
                skill_evidence.append({
                    "skill_name": raw_alias.capitalize(),
                    "normalized_name": canonical,
                    "evidence_source": "skills_list",
                    "associated_project": None,
                    "context_snippet": "Listed in Technical Skills section",
                    "confidence": 0.65,
                })

        # Fallback search across full text
        for raw_alias, canonical in self.SKILL_CANONICAL_MAP.items():
            pattern = r"\b" + re.escape(raw_alias) + r"\b"
            if re.search(pattern, full_lower) and canonical not in normalized_skills:
                extracted_skills.add(raw_alias.capitalize())
                normalized_skills.add(canonical)
                skill_evidence.append({
                    "skill_name": raw_alias.capitalize(),
                    "normalized_name": canonical,
                    "evidence_source": "inferred",
                    "associated_project": None,
                    "context_snippet": "Mentioned in document body",
                    "confidence": 0.50,
                })

        return sorted(list(extracted_skills)), sorted(list(normalized_skills)), skill_evidence

    def extract_projects(self, project_text: str) -> List[Dict[str, Any]]:
        """
        Extracts structured project blocks, technologies, metrics, and problems solved.
        """
        projects = []
        if not project_text.strip():
            return projects

        blocks = re.split(r"\n(?=[A-Z0-9][A-Za-z0-9\s\-_:]{3,80}(?:\n|:|-|\())", project_text)

        for b in blocks:
            lines = [l.strip() for l in b.split("\n") if l.strip()]
            if not lines:
                continue

            title = lines[0].strip(":- ")
            desc = " ".join(lines[1:])

            # Extract metrics (e.g. 95%, 30fps, 40ms, 10k users)
            metrics = None
            metric_match = re.search(r"(\b\d+(?:\.\d+)?%\b|\b\d+\s*fps\b|\b\d+\s*ms\b|\b\d+k\b)", desc, re.I)
            if metric_match:
                metrics = metric_match.group(0)

            # Extract technologies used in project
            found_techs = []
            for raw_alias in self.SKILL_CANONICAL_MAP.keys():
                if re.search(r"\b" + re.escape(raw_alias) + r"\b", desc.lower()):
                    found_techs.append(raw_alias.capitalize())

            # Domain detection
            domain = "Machine Learning"
            if any(t in desc.lower() for t in ["yolo", "opencv", "vision", "segmentation", "detection"]):
                domain = "Computer Vision"
            elif any(t in desc.lower() for t in ["rag", "llm", "langchain", "embeddings", "agent"]):
                domain = "Large Language Models & Agents"
            elif any(t in desc.lower() for t in ["fastapi", "docker", "kubernetes", "mlops", "serving"]):
                domain = "AI Deployment & MLOps"

            projects.append({
                "title": title[:100],
                "domain": domain,
                "technologies": list(set(found_techs)),
                "description": desc[:500],
                "metrics": metrics,
                "responsibilities": None,
            })

        return projects

    def extract_experience_and_seniority(
        self, exp_text: str, full_text: str
    ) -> Tuple[List[Dict[str, Any]], Optional[float], str, bool]:
        """
        Parses employment history, computes years of experience,
        evaluates seniority level, and checks for management/leadership background.
        """
        experience_items = []
        has_leadership = False

        if exp_text.strip():
            blocks = re.split(r"\n(?=[A-Z][A-Za-z0-9\s\-_,]{3,50}\s*(?:\|\s*|\-\s*|\(\d{4}))", exp_text)
            for b in blocks:
                lines = [l.strip() for l in b.split("\n") if l.strip()]
                if not lines:
                    continue
                first_line = lines[0]
                resp = lines[1:]

                # Check if leadership role
                if any(term in first_line.lower() for term in ["manager", "lead", "director", "head of", "vp "]):
                    has_leadership = True

                experience_items.append({
                    "title": first_line[:100],
                    "company": None,
                    "duration": None,
                    "is_current": "present" in first_line.lower(),
                    "responsibilities": resp[:5],
                    "technologies": [],
                })

        # Calculate years of experience from year patterns (e.g. 2021 - 2024)
        year_matches = re.findall(r"\b(20[0-2][0-9])\b", exp_text or full_text)
        years_exp = 3.0  # sensible default intermediate
        if year_matches:
            years = [int(y) for y in year_matches]
            min_year = min(years)
            max_year = max(years)
            current_year = 2026
            diff = max(1, current_year - min_year)
            years_exp = min(15.0, float(diff))

        # Determine seniority level
        if has_leadership:
            seniority_level = "lead"
        elif years_exp >= 6.0:
            seniority_level = "senior"
        elif years_exp >= 2.5:
            seniority_level = "intermediate"
        elif years_exp >= 1.0:
            seniority_level = "junior"
        else:
            seniority_level = "entry"

        # Explicit check for people management in full text
        if any(term in full_text.lower() for term in ["engineering manager", "managed a team of", "direct reports", "head of engineering"]):
            has_leadership = True
            seniority_level = "manager"

        return experience_items, years_exp, seniority_level, has_leadership

    def parse(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Full end-to-end execution of the Deep CV Intelligence extraction pipeline.
        Returns a structured dictionary matching CVProfileBase.
        """
        raw_text = self.extract_text(file_bytes, filename)
        segmented = self.segment_sections(raw_text)

        # Header & Summary
        header_lines = [l.strip() for l in segmented.get("header", "").split("\n") if l.strip()]
        headline = header_lines[0] if header_lines else "AI Engineer & Computer Vision Specialist"
        summary = segmented.get("summary", "") or (header_lines[1] if len(header_lines) > 1 else None)

        # Projects
        projects = self.extract_projects(segmented.get("projects", ""))

        # Experience & Seniority
        experience, years_exp, seniority, has_leadership = self.extract_experience_and_seniority(
            segmented.get("experience", ""), raw_text
        )

        # Skills & Evidence
        extracted_skills, normalized_skills, skill_evidence = self.extract_skills_with_evidence(
            raw_text, segmented, projects, experience
        )

        # Confidence calculation
        confidence = 60.0
        if len(raw_text) > 500:
            confidence += 15.0
        if projects:
            confidence += 15.0
        if len(extracted_skills) >= 5:
            confidence += 10.0
        confidence = min(100.0, confidence)

        profile_id = hashlib.sha256(raw_text.encode()).hexdigest()[:24]

        return {
            "id": profile_id,
            "filename": filename,
            "file_type": filename.lower().split(".")[-1],
            "file_size_bytes": len(file_bytes),
            "raw_text": raw_text,
            "professional_headline": headline[:256],
            "career_summary": summary[:1000] if summary else None,
            "years_of_experience": years_exp,
            "seniority_level": seniority,
            "has_leadership_experience": has_leadership,
            "technical_skills": extracted_skills,
            "normalized_skills": normalized_skills,
            "skill_evidence": skill_evidence,
            "projects": projects,
            "employment_history": experience,
            "education": [],
            "certifications": [],
            "languages": ["English", "Arabic"],
            "extraction_confidence": confidence,
            "approved": False,
            "version": 1,
        }
