import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Candidate } from '../types';
import { 
  Compass, 
  Check, 
  X, 
  ExternalLink, 
  RefreshCw, 
  Sparkles,
  ShieldAlert
} from 'lucide-react';

export const Discovery: React.FC = () => {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(false);
  const [discovering, setDiscovering] = useState(false);

  const loadCandidates = async () => {
    try {
      setLoading(true);
      const data = await api.getCandidates();
      setCandidates(data);
    } catch (err) {
      console.error('Error fetching candidates:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCandidates();
  }, []);

  const handleApprove = async (id: number) => {
    try {
      await api.approveCandidate(id);
      setCandidates((prev) => prev.filter((c) => c.id !== id));
    } catch (err) {
      console.error('Error approving candidate:', err);
    }
  };

  const handleReject = async (id: number) => {
    try {
      await api.rejectCandidate(id);
      setCandidates((prev) => prev.filter((c) => c.id !== id));
    } catch (err) {
      console.error('Error rejecting candidate:', err);
    }
  };

  const handleTriggerDiscovery = async () => {
    try {
      setDiscovering(true);
      await api.runDiscovery();
      await loadCandidates();
    } catch (err) {
      console.error('Error running discovery:', err);
    } finally {
      setDiscovering(false);
    }
  };

  return (
    <div className="space-y-6">
      
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Compass className="w-6 h-6 text-emerald-400" />
            <span>Discovery Center</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Web-discovered hiring platforms, companies, and evaluation portals awaiting verification
          </p>
        </div>

        <button
          onClick={handleTriggerDiscovery}
          disabled={discovering}
          className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 font-semibold text-xs text-white flex items-center gap-2 transition shadow-lg shadow-emerald-600/20"
        >
          <Sparkles className={`w-4 h-4 ${discovering ? 'animate-spin' : ''}`} />
          <span>{discovering ? 'Searching Web for New Portals...' : 'Discover New Platforms'}</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {candidates.map((cand) => (
          <div key={cand.id} className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/10 text-amber-300 border border-amber-500/20">
                    SCORE: {cand.legitimacy_score}
                  </span>
                  <span className="text-xs text-slate-400 capitalize">{cand.validation_status}</span>
                </div>
                <h3 className="text-lg font-bold text-white mt-1">{cand.platform_name}</h3>
                <span className="text-xs text-slate-500">{cand.domain}</span>
              </div>
              <a
                href={cand.source_url}
                target="_blank"
                rel="noreferrer"
                className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
                title="Visit website"
              >
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>

            <div className="text-xs text-slate-400 space-y-1 bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
              <p><strong>Query:</strong> "{cand.discovered_via_query}"</p>
              {cand.detection_notes && <p><strong>Notes:</strong> {cand.detection_notes}</p>}
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-800">
              <button
                onClick={() => handleReject(cand.id)}
                className="px-3 py-1.5 rounded-lg border border-slate-800 text-slate-400 hover:text-rose-400 hover:border-rose-500/30 text-xs font-semibold flex items-center gap-1 transition"
              >
                <X className="w-3.5 h-3.5" />
                <span>Reject</span>
              </button>
              <button
                onClick={() => handleApprove(cand.id)}
                className="px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-1 transition shadow-sm"
              >
                <Check className="w-3.5 h-3.5" />
                <span>Approve & Include</span>
              </button>
            </div>
          </div>
        ))}
      </div>

      {candidates.length === 0 && !loading && (
        <div className="p-12 text-center bg-slate-900/40 border border-slate-800 rounded-2xl text-slate-400 text-sm">
          No new candidate platforms awaiting review. Click "Discover New Platforms" to query the web.
        </div>
      )}

    </div>
  );
};

