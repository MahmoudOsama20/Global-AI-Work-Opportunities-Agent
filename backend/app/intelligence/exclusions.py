import re
from typing import Tuple, Optional, List
from app.core.config import config_manager

class ExclusionEngine:
    """Evaluates opportunities against mandatory strict exclusions.
    
    Exclusions:
    1. Speech and Audio in all forms (ASR, TTS, Voice AI, Audio Transcription/Annotation, etc.)
    2. Automation as a Job Category (RPA, Industrial, PLC, SCADA, Workflow/BPA, Test Automation)
    3. Irrelevant / Unpaid work (Data entry, virtual assistant, unpaid internships)
    """

    def __init__(self):
        self._load_rules()

    def _load_rules(self):
        config = config_manager.get_exclusions()
        self.speech_keywords = [k.lower() for k in config.get("speech_and_audio", {}).get("keywords", [])]
        self.automation_keywords = [k.lower() for k in config.get("automation_as_job_category", {}).get("keywords", [])]
        self.automation_exceptions = [k.lower() for k in config.get("automation_as_job_category", {}).get("exceptions", [])]
        self.irrelevant_keywords = [k.lower() for k in config.get("irrelevant_work", {}).get("keywords", [])]

    def evaluate(self, title: str, description: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Evaluates title and description for strict exclusions.
        Returns: (is_excluded: bool, category: str | None, reason: str | None)
        """
        text_lower = f"{title.lower()} {description.lower()}"

        # 1. Check Speech & Audio (Mandatory - zero tolerance)
        for kw in self.speech_keywords:
            pattern = rf"\b{re.escape(kw)}\b"
            if re.search(pattern, text_lower):
                return True, "speech_and_audio", f"Contains excluded speech/audio keyword: '{kw}'"

        # 2. Check Automation as Job Category (RPA, SCADA, PLC, BPA, Test Automation)
        for kw in self.automation_keywords:
            pattern = rf"\b{re.escape(kw)}\b"
            if re.search(pattern, text_lower):
                # Check for explicit AI Agent / MLOps exceptions
                has_exception = any(exc in text_lower for exc in self.automation_exceptions)
                # If the title itself is generic automation (e.g. 'Automation Engineer', 'RPA Developer', 'PLC Programmer'), exclude regardless
                title_has_kw = bool(re.search(pattern, title.lower()))
                if title_has_kw or not has_exception:
                    return True, "automation_job_category", f"Contains excluded non-AI automation keyword: '{kw}'"

        # 3. Check Irrelevant and Unpaid work
        for kw in self.irrelevant_keywords:
            pattern = rf"\b{re.escape(kw)}\b"
            if re.search(pattern, text_lower):
                return True, "irrelevant_or_unpaid", f"Contains excluded irrelevant/unpaid keyword: '{kw}'"

        # Check explicit unpaid markers
        unpaid_markers = ["unpaid", "volunteer", "$0", "no compensation", "for exposure", "uncompensated"]
        for marker in unpaid_markers:
            if re.search(rf"\b{re.escape(marker)}\b", title.lower()):
                return True, "unpaid", f"Explicitly marked as unpaid: '{marker}' in title"

        return False, None, None
