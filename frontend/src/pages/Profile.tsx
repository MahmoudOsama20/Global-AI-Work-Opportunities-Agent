import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { UserCheck, Save, Check, MapPin, Coins, Sparkles } from 'lucide-react';

export const Profile: React.FC = () => {
  const [profile, setProfile] = useState<any>(null);
  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const data = await api.getProfile();
      setProfile(data);
    } catch (err) {
      console.error('Error fetching profile:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.updateProfile(profile);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      console.error('Error saving profile:', err);
    }
  };

  if (loading || !profile) {
    return <div className="text-slate-400 text-sm">Loading user profile...</div>;
  }

  return (
    <form onSubmit={handleSave} className="space-y-6 max-w-4xl">
      
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <UserCheck className="w-6 h-6 text-emerald-400" />
            <span>Target Professional Profile</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Matching parameters, Egyptian location rules, and technical domain priorities
          </p>
        </div>

        <button
          type="submit"
          className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 font-semibold text-xs text-white flex items-center gap-2 transition shadow-lg shadow-emerald-600/20"
        >
          {saved ? <Check className="w-4 h-4 text-emerald-200" /> : <Save className="w-4 h-4" />}
          <span>{saved ? 'Saved Profile!' : 'Save Configuration'}</span>
        </button>
      </div>

      {/* Location Card */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl space-y-4">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
          <MapPin className="w-4 h-4 text-cyan-400" />
          <span>Location & Regional Constraints</span>
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
          <div>
            <label className="text-slate-400 block mb-1 font-medium">Country</label>
            <input
              type="text"
              value={profile.primary_location?.country || ''}
              disabled
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-300 font-semibold"
            />
          </div>
          <div>
            <label className="text-slate-400 block mb-1 font-medium">City</label>
            <input
              type="text"
              value={profile.primary_location?.city || ''}
              onChange={(e) =>
                setProfile({
                  ...profile,
                  primary_location: { ...profile.primary_location, city: e.target.value },
                })
              }
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
            />
          </div>
          <div>
            <label className="text-slate-400 block mb-1 font-medium">Timezone</label>
            <input
              type="text"
              value={profile.primary_location?.timezone || ''}
              disabled
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-300"
            />
          </div>
        </div>
      </div>

      {/* Compensation Card */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl space-y-4">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
          <Coins className="w-4 h-4 text-amber-400" />
          <span>Compensation & Supported Payout Channels</span>
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="text-slate-400 block mb-1 font-medium">Minimum Hourly Rate (USD)</label>
            <input
              type="number"
              value={profile.payment_preferences?.minimum_hourly_usd || 15}
              onChange={(e) =>
                setProfile({
                  ...profile,
                  payment_preferences: {
                    ...profile.payment_preferences,
                    minimum_hourly_usd: Number(e.target.value),
                  },
                })
              }
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500 font-semibold"
            />
          </div>
          <div>
            <label className="text-slate-400 block mb-1 font-medium">Minimum Fixed Project (USD)</label>
            <input
              type="number"
              value={profile.payment_preferences?.minimum_fixed_project_usd || 100}
              onChange={(e) =>
                setProfile({
                  ...profile,
                  payment_preferences: {
                    ...profile.payment_preferences,
                    minimum_fixed_project_usd: Number(e.target.value),
                  },
                })
              }
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500 font-semibold"
            />
          </div>
        </div>
        <div className="pt-2 text-xs text-slate-400">
          <span className="font-semibold text-slate-300">Verified Payout Methods In Egypt: </span>
          {profile.payment_preferences?.supported_methods_in_location?.join(', ')}
        </div>
      </div>

      {/* Technical Domains Priority List */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl space-y-4">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-emerald-400" />
          <span>Technical Domains & Priority Order</span>
        </h3>
        <div className="space-y-3">
          {profile.domains &&
            Object.entries(profile.domains).map(([key, domain]: [string, any], idx) => (
              <div key={key} className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-start justify-between text-xs">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-slate-800 text-emerald-400 font-bold flex items-center justify-center text-[11px]">
                      {idx + 1}
                    </span>
                    <h4 className="font-bold text-white text-sm">{domain.name}</h4>
                  </div>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {domain.skills?.slice(0, 8).map((sk: string, sIdx: number) => (
                      <span key={sIdx} className="px-2 py-0.5 rounded bg-slate-800 text-[11px] text-slate-300">
                        {sk}
                      </span>
                    ))}
                    {domain.skills?.length > 8 && (
                      <span className="text-[11px] text-slate-500 self-center">
                        +{domain.skills.length - 8} more
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
        </div>
      </div>

    </form>
  );
};
