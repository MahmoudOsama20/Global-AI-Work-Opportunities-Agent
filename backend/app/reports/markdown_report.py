from datetime import datetime, timezone
from typing import List, Dict, Any
from pathlib import Path
from app.schemas.opportunity import NormalizedOpportunity
from app.core.config import DATA_DIR

class MarkdownReportGenerator:
    """Generates structured, standalone Markdown intelligence reports."""

    def generate(
        self,
        run_id: str,
        metrics: Dict[str, Any],
        opportunities: List[NormalizedOpportunity],
        excluded_summary: Dict[str, int],
        sources_status: List[Dict[str, Any]],
        new_sources: List[Dict[str, Any]] = None,
        outlier_account_status: Dict[str, Any] = None,
    ) -> Path:
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        report_dir = DATA_DIR / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / f"report_{run_id}.md"

        lines = []
        lines.append(f"# Global AI Opportunities Intelligence Report")
        lines.append(f"**Run Identifier**: `{run_id}`  ")
        lines.append(f"**Generated**: {now_str}  ")
        lines.append(f"**Target Candidate Profile**: Senior AI & Machine Learning Engineer (Location: Egypt)  \n")
        lines.append("---\n")

        # 1. Executive Summary
        lines.append("## 1. Executive Summary\n")
        lines.append("| Metric | Value |")
        lines.append("|---|---:|")
        lines.append(f"| Sources Attempted | {metrics.get('sources_attempted', 0)} |")
        lines.append(f"| Sources Succeeded | {metrics.get('sources_succeeded', 0)} |")
        lines.append(f"| Sources Failed | {metrics.get('sources_failed', 0)} |")
        lines.append(f"| Total Opportunities Collected | {metrics.get('total_collected', 0)} |")
        lines.append(f"| New Opportunities | {metrics.get('new_count', 0)} |")
        lines.append(f"| Duplicate Opportunities | {metrics.get('duplicate_count', 0)} |")
        lines.append(f"| Relevant AI Opportunities | {metrics.get('relevant_count', 0)} |")
        lines.append(f"| Published Within 24 Hours | {metrics.get('fresh_24h', 0)} |")
        lines.append(f"| Published Within 7 Days | {metrics.get('fresh_7d', 0)} |")
        lines.append(f"| Unknown Publication Date | {metrics.get('unknown_date', 0)} |")
        lines.append(f"| Excellent Matches (Score ≥ 90) | {metrics.get('excellent_matches', 0)} |")
        lines.append(f"| Strong Matches (Score 80-89) | {metrics.get('strong_matches', 0)} |")
        lines.append(f"| Verified / Likely Eligible in Egypt | {metrics.get('eligible_in_egypt', 0)} |")
        lines.append(f"| Requires Eligibility Verification | {metrics.get('unverified_eligibility', 0)} |\n")

        # 2. Top Recommended Opportunities
        lines.append("## 2. Top Recommended Opportunities (Apply First)\n")
        recommended = [
            opp for opp in opportunities
            if opp.overall_score >= 70.0 and opp.egypt_eligibility != "not_eligible"
        ]
        recommended.sort(key=lambda x: x.overall_score, reverse=True)

        if not recommended:
            lines.append("*No opportunities currently meet the recommendation threshold (Score ≥ 70 with valid Egypt eligibility).*\n")
        else:
            for opp in recommended[:15]:
                from app.intelligence.freshness import human_readable_freshness, to_cairo_time
                fresh_str = human_readable_freshness(opp.posted_at)
                cairo_str = to_cairo_time(opp.posted_at)
                lines.append(f"### [{opp.overall_score:.1f}/100] {opp.title} — {opp.company or 'Client'}")
                lines.append(f"- **Source**: {opp.source_name} (`{opp.source_id}`)")
                lines.append(f"- **Published**: `{fresh_str}` ({cairo_str}) | Freshness Status: `{opp.freshness_status}`")
                lines.append(f"- **Seniority Alignment**: `{opp.seniority_compatibility or 'compatible'}`")
                lines.append(f"- **Original Application Link**: [{opp.original_url}]({opp.original_url})")
                lines.append(f"- **Payment Model**: {opp.payment_model.upper()} | **Compensation**: {opp.payment_details or 'Not disclosed'}")
                lines.append(f"- **Egypt Eligibility**: `{opp.egypt_eligibility.replace('_', ' ').upper()}` ({opp.location or 'Remote'})")
                lines.append(f"- **Matched Skills**: {', '.join(opp.required_skills[:6]) if opp.required_skills else 'General AI'}")
                if opp.missing_skills:
                    lines.append(f"- **Additional Requirements**: {', '.join(opp.missing_skills[:4])}")
                lines.append(f"- **Risk Level**: `{opp.risk_level.upper()}` — {opp.risk_explanation}")
                lines.append(f"- **Recommendation**: **{opp.recommendation}**")
                lines.append(f"- **Why it matches**: {opp.match_explanation}\n")

        # 3. AI Training and Evaluation Opportunities
        lines.append("## 3. AI Training & Evaluation Opportunities\n")
        eval_opps = [
            opp for opp in opportunities
            if "ai_training_and_evaluation" in opp.technical_domains or opp.category == "ai_training_and_evaluation"
        ]
        if not eval_opps:
            lines.append("*No specialized AI training / model evaluation roles found in this run.*\n")
        else:
            for opp in eval_opps:
                lines.append(f"- **{opp.title}** ({opp.source_name}) — Score: `{opp.overall_score:.1f}` | Egypt: `{opp.egypt_eligibility}` | [Link]({opp.original_url})")
            lines.append("")

        # 4. Core Engineering Opportunities
        lines.append("## 4. Core AI & Machine Learning Engineering Roles\n")
        eng_opps = [
            opp for opp in opportunities
            if any(d in opp.technical_domains for d in ["large_language_models", "computer_vision", "ai_agents", "mlops_and_deployment"])
        ]
        if not eng_opps:
            lines.append("*No core engineering roles found in this run.*\n")
        else:
            for opp in eng_opps[:20]:
                domains_str = ", ".join(opp.technical_domains)
                lines.append(f"- **{opp.title}** at *{opp.company or 'Direct Client'}* — `{domains_str}` | Score: `{opp.overall_score:.1f}` | [Link]({opp.original_url})")
            lines.append("")

        # 5. Outlier Status
        lines.append("## 5. Outlier Platform Status\n")
        if outlier_account_status:
            lines.append(f"- **Account Authenticated**: `{outlier_account_status.get('is_authenticated')}`")
            lines.append(f"- **Active Project Allocation**: `{outlier_account_status.get('active_project')}`")
            lines.append(f"- **Status Notes**: {outlier_account_status.get('message')}\n")
        else:
            outlier_public_count = sum(1 for o in opportunities if o.source_id == "outlier")
            lines.append(f"- **Public Greenhouse Listings Found**: {outlier_public_count}")
            lines.append("- **Account-Specific Task Queue**: Uninspected (Run `python main.py --inspect-account outlier` to inspect private queue safely).\n")

        # 6. Excluded Opportunities
        lines.append("## 6. Excluded Opportunities (Mandatory Exclusions)\n")
        lines.append("| Category | Excluded Listings Count |")
        lines.append("|---|---:|")
        for cat, cnt in excluded_summary.items():
            lines.append(f"| {cat.replace('_', ' ').title()} | {cnt} |")
        lines.append("\n*Note: Speech/Audio in all forms and generic non-AI automation are strictly excluded before ranking.*\n")

        # 7. Sources and Evidence
        lines.append("## 7. Sources Checked and Evidence\n")
        lines.append("| Source Name | ID | Status | Message |")
        lines.append("|---|---|---|---|")
        for s in sources_status:
            status_badge = "HEALTHY" if s.get("is_healthy") else "FAILED"
            lines.append(f"| {s.get('source_name', s.get('source_id'))} | `{s.get('source_id')}` | `{status_badge}` | {s.get('message', 'OK')} |")

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return report_path

