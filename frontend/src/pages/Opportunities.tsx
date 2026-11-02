import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Opportunity } from '../types';
import { 
  Search, 
  Filter, 
  ExternalLink, 
  ArrowUpDown, 
  CheckCircle2, 
  AlertCircle,
  Coins,
  MapPin
} from 'lucide-react';

interface Props {
  onSelectOpp: (opp: Opportunity) => void;
}

export const Opportunities: React.FC<Props> = ({ onSelectOpp }) => {
  const [items, setItems] = useState<Opportunity[]>([]);
  const [total, setTotal] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [eligibilityFilter, setEligibilityFilter] = useState('');
  const [sourceFilter, setSourceFilter] = useState('');
  const [paymentFilter, setPaymentFilter] = useState('');
  const [minScore, setMinScore] = useState<number | ''>('');
  const [loading, setLoading] = useState(false);

  const loadOpportunities = async () => {
    try {
      setLoading(true);
      const res = await api.getOpportunities({
        search_query: searchQuery || undefined,
        egypt_eligibility: eligibilityFilter || undefined,
        source_id: sourceFilter || undefined,
        payment_model: paymentFilter || undefined,
        min_score: minScore !== '' ? minScore : undefined,
        limit: 100,
      });
      setItems(res.items);
      setTotal(res.total);
    } catch (err) {
      console.error('Error fetching opportunities:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOpportunities();
  }, [eligibilityFilter, sourceFilter, paymentFilter, minScore]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadOpportunities();
  };

  const getScoreBadge = (score: number) => {
    if (score >= 90) return 'bg-amber-500/10 text-amber-300 border-amber-500/30';
    if (score >= 80) return 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30';
    if (score >= 70) return 'bg-blue-500/10 text-blue-300 border-blue-500/30';
    return 'bg-slate-700/50 text-slate-300 border-slate-600';
  };

  const getEligibilityBadge = (eligibility: string) => {
    switch (eligibility) {
      case 'eligible':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'likely_eligible':
        return 'bg-teal-500/10 text-teal-300 border-teal-500/30';
      case 'not_eligible':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      default:
        return 'bg-yellow-500/10 text-yellow-300 border-yellow-500/30';
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Header and Title */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Opportunities Explorer</h1>
          <p className="text-xs text-slate-400 mt-1">
            Displaying {items.length} of {total} verified global AI opportunities
          </p>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-slate-900 border border-slate-800 p-4 rounded-2xl space-y-4">
        <form onSubmit={handleSearchSubmit} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
            <input
              type="text"
              placeholder="Search by title, skills, keyword, or company (e.g. YOLO, PyTorch, RAG, Outlier)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-emerald-500 transition placeholder:text-slate-500"
            />
          </div>
          <button
            type="submit"
            className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 font-semibold text-sm rounded-xl text-white transition shrink-0"
          >
            Search
          </button>
        </form>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div>
            <label className="text-slate-400 block mb-1 font-medium">Egypt Eligibility</label>
            <select
              value={eligibilityFilter}
              onChange={(e) => setEligibilityFilter(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-300 focus:outline-none focus:border-emerald-500"
            >
              <option value="">All Eligibility Statuses</option>
              <option value="eligible">Eligible (Explicit Egypt)</option>
              <option value="likely_eligible">Likely Eligible (Worldwide)</option>
              <option value="unverified">Unverified Country</option>
              <option value="not_eligible">Not Eligible (Foreign Only)</option>
            </select>
          </div>

          <div>
            <label className="text-slate-400 block mb-1 font-medium">Platform / Source</label>
            <select
              value={sourceFilter}
              onChange={(e) => setSourceFilter(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-300 focus:outline-none focus:border-emerald-500"
            >
              <option value="">All Platforms</option>
              <option value="outlier">Outlier AI</option>
              <option value="remotive">Remotive</option>
              <option value="remoteok">Remote OK</option>
              <option value="himalayas">Himalayas</option>
              <option value="weworkremotely">We Work Remotely</option>
              <option value="alignerr">Alignerr</option>
            </select>
          </div>

          <div>
            <label className="text-slate-400 block mb-1 font-medium">Payment Model</label>
            <select
              value={paymentFilter}
              onChange={(e) => setPaymentFilter(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-300 focus:outline-none focus:border-emerald-500"
            >
              <option value="">All Payment Types</option>
              <option value="hourly">Hourly Contract</option>
              <option value="fixed">Fixed Price</option>
              <option value="per_task">Per Task Evaluation</option>
              <option value="monthly">Monthly / Retainer</option>
              <option value="not_disclosed">Undisclosed</option>
            </select>
          </div>

          <div>
            <label className="text-slate-400 block mb-1 font-medium">Minimum Match Score</label>
            <select
              value={minScore}
              onChange={(e) => setMinScore(e.target.value ? Number(e.target.value) : '')}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-300 focus:outline-none focus:border-emerald-500"
            >
              <option value="">Any Score</option>
              <option value="90">90+ (Excellent Matches)</option>
              <option value="80">80+ (Strong Matches)</option>
              <option value="70">70+ (Good Matches)</option>
              <option value="60">60+ (Moderate Matches)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Opportunities Data Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase font-semibold">
              <tr>
                <th className="py-3.5 px-4">Opportunity & Company</th>
                <th className="py-3.5 px-3">Platform</th>
                <th className="py-3.5 px-3">Payment</th>
                <th className="py-3.5 px-3">Egypt Eligibility</th>
                <th className="py-3.5 px-3 text-center">Score</th>
                <th className="py-3.5 px-3">Recommendation</th>
                <th className="py-3.5 px-4 text-right">Link</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {items.map((opp) => (
                <tr
                  key={opp.id}
                  onClick={() => onSelectOpp(opp)}
                  className="hover:bg-slate-800/50 cursor-pointer transition"
                >
                  <td className="py-3.5 px-4 max-w-sm">
                    <div className="font-bold text-white text-sm hover:text-emerald-400 transition truncate">
                      {opp.title}
                    </div>
                    <div className="text-slate-400 text-xs mt-0.5 truncate">
                      {opp.company || 'Direct Client'} &bull; {opp.location || 'Remote'}
                    </div>
                  </td>
                  <td className="py-3.5 px-3 whitespace-nowrap">
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 font-medium">
                      {opp.source_name}
                    </span>
                  </td>
                  <td className="py-3.5 px-3 whitespace-nowrap">
                    <div className="font-semibold text-white">
                      {opp.payment_details || 'Not disclosed'}
                    </div>
                    <div className="text-[10px] text-slate-400 uppercase">
                      {opp.payment_model}
                    </div>
                  </td>
                  <td className="py-3.5 px-3 whitespace-nowrap">
                    <span className={`px-2 py-0.5 rounded text-[11px] font-semibold border ${getEligibilityBadge(opp.egypt_eligibility)}`}>
                      {opp.egypt_eligibility.replace('_', ' ').toUpperCase()}
                    </span>
                  </td>
                  <td className="py-3.5 px-3 text-center whitespace-nowrap">
                    <span className={`px-2.5 py-1 rounded text-xs font-bold border ${getScoreBadge(opp.overall_score)}`}>
                      {opp.overall_score.toFixed(1)}
                    </span>
                  </td>
                  <td className="py-3.5 px-3 max-w-xs">
                    <span className="font-medium text-slate-200 block truncate">
                      {opp.recommendation}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-right whitespace-nowrap">
                    <a
                      href={opp.original_url}
                      target="_blank"
                      rel="noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-emerald-600 text-slate-300 hover:text-white transition font-medium text-xs"
                    >
                      <span>Apply</span>
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {items.length === 0 && !loading && (
          <div className="p-10 text-center text-slate-500 text-sm">
            No opportunities match your filter criteria. Try adjusting or clearing search terms.
          </div>
        )}
      </div>

    </div>
  );
};
