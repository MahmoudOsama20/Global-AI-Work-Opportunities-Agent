import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Source } from '../types';
import { 
  Globe2, 
  CheckCircle2, 
  AlertCircle, 
  RefreshCw, 
  ExternalLink,
  Power,
  ShieldCheck
} from 'lucide-react';

export const Sources: React.FC = () => {
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(false);
  const [checking, setChecking] = useState(false);

  const loadSources = async () => {
    try {
      setLoading(true);
      const data = await api.getSources();
      setSources(data);
    } catch (err) {
      console.error('Error fetching sources:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSources();
  }, []);

  const handleToggle = async (id: string, currentEnabled: boolean) => {
    try {
      await api.updateSource(id, { enabled: !currentEnabled });
      setSources((prev) =>
        prev.map((s) => (s.id === id ? { ...s, enabled: !currentEnabled } : s))
      );
    } catch (err) {
      console.error('Error toggling source:', err);
    }
  };

  const handleHealthCheckAll = async () => {
    try {
      setChecking(true);
      await api.triggerHealthCheck();
      await loadSources();
    } catch (err) {
      console.error('Health check failed:', err);
    } finally {
      setChecking(false);
    }
  };

  return (
    <div className="space-y-6">
      
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Globe2 className="w-6 h-6 text-emerald-400" />
            <span>Sources Registry</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Registered marketplaces, AI evaluation providers, and remote boards
          </p>
        </div>

        <button
          onClick={handleHealthCheckAll}
          disabled={checking}
          className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-semibold text-xs flex items-center gap-2 transition"
        >
          <RefreshCw className={`w-4 h-4 ${checking ? 'animate-spin text-emerald-400' : ''}`} />
          <span>{checking ? 'Checking Health...' : 'Run Health Check All'}</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {sources.map((s) => (
          <div
            key={s.id}
            className={`p-5 rounded-2xl border transition bg-slate-900/80 ${
              s.enabled ? 'border-slate-800 hover:border-slate-700' : 'border-slate-800/40 opacity-60'
            }`}
          >
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  {s.category.replace(/_/g, ' ')}
                </span>
                <h3 className="text-base font-bold text-white mt-0.5">{s.name}</h3>
              </div>
              <button
                onClick={() => handleToggle(s.id, s.enabled)}
                className={`p-1.5 rounded-lg border transition ${
                  s.enabled
                    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20'
                    : 'bg-slate-800 border-slate-700 text-slate-400 hover:text-white'
                }`}
                title={s.enabled ? 'Disable source' : 'Enable source'}
              >
                <Power className="w-4 h-4" />
              </button>
            </div>

            <p className="text-xs text-slate-400 mt-2 line-clamp-2">
              {s.description || 'Verified job source.'}
            </p>

            <div className="mt-4 pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs">
              <div className="flex items-center gap-1.5">
                <span className={`w-2 h-2 rounded-full ${s.status === 'verified' ? 'bg-emerald-400' : 'bg-yellow-400'}`}></span>
                <span className="text-slate-300 capitalize font-medium">{s.status}</span>
              </div>
              <a
                href={s.official_website}
                target="_blank"
                rel="noreferrer"
                className="text-slate-400 hover:text-emerald-400 flex items-center gap-1 text-[11px]"
              >
                <span>Website</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>
        ))}
      </div>

    </div>
  );
};
