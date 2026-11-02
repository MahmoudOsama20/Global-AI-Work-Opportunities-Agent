import React from 'react';
import { 
  Sparkles, 
  Search, 
  Globe2, 
  Compass, 
  UserCheck, 
  FileText, 
  Layers
} from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  isRunning: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, isRunning }) => {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: Layers },
    { id: 'opportunities', label: 'Opportunities', icon: Search },
    { id: 'sources', label: 'Sources', icon: Globe2 },
    { id: 'discovery', label: 'Discovery Center', icon: Compass },
    { id: 'profile', label: 'My CV & Profile', icon: UserCheck },
    { id: 'reports', label: 'Reports & History', icon: FileText },
  ];

  return (
    <header className="bg-slate-900/90 border-b border-slate-800 sticky top-0 z-40 backdrop-blur">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <Sparkles className="w-5 h-5 text-slate-950 font-black" />
            </div>
            <div>
              <span className="font-extrabold text-base tracking-tight text-white flex items-center gap-2">
                Global AI Intelligence Agent
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  Egypt Edition
                </span>
              </span>
              <p className="text-xs text-slate-400">Paid AI Work Discovery & Verification Platform</p>
            </div>
          </div>

          <nav className="flex space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-semibold transition-all ${
                    isActive
                      ? 'bg-slate-800 text-white shadow-sm border border-slate-700'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-emerald-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {isRunning && (
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold animate-pulse">
              <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
              Search Run In Progress...
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

