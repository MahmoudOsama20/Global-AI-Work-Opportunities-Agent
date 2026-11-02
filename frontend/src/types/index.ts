export interface Opportunity {
  id: string;
  source_id: string;
  source_name: string;
  source_type: string;
  title: string;
  company: string | null;
  description: string;
  original_url: string;
  canonical_url: string;
  category: string;
  technical_domains: string[];
  required_skills: string[];
  preferred_skills: string[];
  experience_level: string | null;
  employment_type: string;
  payment_model: string;
  hourly_rate_min: number | null;
  hourly_rate_max: number | null;
  fixed_budget_min: number | null;
  fixed_budget_max: number | null;
  currency: string;
  payment_details: string | null;
  location: string | null;
  remote_status: string;
  eligible_countries: string[];
  egypt_eligibility: string;
  payment_methods: string[];
  application_requirements: string | null;
  assessment_required: boolean;
  posted_at: string | null;
  first_seen_at: string;
  last_seen_at: string;
  last_verified_at: string;
  listing_status: string;
  verification_status: string;
  skill_match_score: number;
  eligibility_score: number;
  overall_score: number;
  match_explanation: string | null;
  missing_skills: string[];
  recommendation: string;
  duplicate_group_id: string | null;
  raw_data_reference: string | null;
  risk_level: string;
  risk_explanation: string | null;
  created_at: string;
  updated_at: string;
}

export interface MetricsSummary {
  total_opportunities: number;
  excellent_matches: number;
  strong_matches: number;
  eligible_in_egypt: number;
  unverified_eligibility: number;
  by_source: Record<string, number>;
}

export interface Source {
  id: string;
  name: string;
  category: string;
  official_website: string;
  careers_url?: string;
  api_url?: string;
  collection_method: string;
  status: string;
  requires_auth: boolean;
  supports_account_inspection: boolean;
  supports_egypt: string;
  payment_methods: string[];
  enabled: boolean;
  description?: string;
  last_health_check_at?: string;
  last_success_at?: string;
  consecutive_failures: number;
  created_at: string;
}

export interface Candidate {
  id: number;
  domain: string;
  platform_name: string;
  source_url: string;
  validation_status: string;
  legitimacy_score: number;
  discovered_via_query: string;
  detection_notes: string;
  created_at: string;
}

export interface RunRecord {
  id: string;
  trigger_type: string;
  started_at: string;
  finished_at?: string;
  status: string;
  sources_attempted: number;
  sources_succeeded: number;
  sources_failed: number;
  total_collected: number;
  new_count: number;
  duplicate_count: number;
  excluded_count: number;
  relevant_count: number;
  report_html_path?: string;
  report_md_path?: string;
}

export interface ReportItem {
  run_id: string;
  filename: string;
  html_path: string;
  md_path?: string;
  created_at: string;
}
