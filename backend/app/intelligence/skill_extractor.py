import re
from typing import List, Tuple, Set
from app.core.config import config_manager

class SkillExtractor:
    """Extracts required and preferred skills from opportunity text and aligns them with user profile skills."""

    def __init__(self):
        self.profile = config_manager.get_profile()
        self.all_profile_skills: List[str] = []
        for domain_info in self.profile.get("domains", {}).values():
            self.all_profile_skills.extend(domain_info.get("skills", []))
        
        # Deduplicate while preserving case
        self.profile_skills_unique = list(dict.fromkeys(self.all_profile_skills))

    def extract_and_match(self, text: str) -> Tuple[List[str], List[str]]:
        """
        Extracts skills found in text and partitions them into:
        (matched_skills: list[str], missing_common_skills: list[str])
        """
        text_lower = text.lower()
        matched: List[str] = []

        for skill in self.profile_skills_unique:
            skill_clean = skill.strip().lower()
            if len(skill_clean) <= 4:
                pattern = rf"\b{re.escape(skill_clean)}\b"
            else:
                pattern = re.escape(skill_clean)
            if re.search(pattern, text_lower):
                matched.append(skill)

        # Detect any specific niche tech mentioned that might be missing from user profile
        niche_tech = [
            "C++", "Rust", "Golang", "Java", "Swift", "C#", ".NET", "PHP",
            "Ruby", "Scala", "Solidity", "AWS SageMaker", "Databricks", "Snowflake",
            "Ray", "TensorRT", "OpenVINO", "Airflow", "Kubeflow"
        ]
        missing_tech: List[str] = []
        for tech in niche_tech:
            pattern = rf"\b{re.escape(tech.lower())}\b"
            if re.search(pattern, text_lower) and tech not in matched:
                missing_tech.append(tech)

        return matched, missing_tech

