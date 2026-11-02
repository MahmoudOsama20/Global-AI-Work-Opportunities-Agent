import re
from typing import List, Dict, Set
from app.core.config import config_manager

class DomainClassifier:
    """Classifies opportunities into one or more primary technical domains based on skills and keywords."""

    def __init__(self):
        self.profile = config_manager.get_profile()
        self.domains = self.profile.get("domains", {})

    def classify(self, text: str) -> List[str]:
        """Returns a list of matched domain IDs ordered by profile priority."""
        text_lower = text.lower()
        matched_domains: Set[str] = set()

        for domain_id, domain_info in self.domains.items():
            skills = domain_info.get("skills", [])
            for skill in skills:
                # Use word boundaries for short acronyms like YOLO, RAG, VLM, K8s, ViT, NER
                skill_clean = skill.strip().lower()
                if len(skill_clean) <= 4:
                    pattern = rf"\b{re.escape(skill_clean)}\b"
                else:
                    pattern = re.escape(skill_clean)
                    
                if re.search(pattern, text_lower):
                    matched_domains.add(domain_id)
                    break

        # Sort by profile priority
        priority_map = {
            "large_language_models": 1,
            "ai_agents": 1,
            "computer_vision": 2,
            "natural_language_processing": 3,
            "deep_learning_and_ml": 3,
            "ai_training_and_evaluation": 4,
            "mlops_and_deployment": 5,
        }
        
        sorted_domains = sorted(
            list(matched_domains),
            key=lambda d: priority_map.get(d, 99)
        )
        return sorted_domains
