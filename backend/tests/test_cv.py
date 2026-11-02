import pytest
from app.intelligence.cv_parser import CVParser
from app.database.session import SessionLocal, init_db
from app.database.repositories.cv_repo import CVRepository
from app.intelligence.matcher import MatchingEngine

SAMPLE_CV_TEXT = """
Mohamed Ahmed
Cairo, Egypt | mohamed@example.com
Senior Computer Vision & AI Engineer

PROFESSIONAL SUMMARY
Experienced AI Engineer with 4 years of expertise in Computer Vision, Deep Learning, and Large Language Models.
Demonstrated success deploying real-time object detection models with YOLO and PyTorch, and building RAG pipelines with LangChain.

TECHNICAL SKILLS
- Programming: Python, C++, SQL
- Frameworks: PyTorch, TensorFlow, OpenCV, Hugging Face
- Domains: Computer Vision, Object Detection, YOLO, RAG, NLP, AI Agents
- Deployment & MLOps: FastAPI, Docker, Kubernetes, AWS, Linux

KEY PROJECTS
Real-Time Industrial Defect Detection
- Developed an automated visual inspection system using YOLOv8 and OpenCV to identify manufacturing flaws.
- Optimized PyTorch model inference using ONNX, achieving 45 FPS and 94% mAP on custom edge devices.
- Deployed REST inference endpoint with FastAPI and Docker.

Multimodal RAG Agent for Document Intelligence
- Built a retrieval-augmented generation system using LangChain, ChromaDB, and OpenAI embeddings.
- Evaluated model responses using custom benchmark datasets.

WORK EXPERIENCE
AI & Computer Vision Engineer | Tech Innovations LLC
2022 - Present | Cairo, Egypt
- Trained custom U-Net and YOLO architectures for video analytics pipelines.
- Integrated FastAPI microservices with Docker Compose for client deployment.
- Collaborated with ML team on model evaluation and data annotation workflows.

Junior Machine Learning Engineer | DataVision Lab
2020 - 2022 | Cairo, Egypt
- Preprocessed large image datasets and built baseline CNN models with PyTorch.
- Conducted model accuracy reviews and error analysis.

EDUCATION
Bachelor of Science in Computer Science | Cairo University | 2020
"""

def test_cv_parser_text_extraction():
    parser = CVParser()
    parsed = parser.parse(SAMPLE_CV_TEXT.encode("utf-8"), "mohamed_cv.txt")

    assert parsed["professional_headline"] is not None
    assert "Computer Vision" in parsed["professional_headline"] or "Mohamed" in parsed["professional_headline"]
    assert parsed["years_of_experience"] >= 3.0
    assert parsed["seniority_level"] in ["intermediate", "senior"]
    assert parsed["has_leadership_experience"] is False

    # Check skills extracted
    tech_skills = parsed["technical_skills"]
    assert any("Yolo" in s for s in tech_skills)
    assert any("Pytorch" in s for s in tech_skills)
    assert any("Opencv" in s for s in tech_skills)
    assert any("Fastapi" in s for s in tech_skills)
    assert any("Docker" in s for s in tech_skills)

    # Check projects extracted
    projects = parsed["projects"]
    assert len(projects) >= 2
    titles = [p["title"] for p in projects]
    assert any("Defect" in t for t in titles)

    # Check skill evidence
    evidence = parsed["skill_evidence"]
    project_evidence = [e for e in evidence if e["evidence_source"] == "project"]
    assert len(project_evidence) >= 2

def test_cv_parser_scanned_pdf_error():
    parser = CVParser()
    # Malformed / empty PDF bytes
    with pytest.raises(ValueError) as exc:
        parser.extract_text(b"not a valid pdf", "scanned.pdf")
    assert "Failed to read PDF document" in str(exc.value)

def test_cv_parser_unsupported_format():
    parser = CVParser()
    with pytest.raises(ValueError) as exc:
        parser.parse(b"some content", "resume.xyz")
    assert "Unsupported file format" in str(exc.value)

