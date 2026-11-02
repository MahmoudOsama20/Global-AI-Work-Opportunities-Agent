import React, { useEffect, useState, useRef } from 'react';
import { api } from '../services/api';
import { CVProfile, CVSkillEvidence, CVProject } from '../types';
import { 
  UserCheck, 
  Save, 
  Check, 
  Upload, 
  FileText, 
  Trash2, 
  ShieldCheck, 
  Award, 
  Briefcase, 
  FolderGit2, 
  Layers, 
  CheckCircle2, 
  AlertCircle,
  RefreshCw,
  Sparkles
} from 'lucide-react';

export const Profile: React.FC = () => {
  const [profileConfig, setProfileConfig] = useState<any>(null);
  const [cvProfile, setCvProfile] = useState<CVProfile | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [approvedSuccess, setApprovedSuccess] = useState(false);
  const [loading, setLoading] = useState(true);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [cfg, cv] = await Promise.all([
        api.getProfile(),
        api.getCVProfile().catch(() => null),
      ]);
      setProfileConfig(cfg);
      setCvProfile(cv);
    } catch (err) {
      console.error('Error loading profile data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setUploading(true);
      setUploadError(null);
      const result = await api.uploadCV(file);
      setCvProfile(result);
    } catch (err: any) {
      setUploadError(err.message || 'Failed to parse CV');
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleApproveProfile = async () => {
    if (!cvProfile) return;
    try {
      const updated = await api.approveCVProfile(cvProfile.id);
      setCvProfile(updated);
      setApprovedSuccess(true);
      setTimeout(() => setApprovedSuccess(false), 3000);
    } catch (err) {
      console.error('Error approving profile:', err);
    }
  };

  const handleDeleteCV = async () => {
    if (!confirm('Are you sure you want to securely delete your uploaded CV data?')) return;
    try {
      await api.deleteCVData();
      setCvProfile(null);
    } catch (err) {
      console.error('Error deleting CV data:', err);
    }
  };

  const handleSaveConfig = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.updateProfile(profileConfig);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      console.error('Error saving profile config:', err);
    }
  };

  if (loading) {
    return <div className="text-slate-400 text-sm">Loading CV intelligence & profile...</div>;
  }

  return (
    <div className="space-y-10 max-w-5xl">
      
      {/* Page Title */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <UserCheck className="w-6 h-6 text-emerald-400" />
            <span>My CV & Professional Profile</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Deep resume intelligence, project evidence attribution, and personalized opportunity matching
          </p>
        </div>
      </div>

      {/* CV Upload Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-6 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800 pb-5">
          <div className="space-y-1">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <FileText className="w-5 h-5 text-emerald-400" />
              <span>Resume & CV Intelligence Engine</span>
            </h2>
            <p className="text-xs text-slate-400">
              Upload your PDF, DOCX, or TXT resume. The engine parses project evidence, extracts skills, and estimates seniority.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept=".pdf,.docx,.txt"
              className="hidden"
            />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 font-semibold text-xs rounded-xl text-white flex items-center gap-2 transition shadow-lg shadow-emerald-600/20 disabled:opacity-50"
            >
              {uploading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Parsing Document...</span>
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  <span>{cvProfile ? 'Replace CV' : 'Upload Resume'}</span>
                </>
              )}
            </button>

            {cvProfile && (
              <button
                type="button"
                onClick={handleDeleteCV}
                className="p-2.5 rounded-xl border border-slate-700 text-slate-400 hover:text-rose-400 hover:border-rose-500/50 transition"
                title="Delete CV Data"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {uploadError && (
          <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{uploadError}</span>
          </div>
        )}

        {/* Extracted Profile Preview */}
        {cvProfile ? (
          <div className="space-y-6">
            
            {/* Status Bar */}
            <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-2xl bg-slate-950/80 border border-slate-800">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 font-bold">
                  {cvProfile.file_type.toUpperCase()}
                </div>
                <div>
                  <p className="text-sm font-bold text-white">{cvProfile.filename}</p>
                  <p className="text-xs text-slate-400">
                    Uploaded {new Date(cvProfile.uploaded_at).toLocaleString()} &bull; Version {cvProfile.version}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <span className="text-xs font-semibold px-3 py-1 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                  Confidence: {cvProfile.extraction_confidence}%
                </span>

                {cvProfile.approved ? (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    APPROVED PROFILE
                  </span>
                ) : (
                  <button
                    type="button"
                    onClick={handleApproveProfile}
                    className="px-4 py-1.5 rounded-full text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 transition shadow-lg shadow-amber-500/20"
                  >
                    {approvedSuccess ? 'Approved!' : 'Approve Profile'}
                  </button>
                )}
              </div>
            </div>

            {/* Structured Fields */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-800">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                  Professional Headline
                </span>
                <p className="text-sm font-bold text-white mt-1">
                  {cvProfile.professional_headline || 'AI Engineer & Specialist'}
                </p>
              </div>

              <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-800">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                  Experience & Seniority
                </span>
                <p className="text-sm font-bold text-white mt-1 capitalize">
                  {cvProfile.seniority_level} Level ({cvProfile.years_of_experience || 3} Years)
                </p>
              </div>

              <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-800">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                  People Leadership
                </span>
                <p className="text-sm font-bold mt-1 flex items-center gap-1.5">
                  {cvProfile.has_leadership_experience ? (
                    <span className="text-emerald-400 font-semibold">Verified Management Track Record</span>
                  ) : (
                    <span className="text-slate-400 font-normal">Individual Contributor (IC)</span>
                  )}
                </p>
              </div>
            </div>

            {/* Extracted Projects */}
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <FolderGit2 className="w-4 h-4 text-emerald-400" />
                <span>Extracted Projects with Proof of Delivery ({cvProfile.projects.length})</span>
              </h3>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {cvProfile.projects.map((proj, idx) => (
                  <div key={idx} className="bg-slate-950/60 p-4 rounded-xl border border-slate-800 space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <h4 className="font-bold text-white text-sm">{proj.title}</h4>
                      {proj.metrics && (
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/10 text-amber-300 border border-amber-500/20">
                          {proj.metrics}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-400 line-clamp-3">{proj.description}</p>
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {proj.technologies.map((t, tidx) => (
                        <span key={tidx} className="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300 border border-slate-700">
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Extracted Skills with Evidence Attributions */}
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Award className="w-4 h-4 text-emerald-400" />
                <span>Skill Evidence Breakdown ({cvProfile.technical_skills.length} skills)</span>
              </h3>

              <div className="flex flex-wrap gap-2">
                {cvProfile.skill_evidence.map((ev, idx) => {
                  let badgeColor = 'bg-slate-800 text-slate-300 border-slate-700';
                  if (ev.evidence_source === 'project') badgeColor = 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30';
                  else if (ev.evidence_source === 'employment') badgeColor = 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30';
                  else if (ev.evidence_source === 'inferred') badgeColor = 'bg-purple-500/10 text-purple-300 border-purple-500/30';

                  return (
                    <div key={idx} className={`px-2.5 py-1 rounded-lg text-xs border flex items-center gap-1.5 ${badgeColor}`}>
                      <span className="font-semibold">{ev.skill_name}</span>
                      <span className="text-[10px] opacity-75 uppercase">({ev.evidence_source})</span>
                    </div>
                  );
                })}
              </div>
            </div>

          </div>
        ) : (
          <div className="p-8 text-center border-2 border-dashed border-slate-800 rounded-2xl space-y-3">
            <FileText className="w-10 h-10 text-slate-500 mx-auto" />
            <h3 className="text-sm font-bold text-white">No Resume Uploaded Yet</h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              Upload your CV to automatically map project deliverables, evaluate seniority, and enable evidence-based matching. All data is processed locally with zero external cloud transmission.
            </p>
          </div>
        )}
      </div>

      {/* Target Profile Settings Form */}
      {profileConfig && (
        <form onSubmit={handleSaveConfig} className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-6 shadow-xl">
          <div className="flex items-center justify-between border-b border-slate-800 pb-5">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Briefcase className="w-5 h-5 text-emerald-400" />
                <span>Target Search Profile Configuration</span>
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Baseline domains, Egyptian currency requirements, and matching gates
              </p>
            </div>

            <button
              type="submit"
              className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 font-semibold text-xs text-white flex items-center gap-2 transition shadow-lg shadow-emerald-600/20"
            >
              {saved ? <Check className="w-4 h-4 text-emerald-200" /> : <Save className="w-4 h-4" />}
              <span>{saved ? 'Saved!' : 'Save Configuration'}</span>
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 text-xs">
            <div>
              <label className="text-slate-400 block mb-1 font-semibold">Target Candidate Name</label>
              <input
                type="text"
                value={profileConfig.candidate?.name || ''}
                onChange={(e) => setProfileConfig({
                  ...profileConfig,
                  candidate: { ...profileConfig.candidate, name: e.target.value }
                })}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-white"
              />
            </div>

            <div>
              <label className="text-slate-400 block mb-1 font-semibold">Primary Location</label>
              <input
                type="text"
                value={profileConfig.candidate?.location || 'Cairo, Egypt'}
                onChange={(e) => setProfileConfig({
                  ...profileConfig,
                  candidate: { ...profileConfig.candidate, location: e.target.value }
                })}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-white"
              />
            </div>
          </div>
        </form>
      )}

    </div>
  );
};
