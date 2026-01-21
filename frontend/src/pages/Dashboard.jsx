import { useState, useEffect } from 'react';
import { getLeads, syncReplies } from '../api';

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalLeads: 0,
    emailed: 0,
    replied: 0,
    highPriority: 0,
    mediumPriority: 0,
    lowPriority: 0,
    ignorePriority: 0,
  });
  const [syncing, setSyncing] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const leads = await getLeads();
      const totalLeads = leads.length;
      const emailed = leads.filter((l) => ['EMAILED', 'REPLIED'].includes(l.status)).length;
      const replied = leads.filter((l) => l.status === 'REPLIED').length;

      // Calculate priority stats
      const highPriority = leads.filter((l) => l.lead_priority === 'HIGH').length;
      const mediumPriority = leads.filter((l) => l.lead_priority === 'MEDIUM').length;
      const lowPriority = leads.filter((l) => l.lead_priority === 'LOW').length;
      const ignorePriority = leads.filter((l) => l.lead_priority === 'IGNORE').length;

      setStats({ totalLeads, emailed, replied, highPriority, mediumPriority, lowPriority, ignorePriority });
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const handleSyncReplies = async () => {
    setSyncing(true);
    setMessage(null);

    try {
      const result = await syncReplies();
      setMessage({
        type: 'success',
        text: result.message || `Found ${result.replies_found} new replies`,
      });
      // Reload stats after syncing
      await loadStats();
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.message || 'Failed to sync replies',
      });
    } finally {
      setSyncing(false);
    }
  };

  return (
    <div className="container mx-auto px-6 py-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-slate-900 mb-2">Dashboard</h2>
        <p className="text-slate-600">Track your email campaigns and replies</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card bg-gradient-to-br from-primary-50 to-primary-100 border-primary-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-primary-700 mb-1">Total Leads</p>
              <p className="text-4xl font-bold text-primary-900">{stats.totalLeads}</p>
            </div>
            <div className="w-16 h-16 bg-primary-500 rounded-full flex items-center justify-center">
              <svg
                className="w-8 h-8 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                />
              </svg>
            </div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-blue-700 mb-1">Emailed</p>
              <p className="text-4xl font-bold text-blue-900">{stats.emailed}</p>
            </div>
            <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center">
              <svg
                className="w-8 h-8 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                />
              </svg>
            </div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-success-50 to-success-100 border-success-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-success-700 mb-1">Replied</p>
              <p className="text-4xl font-bold text-success-900">{stats.replied}</p>
            </div>
            <div className="w-16 h-16 bg-success-500 rounded-full flex items-center justify-center">
              <svg
                className="w-8 h-8 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Priority Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="card bg-gradient-to-br from-red-50 to-red-100 border-red-200">
          <p className="text-sm font-medium text-red-700 mb-1">High Priority</p>
          <p className="text-3xl font-bold text-red-900">{stats.highPriority}</p>
        </div>

        <div className="card bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
          <p className="text-sm font-medium text-orange-700 mb-1">Medium Priority</p>
          <p className="text-3xl font-bold text-orange-900">{stats.mediumPriority}</p>
        </div>

        <div className="card bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <p className="text-sm font-medium text-blue-700 mb-1">Low Priority</p>
          <p className="text-3xl font-bold text-blue-900">{stats.lowPriority}</p>
        </div>

        <div className="card bg-gradient-to-br from-slate-50 to-slate-100 border-slate-200">
          <p className="text-sm font-medium text-slate-700 mb-1">Ignored</p>
          <p className="text-3xl font-bold text-slate-900">{stats.ignorePriority}</p>
        </div>
      </div>

      {/* Sync Replies Section */}
      <div className="card">
        <h3 className="text-xl font-semibold text-slate-900 mb-4">Sync Replies</h3>
        <p className="text-slate-600 mb-4">
          Click the button below to scan your inbox for new replies and update lead statuses.
        </p>

        {message && (
          <div
            className={`mb-4 p-4 rounded-lg ${message.type === 'success'
                ? 'bg-success-50 text-success-800 border border-success-200'
                : 'bg-danger-50 text-danger-800 border border-danger-200'
              }`}
          >
            {message.text}
          </div>
        )}

        <button
          onClick={handleSyncReplies}
          disabled={syncing}
          className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {syncing ? (
            <>
              <svg
                className="animate-spin -ml-1 mr-2 h-5 w-5 text-white inline-block"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Syncing...
            </>
          ) : (
            'Sync Replies Now'
          )}
        </button>
      </div>
    </div>
  );
}