def test_cv_repository_lifecycle():
    init_db()
    with SessionLocal() as session:
        repo = CVRepository(session)
        repo.delete_all()
        parser = CVParser()
        parsed = parser.parse(SAMPLE_CV_TEXT.encode("utf-8"), "test_candidate.txt")

        # Save profile
        profile = repo.save_profile(parsed)
        assert profile.id == parsed["id"]
        assert profile.approved is False

        # Get active profile
        active = repo.get_active_profile()
        assert active is not None
        assert active.id == profile.id

        # Update and approve profile
        updated = repo.update_profile(profile.id, {"approved": True, "seniority_level": "senior"})
        assert updated.approved is True
        assert updated.seniority_level == "senior"

        # Delete profile
        deleted = repo.delete_profile(profile.id)
        assert deleted is True

def test_seniority_penalty_engineering_manager():
    """
    Verifies that an 'Engineering Manager' role receives a heavy seniority penalty
    and does NOT receive a 90+ score when evaluated against an IC candidate profile.
    """
    matcher = MatchingEngine()
    cv_profile = {
        "seniority_level": "intermediate",
        "has_leadership_experience": False,
        "technical_skills": ["Python", "PyTorch", "Kubernetes", "Docker", "AWS", "FastAPI"],
        "skill_evidence": [
            {"skill_name": "PyTorch", "evidence_source": "project"},
            {"skill_name": "Docker", "evidence_source": "project"},
        ],
    }

    # Evaluate Engineering Manager role
    res = matcher.score_opportunity(
        domains=["infrastructure_and_containers", "mlops_and_deployment"],
        matched_skills=["Python", "Kubernetes", "Docker", "AWS", "PyTorch"],
        missing_skills=[],
        eligibility_score=100.0,
        egypt_eligibility="eligible",
        hourly_rate_min=50.0,
        hourly_rate_max=70.0,
        description="We are seeking an Engineering Manager to lead our Infrastructure team. Manage 6 engineers, hold 1-on-1s, drive hiring and architecture.",
        title="Engineering Manager, Infrastructure",
        risk_level="low",
        freshness_score=95.0,
        cv_profile=cv_profile,
    )

    # Score should be significantly penalized (<= 60), NOT 90+
    assert res["overall_score"] < 60.0
    assert res["seniority_compatibility"] == "incompatible_leadership"
    assert "Seniority Mismatch" in res["recommendation"]
    assert res["seniority_mismatch_reason"] is not None

def test_seniority_compatibility_cv_engineer():
    """
    Verifies that a matching Computer Vision Engineer role receives high score and compatible status.
    """
    matcher = MatchingEngine()
    cv_profile = {
        "seniority_level": "intermediate",
        "has_leadership_experience": False,
        "technical_skills": ["Python", "PyTorch", "OpenCV", "YOLO", "FastAPI"],
        "skill_evidence": [
            {"skill_name": "PyTorch", "evidence_source": "project"},
            {"skill_name": "YOLO", "evidence_source": "project"},
        ],
    }

    res = matcher.score_opportunity(
        domains=["computer_vision_and_vlms"],
        matched_skills=["PyTorch", "OpenCV", "YOLO", "Python"],
        missing_skills=[],
        eligibility_score=100.0,
        egypt_eligibility="eligible",
        hourly_rate_min=40.0,
        hourly_rate_max=50.0,
        description="Looking for a Computer Vision Engineer to build defect inspection pipelines using YOLO and PyTorch. Remote contract.",
        title="Computer Vision Engineer",
        risk_level="low",
        freshness_score=100.0,
        cv_profile=cv_profile,
    )

    assert res["overall_score"] >= 80.0
    assert res["seniority_compatibility"] == "compatible"
    assert "Match" in res["recommendation"]
    assert res["seniority_mismatch_reason"] is None
