import React from 'react';
import { Opportunity } from '../types';
import { 
  X, 
  ExternalLink, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  Coins, 
  MapPin, 
  Clock, 
  Tag
} from 'lucide-react';

interface ModalProps {
  opp: Opportunity | null;
  onClose: () => void;
}

export const OpportunityModal: React.FC<ModalProps> = ({ opp, onClose }) => {
  if (!opp) return null;

  const getScoreBadgeColor = (score: number) => {
    if (score >= 90) return 'bg-amber-500/10 text-amber-300 border-amber-500/30';
    if (score >= 80) return 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30';
    if (score >= 70) return 'bg-blue-500/10 text-blue-300 border-blue-500/30';
    return 'bg-slate-700/50 text-slate-300 border-slate-600';
  };

  const getEligibilityBadgeColor = (eligibility: string) => {
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
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col shadow-2xl">
        
        {/* Modal Header */}
        <div className="p-6 border-b border-slate-800 flex items-start justify-between bg-slate-800/40">
          <div className="space-y-2 pr-6">
            <div className="flex flex-wrap items-center gap-2">
              <span className={`px-2.5 py-0.5 rounded text-xs font-bold border ${getScoreBadgeColor(opp.overall_score)}`}>
                MATCH SCORE: {opp.overall_score.toFixed(1)} / 100
              </span>
              <span className="px-2.5 py-0.5 rounded text-xs font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                {opp.source_name}
              </span>
              <span className={`px-2.5 py-0.5 rounded text-xs font-semibold border ${getEligibilityBadgeColor(opp.egypt_eligibility)}`}>
                {opp.egypt_eligibility.replace('_', ' ').toUpperCase()}
              </span>
              <span className="px-2.5 py-0.5 rounded text-xs font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                RISK: {opp.risk_level.toUpperCase()}
              </span>
            </div>
            <h2 className="text-2xl font-extrabold text-white">{opp.title}</h2>
            <p className="text-sm text-slate-400 font-medium">
              {opp.company || 'Direct Client'} &bull; Discovered {new Date(opp.first_seen_at).toLocaleDateString()}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 text-sm text-slate-200">
          
          {/* Action Callout */}
          <div className="bg-emerald-950/30 border border-emerald-500/30 rounded-xl p-4 flex items-center justify-between gap-4">
            <div>
              <span className="text-xs uppercase font-bold text-emerald-400 tracking-wider">Recommendation</span>
              <p className="text-base font-bold text-white mt-0.5">{opp.recommendation}</p>
              <p className="text-xs text-slate-400 mt-1">{opp.match_explanation}</p>
            </div>
            <a
              href={opp.original_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm transition shrink-0 shadow-lg shadow-emerald-600/20"
            >
              <span>Apply on {opp.source_name}</span>
              <ExternalLink className="w-4 h-4" />
            </a>
          </div>

          {/* Quick Info Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="bg-slate-800/40 p-3.5 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400 flex items-center gap-1.5 font-medium">
                <Coins className="w-3.5 h-3.5 text-amber-400" />
                Compensation
              </span>
              <p className="text-sm font-bold text-white mt-1">
                {opp.payment_details || 'Not disclosed'}
              </p>
            </div>
            <div className="bg-slate-800/40 p-3.5 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400 flex items-center gap-1.5 font-medium">
                <MapPin className="w-3.5 h-3.5 text-cyan-400" />
                Location & Eligibility
              </span>
              <p className="text-sm font-bold text-white mt-1">
                {opp.location || 'Remote'}
              </p>
            </div>
            <div className="bg-slate-800/40 p-3.5 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400 flex items-center gap-1.5 font-medium">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                Risk Assessment
              </span>
              <p className="text-sm font-bold text-white mt-1">
                {opp.risk_explanation || 'Verified low risk'}
              </p>
            </div>
          </div>

          {/* Skills Breakdown */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Matched Technical Skills</h4>
            <div className="flex flex-wrap gap-1.5">
              {opp.required_skills.map((skill, idx) => (
                <span key={idx} className="px-2.5 py-1 rounded-md text-xs font-semibold bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                  {skill}
                </span>
              ))}
            </div>
          </div>

          {opp.missing_skills.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Additional Tech Mentioned</h4>
              <div className="flex flex-wrap gap-1.5">
                {opp.missing_skills.map((skill, idx) => (
                  <span key={idx} className="px-2.5 py-1 rounded-md text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Full Job Description */}
          <div className="space-y-2 pt-2 border-t border-slate-800">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Original Job Description</h4>
            <div className="p-4 rounded-xl bg-slate-950/50 border border-slate-800/80 text-xs text-slate-300 leading-relaxed max-h-72 overflow-y-auto whitespace-pre-wrap">
              {opp.description}
            </div>
          </div>

          {/* Provenance and Links */}
          <div className="text-xs text-slate-400 space-y-1 pt-2 border-t border-slate-800">
            <p><strong>Original URL:</strong> <a href={opp.original_url} target="_blank" rel="noreferrer" className="text-emerald-400 hover:underline">{opp.original_url}</a></p>
            {opp.raw_data_reference && <p><strong>Cross-Source References:</strong> {opp.raw_data_reference}</p>}
          </div>

        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-800/40 flex items-center justify-between">
          <span className="text-xs text-slate-400">
            Internal ID: <code className="text-slate-300">{opp.id}</code>
          </span>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold transition"
          >
            Close Details
          </button>
        </div>

      </div>
    </div>
  );
};
