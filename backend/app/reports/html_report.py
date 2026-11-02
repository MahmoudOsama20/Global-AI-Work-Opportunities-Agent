from datetime import datetime, timezone
from typing import List, Dict, Any
from pathlib import Path
from jinja2 import Template
from app.schemas.opportunity import NormalizedOpportunity
from app.core.config import DATA_DIR

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Global AI Opportunities Intelligence Report — {{ run_id }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>body { font-family: 'Inter', sans-serif; }</style>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen py-10 px-4 sm:px-6 lg:px-8">
    <div class="max-w-7xl mx-auto space-y-10">
        
        <!-- Header -->
        <header class="bg-slate-800/80 border border-slate-700/60 rounded-2xl p-8 backdrop-blur shadow-xl">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 mb-3">
                        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                        INTELLIGENCE REPORT READY
                    </div>
                    <h1 class="text-3xl font-bold tracking-tight text-white">Global AI Opportunities Intelligence Agent</h1>
                    <p class="text-slate-400 text-sm mt-1">Run Identifier: <code class="text-emerald-400">{{ run_id }}</code> &bull; Generated: {{ generated_at }}</p>
                </div>
                <div class="text-right">
                    <span class="text-xs uppercase tracking-wider text-slate-400 font-medium">Candidate Location</span>
                    <p class="text-lg font-bold text-white">Cairo, Egypt (EG)</p>
                    <span class="text-xs text-slate-400">Remote Only &bull; USD / EUR / GBP</span>
                </div>
            </div>
        </header>

        <!-- Executive Metrics Grid -->
        <section class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
            <div class="bg-slate-800/60 border border-slate-700/50 p-5 rounded-xl">
                <span class="text-xs font-medium text-slate-400 uppercase">Total Collected</span>
                <p class="text-3xl font-extrabold text-white mt-2">{{ metrics.total_collected or 0 }}</p>
            </div>
            <div class="bg-slate-800/60 border border-slate-700/50 p-5 rounded-xl">
                <span class="text-xs font-medium text-slate-400 uppercase">New Listings</span>
                <p class="text-3xl font-extrabold text-emerald-400 mt-2">{{ metrics.new_count or 0 }}</p>
            </div>
            <div class="bg-slate-800/60 border border-slate-700/50 p-5 rounded-xl">
                <span class="text-xs font-medium text-slate-400 uppercase">Duplicates</span>
                <p class="text-3xl font-extrabold text-indigo-400 mt-2">{{ metrics.duplicate_count or 0 }}</p>
            </div>
            <div class="bg-slate-800/60 border border-slate-700/50 p-5 rounded-xl">
                <span class="text-xs font-medium text-slate-400 uppercase">Fresh (≤ 24h)</span>
                <p class="text-3xl font-extrabold text-emerald-400 mt-2">{{ metrics.fresh_24h or 0 }}</p>
            </div>
            <div class="bg-slate-800/60 border border-slate-700/50 p-5 rounded-xl">
                <span class="text-xs font-medium text-slate-400 uppercase">Fresh (≤ 7d)</span>
                <p class="text-3xl font-extrabold text-teal-400 mt-2">{{ metrics.fresh_7d or 0 }}</p>
            </div>
            <div class="bg-slate-800/60 border border-slate-700/50 p-5 rounded-xl">
                <span class="text-xs font-medium text-slate-400 uppercase">Excellent Matches</span>
                <p class="text-3xl font-extrabold text-amber-400 mt-2">{{ metrics.excellent_matches or 0 }}</p>
            </div>
            <div class="bg-slate-800/60 border border-slate-700/50 p-5 rounded-xl">
                <span class="text-xs font-medium text-slate-400 uppercase">Egypt Eligible</span>
                <p class="text-3xl font-extrabold text-cyan-400 mt-2">{{ metrics.eligible_in_egypt or 0 }}</p>
            </div>
            <div class="bg-slate-800/60 border border-slate-700/50 p-5 rounded-xl">
                <span class="text-xs font-medium text-slate-400 uppercase">Excluded Work</span>
                <p class="text-3xl font-extrabold text-rose-400 mt-2">{{ metrics.excluded_count or 0 }}</p>
            </div>
        </section>

        <!-- Top Recommended Opportunities -->
        <section class="space-y-4">
            <div class="flex items-center justify-between">
                <h2 class="text-2xl font-bold text-white flex items-center gap-2">
                    <span>Top Recommended Opportunities</span>
                    <span class="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Apply First</span>
                </h2>
                <span class="text-xs text-slate-400">Ranked by 100-Point Match Score &bull; Egyptian Eligibility Verified</span>
            </div>

            <div class="grid grid-cols-1 gap-4">
                {% for opp in top_opportunities %}
                <div class="bg-slate-800/70 border border-slate-700/60 hover:border-slate-600 transition rounded-xl p-6 shadow-md">
                    <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                        <div class="space-y-1">
                            <div class="flex flex-wrap items-center gap-2">
                                <span class="px-2.5 py-0.5 rounded text-xs font-bold bg-amber-500/10 text-amber-300 border border-amber-500/20">
                                    SCORE: {{ "%.1f"|format(opp.overall_score) }}
                                </span>
                                <span class="px-2 py-0.5 rounded text-xs font-medium bg-slate-700 text-slate-300">
                                    {{ opp.source_name }}
                                </span>
                                <span class="px-2 py-0.5 rounded text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                                    {{ opp.egypt_eligibility|replace('_', ' ')|upper }}
                                </span>
                                <span class="px-2 py-0.5 rounded text-xs font-medium bg-slate-800 text-slate-400 border border-slate-700">
                                    RISK: {{ opp.risk_level|upper }}
                                </span>
                            </div>
                            <h3 class="text-xl font-bold text-white">{{ opp.title }}</h3>
                            <p class="text-sm text-slate-400">{{ opp.company or 'Direct Client' }} &bull; {{ opp.payment_details or 'Compensation not disclosed' }} &bull; Location: {{ opp.location or 'Remote' }}</p>
                        </div>
                        <div>
                            <a href="{{ opp.original_url }}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm transition shadow-lg shadow-emerald-600/20">
                                <span>Apply on {{ opp.source_name }}</span>
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
                            </a>
                        </div>
                    </div>
                    
                    <div class="mt-4 pt-4 border-t border-slate-700/40 text-xs text-slate-300 space-y-2">
                        <p><strong class="text-slate-400">Matched Skills:</strong> {{ opp.required_skills[:6]|join(', ') }}</p>
                        <p><strong class="text-slate-400">Analysis:</strong> {{ opp.match_explanation }}</p>
                    </div>
                </div>
                {% else %}
                <div class="bg-slate-800/40 border border-slate-700/40 rounded-xl p-8 text-center text-slate-400">
                    No top-tier opportunities found in this run meeting the score threshold.
                </div>
                {% endfor %}
            </div>
        </section>

        <!-- Exclusions Breakdown -->
        <section class="bg-slate-800/60 border border-slate-700/50 rounded-xl p-6">
            <h3 class="text-lg font-bold text-white mb-2">Mandatory Filter Exclusions Summary</h3>
            <p class="text-xs text-slate-400 mb-4">The agent automatically filters speech/audio (ASR/TTS) and generic non-AI automation prior to ranking.</p>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
                {% for cat, count in excluded_summary.items() %}
                <div class="bg-slate-900/50 p-4 rounded-lg border border-slate-800">
                    <span class="text-xs text-slate-400 block">{{ cat|replace('_', ' ')|title }}</span>
                    <span class="text-xl font-bold text-rose-400 mt-1 block">{{ count }}</span>
                </div>
                {% endfor %}
            </div>
        </section>

        <!-- Footer -->
        <footer class="text-center text-xs text-slate-500 py-6 border-t border-slate-800">
            Global AI Opportunities Intelligence Agent &bull; Manually triggered production audit report
        </footer>

    </div>
</body>
</html>
"""

class HtmlReportGenerator:
    """Generates standalone, responsive HTML intelligence reports."""

    def generate(
        self,
        run_id: str,
        metrics: Dict[str, Any],
        opportunities: List[NormalizedOpportunity],
        excluded_summary: Dict[str, int],
        sources_status: List[Dict[str, Any]],
    ) -> Path:
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        report_dir = DATA_DIR / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / f"report_{run_id}.html"

        # Filter top opportunities
        top = [
            opp for opp in opportunities
            if opp.overall_score >= 70.0 and opp.egypt_eligibility != "not_eligible"
        ]
        top.sort(key=lambda x: x.overall_score, reverse=True)

        template = Template(HTML_TEMPLATE)
        rendered = template.render(
            run_id=run_id,
            generated_at=now_str,
            metrics=metrics,
            top_opportunities=top[:25],
            excluded_summary=excluded_summary,
            sources_status=sources_status,
        )

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(rendered)

        return report_path

