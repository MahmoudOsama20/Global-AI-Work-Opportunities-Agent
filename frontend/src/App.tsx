import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { OpportunityModal } from './components/OpportunityModal';
import { Overview } from './pages/Overview';
import { Opportunities } from './pages/Opportunities';
import { Sources } from './pages/Sources';
import { Discovery } from './pages/Discovery';
import { Profile } from './pages/Profile';
import { Reports } from './pages/Reports';
import { Opportunity } from './types';
import { api } from './services/api';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedOpp, setSelectedOpp] = useState<Opportunity | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [runMessage, setRunMessage] = useState<string | null>(null);

  const handleTriggerRun = async () => {
    try {
      setIsRunning(true);
      setRunMessage('Running global search across active sources...');
      const summary = await api.runPipeline();
      setRunMessage(
        `Search completed! Collected: ${summary.total_collected}, Relevant: ${summary.relevant_count}, Duplicates: ${summary.duplicate_count}`
      );
      setTimeout(() => setRunMessage(null), 8000);
    } catch (err: any) {
      console.error('Run failed:', err);
      setRunMessage(`Run failed: ${err.message || 'Error occurred'}`);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} isRunning={isRunning} />

      {/* Global Status Banner when run finishes or errors */}
      {runMessage && (
        <div className="bg-emerald-950/80 border-b border-emerald-500/30 text-emerald-300 px-4 py-2.5 text-center text-xs font-semibold">
          {runMessage}
        </div>
      )}

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <Overview
            onSelectOpp={(opp) => setSelectedOpp(opp)}
            isRunning={isRunning}
            onTriggerRun={handleTriggerRun}
          />
        )}
        {activeTab === 'opportunities' && (
          <Opportunities onSelectOpp={(opp) => setSelectedOpp(opp)} />
        )}
        {activeTab === 'sources' && <Sources />}
        {activeTab === 'discovery' && <Discovery />}
        {activeTab === 'profile' && <Profile />}
        {activeTab === 'reports' && <Reports />}
      </main>

      {/* Opportunity Details Modal */}
      <OpportunityModal opp={selectedOpp} onClose={() => setSelectedOpp(null)} />
    </div>
  );
};

export default App;

