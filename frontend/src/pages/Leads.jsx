import { useState, useEffect } from 'react';
import { createLead, getLeads } from '../api';

export default function Leads() {
    const [leads, setLeads] = useState([]);
    const [loading, setLoading] = useState(true);
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        company: '',
    });
    const [submitting, setSubmitting] = useState(false);
    const [message, setMessage] = useState(null);
    const [priorityFilter, setPriorityFilter] = useState('ALL');
    const [intentFilter, setIntentFilter] = useState('ALL');

    useEffect(() => {
        loadLeads();
    }, []);

    const loadLeads = async () => {
        try {
            const data = await getLeads();
            setLeads(data);
        } catch (error) {
            console.error('Error loading leads:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSubmitting(true);
        setMessage(null);

        try {
            await createLead(formData);
            setMessage({
                type: 'success',
                text: 'Lead created successfully!',
            });
            setFormData({ name: '', email: '', company: '' });
            await loadLeads();
        } catch (error) {
            setMessage({
                type: 'error',
                text: error.message || 'Failed to create lead',
            });
        } finally {
            setSubmitting(false);
        }
    };

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const formatDate = (dateString) => {
        if (!dateString) return '-';
        return new Date(dateString).toLocaleString();
    };

    // Filter and sort leads
    const filteredLeads = leads
        .filter((lead) => {
            if (priorityFilter !== 'ALL' && lead.lead_priority !== priorityFilter) return false;
            if (intentFilter !== 'ALL' && lead.last_reply_intent !== intentFilter) return false;
            return true;
        })
        .sort((a, b) => {
            // Sort by priority rank first (HIGH > MEDIUM > LOW > IGNORE)
            const priorityRank = { HIGH: 4, MEDIUM: 3, LOW: 2, IGNORE: 1 };
            const aPriority = priorityRank[a.lead_priority] || 0;
            const bPriority = priorityRank[b.lead_priority] || 0;

            if (aPriority !== bPriority) {
                return bPriority - aPriority;
            }

            // Then by score (descending)
            return (b.lead_score || 0) - (a.lead_score || 0);
        });

    return (
        <div className="container mx-auto px-6 py-8">
            <div className="mb-8">
                <h2 className="text-3xl font-bold text-slate-900 mb-2">Leads Management</h2>
                <p className="text-slate-600">Add and manage your leads with AI-powered scoring</p>
            </div>

            {/* Add Lead Form */}
            <div className="card mb-8">
                <h3 className="text-xl font-semibold text-slate-900 mb-4">Add New Lead</h3>

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

                <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="label">Name *</label>
                        <input
                            type="text"
                            name="name"
                            value={formData.name}
                            onChange={handleChange}
                            className="input"
                            required
                            placeholder="John Doe"
                        />
                    </div>

                    <div>
                        <label className="label">Email *</label>
                        <input
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            className="input"
                            required
                            placeholder="john@example.com"
                        />
                    </div>

                    <div>
                        <label className="label">Company</label>
                        <input
                            type="text"
                            name="company"
                            value={formData.company}
                            onChange={handleChange}
                            className="input"
                            placeholder="Acme Inc."
                        />
                    </div>

                    <div className="md:col-span-3">
                        <button
                            type="submit"
                            disabled={submitting}
                            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {submitting ? 'Adding...' : 'Add Lead'}
                        </button>
                    </div>
                </form>
            </div>

            {/* Filters */}
            <div className="card mb-4">
                <div className="flex items-center gap-4 flex-wrap">
                    <div>
                        <label className="label">Filter by Priority</label>
                        <select
                            value={priorityFilter}
                            onChange={(e) => setPriorityFilter(e.target.value)}
                            className="input w-40"
                        >
                            <option value="ALL">All</option>
                            <option value="HIGH">High</option>
                            <option value="MEDIUM">Medium</option>
                            <option value="LOW">Low</option>
                            <option value="IGNORE">Ignore</option>
                        </select>
                    </div>

                    <div>
                        <label className="label">Filter by Intent</label>
                        <select
                            value={intentFilter}
                            onChange={(e) => setIntentFilter(e.target.value)}
                            className="input w-48"
                        >
                            <option value="ALL">All</option>
                            <option value="INTERESTED">Interested</option>
                            <option value="ASKING_PRICE">Asking Price</option>
                            <option value="MEETING">Meeting</option>
                            <option value="NOT_INTERESTED">Not Interested</option>
                            <option value="UNSUBSCRIBE">Unsubscribe</option>
                            <option value="SPAM">Spam</option>
                            <option value="OTHER">Other</option>
                        </select>
                    </div>

                    <div className="ml-auto">
                        <p className="text-sm text-slate-600 mt-6">
                            Showing {filteredLeads.length} of {leads.length} leads
                        </p>
                    </div>
                </div>
            </div>

            {/* Leads Table */}
            <div className="card">
                <h3 className="text-xl font-semibold text-slate-900 mb-4">All Leads</h3>

                {loading ? (
                    <div className="text-center py-8 text-slate-500">Loading leads...</div>
                ) : filteredLeads.length === 0 ? (
                    <div className="text-center py-8 text-slate-500">
                        {leads.length === 0 ? 'No leads yet. Add your first lead above!' : 'No leads match the filters.'}
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-slate-200">
                                    <th className="text-left py-3 px-4 font-semibold text-slate-700">Name</th>
                                    <th className="text-left py-3 px-4 font-semibold text-slate-700">Email</th>
                                    <th className="text-left py-3 px-4 font-semibold text-slate-700">Company</th>
                                    <th className="text-left py-3 px-4 font-semibold text-slate-700">Status</th>
                                    <th className="text-left py-3 px-4 font-semibold text-slate-700">Score</th>
                                    <th className="text-left py-3 px-4 font-semibold text-slate-700">Priority</th>
                                    <th className="text-left py-3 px-4 font-semibold text-slate-700">Last Intent</th>
                                    <th className="text-left py-3 px-4 font-semibold text-slate-700">Last Reply</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredLeads.map((lead) => (
                                    <tr key={lead.id} className="border-b border-slate-100 hover:bg-slate-50">
                                        <td className="py-3 px-4 font-medium text-slate-900">{lead.name}</td>
                                        <td className="py-3 px-4 text-slate-600">{lead.email}</td>
                                        <td className="py-3 px-4 text-slate-600">{lead.company || '-'}</td>
                                        <td className="py-3 px-4">
                                            <span className={`badge-${lead.status.toLowerCase().replace('_', '-')}`}>
                                                {lead.status}
                                            </span>
                                        </td>
                                        <td className="py-3 px-4">
                                            <div className="flex items-center">
                                                <span className="font-semibold text-lg text-slate-900">{lead.lead_score || 0}</span>
                                                <span className="text-xs text-slate-500 ml-1">/100</span>
                                            </div>
                                        </td>
                                        <td className="py-3 px-4">
                                            <span className={`badge-${lead.lead_priority.toLowerCase()}`}>
                                                {lead.lead_priority}
                                            </span>
                                        </td>
                                        <td className="py-3 px-4 text-sm text-slate-600">
                                            {lead.last_reply_intent || '-'}
                                        </td>
                                        <td className="py-3 px-4 text-sm text-slate-600">
                                            {formatDate(lead.last_replied_at)}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
}
