import { useState, useEffect } from 'react';
import { getOutboundEmails, getLeads } from '../api';

export default function OutboundEmails() {
    const [emails, setEmails] = useState([]);
    const [leads, setLeads] = useState({});
    const [loading, setLoading] = useState(true);
    const [expandedId, setExpandedId] = useState(null);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [emailsData, leadsData] = await Promise.all([getOutboundEmails(), getLeads()]);

            // Create a map of lead_id -> lead for easy lookup
            const leadsMap = {};
            leadsData.forEach((lead) => {
                leadsMap[lead.id] = lead;
            });

            setEmails(emailsData);
            setLeads(leadsMap);
        } catch (error) {
            console.error('Error loading data:', error);
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleString();
    };

    const toggleExpanded = (emailId) => {
        setExpandedId(expandedId === emailId ? null : emailId);
    };

    return (
        <div className="container mx-auto px-6 py-8">
            <div className="mb-8">
                <h2 className="text-3xl font-bold text-slate-900 mb-2">Outbound Emails</h2>
                <p className="text-slate-600">View all sent emails with AI-powered reply analysis</p>
            </div>

            <div className="card">
                {loading ? (
                    <div className="text-center py-8 text-slate-500">Loading emails...</div>
                ) : emails.length === 0 ? (
                    <div className="text-center py-8 text-slate-500">
                        No emails sent yet. Go to "Send Email" to compose your first email!
                    </div>
                ) : (
                    <div className="space-y-4">
                        {emails.map((email) => {
                            const lead = leads[email.lead_id];
                            const isExpanded = expandedId === email.id;

                            return (
                                <div
                                    key={email.id}
                                    className="p-5 border border-slate-200 rounded-lg hover:border-primary-300 transition-all duration-200 hover:shadow-md"
                                >
                                    <div className="flex items-start justify-between mb-3">
                                        <div className="flex-1">
                                            <h3 className="text-lg font-semibold text-slate-900 mb-1">
                                                {email.subject}
                                            </h3>
                                            {lead && (
                                                <p className="text-sm text-slate-600">
                                                    To: <span className="font-medium">{lead.name}</span> ({lead.email})
                                                    {lead.company && ` - ${lead.company}`}
                                                </p>
                                            )}
                                        </div>
                                        <div className="ml-4 flex gap-2">
                                            {email.is_replied ? (
                                                <>
                                                    {email.priority && (
                                                        <span className={`badge-${email.priority.toLowerCase()}`}>
                                                            {email.priority}
                                                        </span>
                                                    )}
                                                    <span className="badge bg-success-100 text-success-700 flex items-center">
                                                        <svg
                                                            className="w-4 h-4 mr-1"
                                                            fill="currentColor"
                                                            viewBox="0 0 20 20"
                                                        >
                                                            <path
                                                                fillRule="evenodd"
                                                                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                                                clipRule="evenodd"
                                                            />
                                                        </svg>
                                                        Replied
                                                    </span>
                                                </>
                                            ) : (
                                                <span className="badge bg-slate-100 text-slate-600">No Reply</span>
                                            )}
                                        </div>
                                    </div>

                                    {/* AI Scoring Display (only if replied) */}
                                    {email.is_replied && email.reply_score !== null && (
                                        <div className="mb-3 p-3 bg-slate-50 rounded-lg">
                                            <div className="grid grid-cols-3 gap-4">
                                                <div>
                                                    <p className="text-xs text-slate-600 mb-1">AI Score</p>
                                                    <div className="flex items-baseline">
                                                        <span className="text-2xl font-bold text-slate-900">
                                                            {email.reply_score}
                                                        </span>
                                                        <span className="text-sm text-slate-500 ml-1">/100</span>
                                                    </div>
                                                </div>
                                                <div>
                                                    <p className="text-xs text-slate-600 mb-1">Intent</p>
                                                    <p className="text-sm font-semibold text-slate-900">
                                                        {email.intent || 'N/A'}
                                                    </p>
                                                </div>
                                                <div>
                                                    <p className="text-xs text-slate-600 mb-1">Confidence</p>
                                                    <p className="text-sm font-semibold text-slate-900">
                                                        {email.confidence
                                                            ? `${(email.confidence * 100).toFixed(0)}%`
                                                            : 'N/A'}
                                                    </p>
                                                </div>
                                            </div>

                                            {/* Expandable Reasons Section */}
                                            {email.is_replied && (
                                                <div className="mt-2">
                                                    <button
                                                        onClick={() => toggleExpanded(email.id)}
                                                        className="text-sm text-primary-600 hover:text-primary-700 font-medium flex items-center"
                                                    >
                                                        {isExpanded ? (
                                                            <>
                                                                <svg
                                                                    className="w-4 h-4 mr-1"
                                                                    fill="none"
                                                                    stroke="currentColor"
                                                                    viewBox="0 0 24 24"
                                                                >
                                                                    <path
                                                                        strokeLinecap="round"
                                                                        strokeLinejoin="round"
                                                                        strokeWidth={2}
                                                                        d="M5 15l7-7 7 7"
                                                                    />
                                                                </svg>
                                                                Hide Details
                                                            </>
                                                        ) : (
                                                            <>
                                                                <svg
                                                                    className="w-4 h-4 mr-1"
                                                                    fill="none"
                                                                    stroke="currentColor"
                                                                    viewBox="0 0 24 24"
                                                                >
                                                                    <path
                                                                        strokeLinecap="round"
                                                                        strokeLinejoin="round"
                                                                        strokeWidth={2}
                                                                        d="M19 9l-7 7-7-7"
                                                                    />
                                                                </svg>
                                                                View AI Analysis
                                                            </>
                                                        )}
                                                    </button>
                                                </div>
                                            )}
                                        </div>
                                    )}

                                    {/* Expanded Reasons Details */}
                                    {isExpanded && email.is_replied && (
                                        <div className="mb-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                                            <p className="text-sm font-semibold text-blue-900 mb-2">
                                                AI Analysis Reasons:
                                            </p>
                                            {/* Note: reasons will come from inbound_replies table */}
                                            <p className="text-sm text-blue-800">
                                                Reasons available in inbound replies table
                                            </p>
                                        </div>
                                    )}

                                    <div className="mb-3">
                                        <p className="text-sm text-slate-700 whitespace-pre-wrap line-clamp-3">
                                            {email.body}
                                        </p>
                                    </div>

                                    <div className="flex items-center justify-between text-xs text-slate-500 pt-3 border-t border-slate-100">
                                        <span>Sent: {formatDate(email.sent_at)}</span>
                                        <span className="font-mono text-xs bg-slate-100 px-2 py-1 rounded">
                                            ID: {email.message_id.substring(0, 20)}...
                                        </span>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* Stats Summary */}
            {emails.length > 0 && (
                <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="card bg-gradient-to-br from-primary-50 to-primary-100 border-primary-200">
                        <p className="text-sm font-medium text-primary-700 mb-1">Total Sent</p>
                        <p className="text-3xl font-bold text-primary-900">{emails.length}</p>
                    </div>
                    <div className="card bg-gradient-to-br from-success-50 to-success-100 border-success-200">
                        <p className="text-sm font-medium text-success-700 mb-1">Replies Received</p>
                        <p className="text-3xl font-bold text-success-900">
                            {emails.filter((e) => e.is_replied).length}
                        </p>
                    </div>
                    <div className="card bg-gradient-to-br from-red-50 to-red-100 border-red-200">
                        <p className="text-sm font-medium text-red-700 mb-1">High Priority</p>
                        <p className="text-3xl font-bold text-red-900">
                            {emails.filter((e) => e.priority === 'HIGH').length}
                        </p>
                    </div>
                    <div className="card bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
                        <p className="text-sm font-medium text-orange-700 mb-1">Medium Priority</p>
                        <p className="text-3xl font-bold text-orange-900">
                            {emails.filter((e) => e.priority === 'MEDIUM').length}
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
}
