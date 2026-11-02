import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { MetricsSummary, Opportunity, RunRecord } from '../types';
import { 
  Play, 
  Sparkles, 
  CheckCircle2, 
  AlertCircle, 
  TrendingUp, 
  ShieldCheck, 
  MapPin, 
  Coins, 
  ExternalLink,
  RefreshCw,
  Clock
} from 'lucide-react';

interface OverviewProps {
  onSelectOpp: (opp: Opportunity) => void;
  isRunning: boolean;
  onTriggerRun: () => void;
}

export const Overview: React.FC<OverviewProps> = ({ onSelectOpp, isRunning, onTriggerRun }) => {
  const [metrics, setMetrics] = useState<MetricsSummary | null>(null);
  const [topOpps, setTopOpps] = useState<Opportunity[]>([]);
  const [recentRuns, setRecentRuns] = useState<RunRecord[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const [m, oppsRes, runs] = await Promise.all([
        api.getMetrics(),
        api.getOpportunities({ limit: 6, min_score: 70 }),
        api.getRuns(),
      ]);
      setMetrics(m);
      setTopOpps(oppsRes.items);
      setRecentRuns(runs.slice(0, 3));
    } catch (err) {
      console.error('Error loading overview data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [isRunning]);

  return (
    <div className="space-y-8">
      
      {/* Search Trigger Hero Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-slate-800 to-emerald-950/60 border border-slate-700/60 p-8 shadow-2xl">
        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div className="space-y-3 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Sparkles className="w-3.5 h-3.5" />
              ON-DEMAND AI WORK DISCOVERY
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
              Discover Global Paid AI Work In Seconds
            </h1>
            <p className="text-sm text-slate-300 leading-relaxed">
              Searches verified platforms (Outlier, Remotive, RemoteOK, Himalayas, Alignerr, We Work Remotely), evaluates requirements against your skills, validates Egyptian payout compatibility, purges speech/audio and generic automation, and delivers an evidence-based report.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-center gap-4">
            <button
              onClick={onTriggerRun}
              disabled={isRunning}
              className={`w-full sm:w-auto px-8 py-4 rounded-xl font-bold text-base flex items-center justify-center gap-3 transition shadow-xl ${
                isRunning
                  ? 'bg-slate-800 text-slate-400 border border-slate-700 cursor-not-allowed'
                  : 'bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-emerald-500/25 active:scale-95'
              }`}
            >
              {isRunning ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  <span>Searching Global Web...</span>
                </>
              ) : (
                <>
                  <Play className="w-5 h-5 fill-current" />
                  <span>RUN GLOBAL AI OPPORTUNITY SEARCH</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Primary Intelligence Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-sm">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Discovered</span>
          <p className="text-3xl font-extrabold text-white mt-2">{metrics?.total_opportunities || 0}</p>
          <span className="text-[11px] text-slate-400 mt-1 block">Active across platforms</span>
        </div>
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-sm">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Excellent Matches</span>
          <p className="text-3xl font-extrabold text-amber-400 mt-2">{metrics?.excellent_matches || 0}</p>
          <span className="text-[11px] text-amber-400/80 mt-1 block">Score 90 – 100</span>
        </div>
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-sm">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Strong Matches</span>
          <p className="text-3xl font-extrabold text-emerald-400 mt-2">{metrics?.strong_matches || 0}</p>
          <span className="text-[11px] text-emerald-400/80 mt-1 block">Score 80 – 89</span>
        </div>
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-sm">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Eligible In Egypt</span>
          <p className="text-3xl font-extrabold text-cyan-400 mt-2">{metrics?.eligible_in_egypt || 0}</p>
          <span className="text-[11px] text-cyan-400/80 mt-1 block">Payout verified</span>
        </div>
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-sm">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Needs Verification</span>
          <p className="text-3xl font-extrabold text-yellow-400 mt-2">{metrics?.unverified_eligibility || 0}</p>
          <span className="text-[11px] text-yellow-400/80 mt-1 block">Unspecified country</span>
        </div>
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-sm">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Sources Active</span>
          <p className="text-3xl font-extrabold text-indigo-400 mt-2">
            {metrics?.by_source ? Object.keys(metrics.by_source).length : 0}
          </p>
          <span className="text-[11px] text-indigo-400/80 mt-1 block">Marketplaces & Boards</span>
        </div>
      </div>

      {/* Main Content Split: Top Matches & Source Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Top Matches Preview (2 Cols) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-emerald-400" />
              <span>Highest Ranked Opportunities</span>
            </h2>
            <span className="text-xs text-slate-400 font-medium">Ranked by Match Engine</span>
          </div>

          <div className="space-y-3">
            {topOpps.map((opp) => (
              <div
                key={opp.id}
                onClick={() => onSelectOpp(opp)}
                className="bg-slate-900/70 border border-slate-800 hover:border-slate-700 p-5 rounded-2xl transition cursor-pointer group shadow-sm"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="space-y-1.5 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className={`px-2 py-0.5 rounded text-xs font-bold border ${
                        opp.overall_score >= 90
                          ? 'bg-amber-500/10 text-amber-300 border-amber-500/30'
                          : 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
                      }`}>
                        SCORE: {opp.overall_score.toFixed(1)}
                      </span>
                      <span className="px-2 py-0.5 rounded text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700">
                        {opp.source_name}
                      </span>
                      <span className="px-2 py-0.5 rounded text-xs font-medium bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
                        {opp.egypt_eligibility.replace('_', ' ').toUpperCase()}
                      </span>
                    </div>
                    <h3 className="text-base font-bold text-white group-hover:text-emerald-400 transition">
                      {opp.title}
                    </h3>
                    <p className="text-xs text-slate-400">
                      {opp.company || 'Direct Client'} &bull; {opp.payment_details || 'Compensation not disclosed'} &bull; {opp.location || 'Remote'}
                    </p>
                    <div className="flex flex-wrap gap-1 pt-1">
                      {opp.required_skills.slice(0, 4).map((skill, sIdx) => (
                        <span key={sIdx} className="px-2 py-0.5 rounded bg-slate-800/80 text-[11px] text-slate-300 border border-slate-700/50">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                  <a
                    href={opp.original_url}
                    target="_blank"
                    rel="noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="p-2 text-slate-400 hover:text-emerald-400 hover:bg-slate-800 rounded-lg transition"
                    title="Open original listing link"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                </div>
              </div>
            ))}

            {topOpps.length === 0 && !loading && (
              <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-8 text-center text-slate-400">
                No opportunities collected yet. Click "RUN GLOBAL AI OPPORTUNITY SEARCH" above to start!
              </div>
            )}
          </div>
        </div>

        {/* Right Sidebar: Sources Breakdown & Recent Runs (1 Col) */}
        <div className="space-y-6">
          
          {/* Opportunities By Source */}
          <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Opportunities by Platform
            </h3>
            <div className="space-y-2.5">
              {metrics?.by_source && Object.entries(metrics.by_source).map(([source, count]) => (
                <div key={source} className="flex items-center justify-between text-xs py-1 border-b border-slate-800/60 last:border-0">
                  <span className="text-slate-300 font-medium">{source}</span>
                  <span className="px-2.5 py-0.5 rounded-full bg-slate-800 font-bold text-emerald-400 border border-slate-700">
                    {count}
                  </span>
                </div>
              ))}
              {(!metrics?.by_source || Object.keys(metrics.by_source).length === 0) && (
                <p className="text-xs text-slate-500">No sources tracked yet.</p>
              )}
            </div>
          </div>

          {/* Recent Runs History */}
          <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
              <Clock className="w-4 h-4 text-slate-400" />
              <span>Recent Search Runs</span>
            </h3>
            <div className="space-y-3">
              {recentRuns.map((run) => (
                <div key={run.id} className="p-3 rounded-xl bg-slate-800/40 border border-slate-800 text-xs space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-white">{run.id}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      {run.status.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-slate-400">
                    Collected {run.total_collected} &bull; {run.relevant_count} relevant &bull; {run.duplicate_count} duplicates
                  </p>
                </div>
              ))}
              {recentRuns.length === 0 && (
                <p className="text-xs text-slate-500">No previous runs recorded.</p>
              )}
            </div>
          </div>

        </div>

      </div>

    </div>
  );
};
