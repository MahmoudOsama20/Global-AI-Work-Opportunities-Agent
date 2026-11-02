import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ReportItem } from '../types';
import { FileText, ExternalLink, Download, Clock } from 'lucide-react';

export const Reports: React.FC = () => {
  const [reports, setReports] = useState<ReportItem[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    try {
      setLoading(true);
      const data = await api.getReports();
      setReports(data);
    } catch (err) {
      console.error('Error fetching reports:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <FileText className="w-6 h-6 text-emerald-400" />
          <span>Intelligence Reports & Audit History</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Self-contained evidence-based reports generated from completed manual search runs
        </p>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase font-semibold">
              <tr>
                <th className="py-3.5 px-4">Run Identifier</th>
                <th className="py-3.5 px-4">Generated Date</th>
                <th className="py-3.5 px-4 text-right">View / Download</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {reports.map((r) => (
                <tr key={r.run_id} className="hover:bg-slate-800/40 transition">
                  <td className="py-3.5 px-4 font-bold text-white">
                    <code>{r.run_id}</code>
                  </td>
                  <td className="py-3.5 px-4 text-slate-400">
                    {new Date(r.created_at).toLocaleString()}
                  </td>
                  <td className="py-3.5 px-4 text-right space-x-2">
                    <a
                      href={`/api/reports/${r.run_id}/html`}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold transition shadow-sm text-xs"
                    >
                      <span>Open HTML Report</span>
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                    {r.md_path && (
                      <a
                        href={`/api/reports/${r.run_id}/markdown`}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-semibold transition text-xs"
                      >
                        <span>Markdown</span>
                        <Download className="w-3.5 h-3.5" />
                      </a>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {reports.length === 0 && !loading && (
          <div className="p-10 text-center text-slate-500 text-sm">
            No reports generated yet. Run a global search to produce the first intelligence report.
          </div>
        )}
      </div>

    </div>
  );
};

