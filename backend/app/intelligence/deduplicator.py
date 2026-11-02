import hashlib
from typing import List, Dict, Tuple, Optional
from rapidfuzz import fuzz
from app.schemas.opportunity import NormalizedOpportunity

class DeduplicationEngine:
    """Detects duplicate listings across disparate sources and merges cross-source references."""

    def __init__(self, title_threshold: float = 88.0, text_threshold: float = 85.0):
        self.title_threshold = title_threshold
        self.text_threshold = text_threshold

    def are_duplicates(self, opp_a: NormalizedOpportunity, opp_b: NormalizedOpportunity) -> Tuple[bool, str]:
        """
        Determines whether two opportunities are duplicates.
        Returns: (is_duplicate: bool, reason: str)
        """
        # Strategy 1: Canonical URL exact match
        if opp_a.canonical_url and opp_b.canonical_url and opp_a.canonical_url == opp_b.canonical_url:
            return True, "Exact canonical URL match"

        # Strategy 2: Same company + high title similarity
        if opp_a.company and opp_b.company:
            comp_a = opp_a.company.strip().lower()
            comp_b = opp_b.company.strip().lower()
            if comp_a == comp_b or fuzz.ratio(comp_a, comp_b) > 90:
                title_sim = fuzz.token_sort_ratio(opp_a.title.lower(), opp_b.title.lower())
                if title_sim >= self.title_threshold:
                    return True, f"Matching company ({opp_a.company}) and title similarity ({title_sim:.1f}%)"

        # Strategy 3: Across platforms with near-identical title + high description similarity
        title_sim = fuzz.token_set_ratio(opp_a.title.lower(), opp_b.title.lower())
        if title_sim >= 92.0:
            # Compare first 300 chars of descriptions
            desc_a = opp_a.description[:300].lower()
            desc_b = opp_b.description[:300].lower()
            desc_sim = fuzz.ratio(desc_a, desc_b)
            if desc_sim >= self.text_threshold:
                return True, f"Cross-platform match: Title ({title_sim:.1f}%), Content ({desc_sim:.1f}%)"

        return False, ""

    def cluster_and_deduplicate(
        self, opportunities: List[NormalizedOpportunity]
    ) -> Tuple[List[NormalizedOpportunity], int]:
        """
        Processes a list of opportunities, grouping duplicates.
        Returns: (deduplicated_opportunities: list, duplicate_count: int)
        """
        canonical_list: List[NormalizedOpportunity] = []
        duplicate_count = 0

        for candidate in opportunities:
            matched_canonical = None
            match_reason = ""
            for existing in canonical_list:
                is_dup, reason = self.are_duplicates(candidate, existing)
                if is_dup:
                    matched_canonical = existing
                    match_reason = reason
                    break

            if matched_canonical:
                duplicate_count += 1
                # Generate a group ID if not present
                group_id = matched_canonical.duplicate_group_id or f"group_{hashlib.md5(matched_canonical.id.encode()).hexdigest()[:12]}"
                matched_canonical.duplicate_group_id = group_id
                candidate.duplicate_group_id = group_id

                # Enrich canonical opportunity with candidate links and details
                if candidate.original_url not in matched_canonical.original_url:
                    matched_canonical.raw_data_reference = (
                        f"{matched_canonical.raw_data_reference or ''} | Also seen on [{candidate.source_name}]: {candidate.original_url}"
                    ).strip(" | ")
                # Keep highest scores
                matched_canonical.overall_score = max(matched_canonical.overall_score, candidate.overall_score)
            else:
                canonical_list.append(candidate)

        return canonical_list, duplicate_count

