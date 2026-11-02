from typing import List
from app.core.config import config_manager

class DiscoveryQueryGenerator:
    """Generates targeted discovery search queries based on candidate profile and exclusion criteria."""

    def __init__(self):
        self.profile = config_manager.get_profile()

    def generate_queries(self) -> List[str]:
        """Generates a comprehensive list of high-intent search queries."""
        base_queries = [
            "paid AI training jobs worldwide",
            "remote LLM evaluator jobs",
            "Computer Vision freelance projects paid",
            "remote VLM engineer contracts",
            "AI coding evaluator opportunities",
            "paid AI model evaluation platforms",
            "remote NLP engineering contracts",
            "AI research expert networks hiring",
            "ML model deployment freelance projects",
            "Kubernetes AI infrastructure contracts",
            "Arabic AI data annotation jobs -speech -audio",
            "RLHF prompt evaluation platform hire worldwide",
        ]
        return base_queries
