import { Opportunity, MetricsSummary, Source, Candidate, RunRecord, ReportItem } from '../types';

const API_BASE = '/api';

export const api = {
  // Metrics & Stats
  async getMetrics(): Promise<MetricsSummary> {
    const res = await fetch(`${API_BASE}/opportunities/metrics`);
    if (!res.ok) throw new Error('Failed to fetch metrics');
    return res.json();
  },

  // Opportunities
  async getOpportunities(params: Record<string, any> = {}): Promise<{ total: number; items: Opportunity[] }> {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') {
        query.append(k, String(v));
      }
    });
    const res = await fetch(`${API_BASE}/opportunities?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch opportunities');
    return res.json();
  },

  async getOpportunity(id: string): Promise<Opportunity> {
    const res = await fetch(`${API_BASE}/opportunities/${id}`);
    if (!res.ok) throw new Error('Failed to fetch opportunity');
    return res.json();
  },

  // Sources
  async getSources(): Promise<Source[]> {
    const res = await fetch(`${API_BASE}/sources`);
    if (!res.ok) throw new Error('Failed to fetch sources');
    return res.json();
  },

  async updateSource(id: string, payload: Partial<Source>): Promise<Source> {
    const res = await fetch(`${API_BASE}/sources/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to update source');
    return res.json();
  },

  async triggerHealthCheck(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/sources/health-check`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to trigger health check');
    return res.json();
  },

  // Pipeline
  async runPipeline(options: { source_id?: string; category?: string; discover_sources?: boolean } = {}): Promise<any> {
    const query = new URLSearchParams();
    if (options.source_id) query.append('source_id', options.source_id);
    if (options.category) query.append('category', options.category);
    if (options.discover_sources) query.append('discover_sources', 'true');
    const res = await fetch(`${API_BASE}/pipeline/run?${query.toString()}`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to start pipeline run');
    return res.json();
  },

  async getRuns(): Promise<RunRecord[]> {
    const res = await fetch(`${API_BASE}/pipeline/runs`);
    if (!res.ok) throw new Error('Failed to fetch runs');
    return res.json();
  },

  // Discovery
  async getCandidates(): Promise<Candidate[]> {
    const res = await fetch(`${API_BASE}/discovery/candidates`);
    if (!res.ok) throw new Error('Failed to fetch candidates');
    return res.json();
  },

  async approveCandidate(id: number): Promise<any> {
    const res = await fetch(`${API_BASE}/discovery/candidates/${id}/approve`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to approve candidate');
    return res.json();
  },

  async rejectCandidate(id: number): Promise<any> {
    const res = await fetch(`${API_BASE}/discovery/candidates/${id}/reject`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to reject candidate');
    return res.json();
  },

  async runDiscovery(): Promise<any> {
    const res = await fetch(`${API_BASE}/discovery/run`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to trigger discovery');
    return res.json();
  },

  // Profile
  async getProfile(): Promise<any> {
    const res = await fetch(`${API_BASE}/profile`);
    if (!res.ok) throw new Error('Failed to fetch profile');
    return res.json();
  },

  async updateProfile(data: any): Promise<any> {
    const res = await fetch(`${API_BASE}/profile`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to update profile');
    return res.json();
  },

  // Reports
  async getReports(): Promise<ReportItem[]> {
    const res = await fetch(`${API_BASE}/reports`);
    if (!res.ok) throw new Error('Failed to fetch reports');
    return res.json();
  },
};
