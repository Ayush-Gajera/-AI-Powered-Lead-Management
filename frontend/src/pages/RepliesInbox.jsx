import { useState, useEffect, useRef } from 'react';
import {
    getInboundReplies,
    generateNextAction,
    generateDraft,
    uploadAttachment,
    sendDraftReply,
} from '../api';

export default function RepliesInbox() {
    const [replies, setReplies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [expandedReply, setExpandedReply] = useState(null);
    const [message, setMessage] = useState(null);

    // State for each reply's actions/drafts
    const [replyStates, setReplyStates] = useState({});

    const fileInputRef = useRef(null);

    useEffect(() => {
        loadReplies();
    }, []);

    const loadReplies = async () => {
        try {
            const data = await getInboundReplies();
            setReplies(data);

            // Initialize state for each reply
            const states = {};
            data.forEach((reply) => {
                states[reply.id] = {
                    generatingAction: false,
                    generatingDraft: false,
                    sending: false,
                    selectedTone: reply.draft_tone || 'FRIENDLY',
                    draftSubject: reply.draft_subject || '',
                    draftBody: reply.draft_body || '',
                    attachments: reply.attachments || [],
                    uploadingFile: false,
                };
            });
            setReplyStates(states);
        } catch (error) {
            console.error('Error loading replies:', error);
            showMessage('error', error.message);
        } finally {
            setLoading(false);
        }
    };

    const showMessage = (type, text) => {
        setMessage({ type, text });
        setTimeout(() => setMessage(null), 5000);
    };

    const handleGenerateNextAction = async (replyId, force = false) => {
        setReplyStates((prev) => ({
            ...prev,
            [replyId]: { ...prev[replyId], generatingAction: true },
        }));

        try {
            const action = await generateNextAction(replyId, force);

            // Update reply in list
            setReplies((prev) =>
                prev.map((r) =>
                    r.id === replyId
                        ? {
                            ...r,
                            next_action_title: action.next_action_title,
                            next_action_steps: action.next_action_steps,
                            urgency: action.urgency,
                            followup_days: action.followup_days,
                            suggested_tone: action.suggested_tone,
                        }
                        : r
                )
            );

            showMessage('success', 'Next action generated!');
        } catch (error) {
            showMessage('error', error.message);
        } finally {
            setReplyStates((prev) => ({
                ...prev,
                [replyId]: { ...prev[replyId], generatingAction: false },
            }));
        }
    };

    const handleGenerateDraft = async (replyId, force = false) => {
        const state = replyStates[replyId];
        const tone = state?.selectedTone || 'FRIENDLY';

        setReplyStates((prev) => ({
            ...prev,
            [replyId]: { ...prev[replyId], generatingDraft: true },
        }));

        try {
            const draft = await generateDraft(replyId, tone, force);

            setReplyStates((prev) => ({
                ...prev,
                [replyId]: {
                    ...prev[replyId],
                    draftSubject: draft.subject,
                    draftBody: draft.body,
                    generatingDraft: false,
                },
            }));

            showMessage(
                'success',
                draft.cached ? 'Draft loaded from cache' : 'Draft generated!'
            );
        } catch (error) {
            showMessage('error', error.message);
            setReplyStates((prev) => ({
                ...prev,
                [replyId]: { ...prev[replyId], generatingDraft: false },
            }));
        }
    };

    const handleFileSelect = async (replyId, event) => {
        const files = Array.from(event.target.files);

        setReplyStates((prev) => ({
            ...prev,
            [replyId]: { ...prev[replyId], uploadingFile: true },
        }));

        try {
            const uploadedFiles = [];

            for (const file of files) {
                const fileData = await uploadAttachment(file);
                uploadedFiles.push(fileData);
            }

            setReplyStates((prev) => ({
                ...prev,
                [replyId]: {
                    ...prev[replyId],
                    attachments: [...(prev[replyId].attachments || []), ...uploadedFiles],
                    uploadingFile: false,
                },
            }));

            showMessage('success', `${files.length} file(s) uploaded`);
        } catch (error) {
            showMessage('error', error.message);
            setReplyStates((prev) => ({
                ...prev,
                [replyId]: { ...prev[replyId], uploadingFile: false },
            }));
        }
    };

    const handleRemoveAttachment = (replyId, index) => {
        setReplyStates((prev) => ({
            ...prev,
            [replyId]: {
                ...prev[replyId],
                attachments: prev[replyId].attachments.filter((_, i) => i !== index),
            },
        }));
    };

    const handleSendDraft = async (replyId) => {
        const state = replyStates[replyId];

        if (!state.draftSubject || !state.draftBody) {
            showMessage('error', 'Please generate a draft first');
            return;
        }

        setReplyStates((prev) => ({
            ...prev,
            [replyId]: { ...prev[replyId], sending: true },
        }));

        try {
            await sendDraftReply(replyId, {
                edited_subject: state.draftSubject,
                edited_body: state.draftBody,
                attachments: state.attachments,
            });

            showMessage('success', 'Reply sent successfully!');

            // Reload replies
            await loadReplies();
        } catch (error) {
            showMessage('error', error.message);
        } finally {
            setReplyStates((prev) => ({
                ...prev,
                [replyId]: { ...prev[replyId], sending: false },
            }));
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return '-';
        return new Date(dateString).toLocaleString();
    };

    const toggleExpanded = (replyId) => {
        setExpandedReply(expandedReply === replyId ? null : replyId);
    };

    return (
        <div className="container mx-auto px-6 py-8">
            <div className="mb-8">
                <h2 className="text-3xl font-bold text-slate-900 mb-2">Replies Inbox</h2>
                <p className="text-slate-600">
                    Manage inbound replies with AI-powered next actions and draft responses
                </p>
            </div>

            {/* Global Message */}
            {message && (
                <div
                    className={`mb-6 p-4 rounded-lg ${message.type === 'success'
                            ? 'bg-success-50 text-success-800 border border-success-200'
                            : 'bg-danger-50 text-danger-800 border border-danger-200'
                        }`}
                >
                    {message.text}
                </div>
            )}

            {loading ? (
                <div className="text-center py-12 text-slate-500">Loading replies...</div>
            ) : replies.length === 0 ? (
                <div className="card text-center py-12 text-slate-500">
                    <p className="text-lg mb-2">No replies yet</p>
                    <p>Replies will appear here after you sync your inbox</p>
                </div>
            ) : (
                <div className="space-y-6">
                    {replies.map((reply) => {
                        const lead = reply.leads;
                        const outbound = reply.outbound_emails;
                        const state = replyStates[reply.id] || {};
                        const isExpanded = expandedReply === reply.id;

                        return (
                            <div key={reply.id} className="card">
                                {/* Reply Header */}
                                <div className="flex items-start justify-between mb-4 pb-4 border-b border-slate-200">
                                    <div className="flex-1">
                                        <h3 className="text-lg font-semibold text-slate-900 mb-1">
                                            {lead?.name || 'Unknown'} • {lead?.email || ''}
                                        </h3>
                                        {lead?.company && (
                                            <p className="text-sm text-slate-600 mb-2">{lead.company}</p>
                                        )}
                                        <div className="flex items-center gap-3 flex-wrap">
                                            <span className="text-sm text-slate-500">
                                                {formatDate(reply.received_at)}
                                            </span>
                                            <span className={`badge-${reply.priority?.toLowerCase()}`}>
                                                {reply.priority}
                                            </span>
                                            <span className="badge bg-slate-100 text-slate-700">
                                                {reply.intent}
                                            </span>
                                            <span className="text-sm font-semibold text-slate-900">
                                                Score: {reply.reply_score}/100
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                {/* Reply Preview */}
                                <div className="mb-4">
                                    <p className="text-sm text-slate-700 whitespace-pre-wrap line-clamp-3">
                                        {reply.body_preview}
                                    </p>
                                </div>

                                {/* Next Action Card */}
                                {reply.next_action_title ? (
                                    <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                                        <div className="flex items-start justify-between mb-2">
                                            <h4 className="font-semibold text-blue-900">
                                                📋 {reply.next_action_title}
                                            </h4>
                                            <div className="flex items-center gap-2">
                                                {reply.urgency && (
                                                    <span
                                                        className={`badge ${reply.urgency === 'NOW'
                                                                ? 'badge-high'
                                                                : reply.urgency === 'TODAY'
                                                                    ? 'badge-medium'
                                                                    : 'badge-low'
                                                            }`}
                                                    >
                                                        {reply.urgency}
                                                    </span>
                                                )}
                                                <button
                                                    onClick={() => handleGenerateNextAction(reply.id, true)}
                                                    disabled={state.generatingAction}
                                                    className="text-xs text-blue-600 hover:text-blue-700 underline"
                                                >
                                                    Regenerate
                                                </button>
                                            </div>
                                        </div>
                                        <ul className="space-y-1">
                                            {reply.next_action_steps?.map((step, idx) => (
                                                <li key={idx} className="text-sm text-blue-800 flex items-start">
                                                    <span className="mr-2">•</span>
                                                    {step}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                ) : (
                                    <button
                                        onClick={() => handleGenerateNextAction(reply.id)}
                                        disabled={state.generatingAction}
                                        className="btn-primary mb-4 disabled:opacity-50"
                                    >
                                        {state.generatingAction ? 'Generating...' : '🤖 Generate Next Action'}
                                    </button>
                                )}

                                {/* Draft Reply Section - Expandable */}
                                <div className="border-t border-slate-200 pt-4">
                                    <button
                                        onClick={() => toggleExpanded(reply.id)}
                                        className="w-full flex items-center justify-between text-left font-semibold text-slate-900 hover:text-primary-600"
                                    >
                                        <span>✉️ Draft Reply {reply.draft_status ? `(${reply.draft_status})` : ''}</span>
                                        <svg
                                            className={`w-5 h-5 transform transition-transform ${isExpanded ? 'rotate-180' : ''
                                                }`}
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
                                    </button>

                                    {isExpanded && (
                                        <div className="mt-4 space-y-4">
                                            {/* Tone Selector */}
                                            <div>
                                                <label className="label">Tone</label>
                                                <select
                                                    value={state.selectedTone}
                                                    onChange={(e) =>
                                                        setReplyStates((prev) => ({
                                                            ...prev,
                                                            [reply.id]: { ...prev[reply.id], selectedTone: e.target.value },
                                                        }))
                                                    }
                                                    className="input w-48"
                                                >
                                                    <option value="FORMAL">Formal</option>
                                                    <option value="FRIENDLY">Friendly</option>
                                                    <option value="SHORT">Short</option>
                                                </select>
                                            </div>

                                            {/* Generate Draft Button */}
                                            {!state.draftSubject && (
                                                <button
                                                    onClick={() => handleGenerateDraft(reply.id)}
                                                    disabled={state.generatingDraft}
                                                    className="btn-primary disabled:opacity-50"
                                                >
                                                    {state.generatingDraft ? 'Generating...' : '🤖 Generate Draft'}
                                                </button>
                                            )}

                                            {/* Draft Editor */}
                                            {state.draftSubject && (
                                                <>
                                                    <div>
                                                        <label className="label">Subject</label>
                                                        <input
                                                            type="text"
                                                            value={state.draftSubject}
                                                            onChange={(e) =>
                                                                setReplyStates((prev) => ({
                                                                    ...prev,
                                                                    [reply.id]: { ...prev[reply.id], draftSubject: e.target.value },
                                                                }))
                                                            }
                                                            className="input"
                                                        />
                                                    </div>

                                                    <div>
                                                        <label className="label">Body</label>
                                                        <textarea
                                                            value={state.draftBody}
                                                            onChange={(e) =>
                                                                setReplyStates((prev) => ({
                                                                    ...prev,
                                                                    [reply.id]: { ...prev[reply.id], draftBody: e.target.value },
                                                                }))
                                                            }
                                                            className="input min-h-[200px] font-mono text-sm"
                                                            rows={10}
                                                        />
                                                    </div>

                                                    {/* Attachments */}
                                                    <div>
                                                        <label className="label">Attachments</label>
                                                        <input
                                                            ref={fileInputRef}
                                                            type="file"
                                                            multiple
                                                            onChange={(e) => handleFileSelect(reply.id, e)}
                                                            className="hidden"
                                                        />
                                                        <button
                                                            onClick={() => fileInputRef.current?.click()}
                                                            disabled={state.uploadingFile}
                                                            className="btn bg-slate-200 text-slate-700 hover:bg-slate-300 mb-2"
                                                        >
                                                            {state.uploadingFile ? 'Uploading...' : '📎 Add Files'}
                                                        </button>

                                                        {state.attachments?.length > 0 && (
                                                            <div className="space-y-2 mt-2">
                                                                {state.attachments.map((att, idx) => (
                                                                    <div
                                                                        key={idx}
                                                                        className="flex items-center justify-between p-2 bg-slate-50 rounded"
                                                                    >
                                                                        <span className="text-sm text-slate-700">{att.file_name}</span>
                                                                        <button
                                                                            onClick={() => handleRemoveAttachment(reply.id, idx)}
                                                                            className="text-red-600 hover:text-red-700 text-sm"
                                                                        >
                                                                            Remove
                                                                        </button>
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        )}
                                                    </div>

                                                    {/* Action Buttons */}
                                                    <div className="flex items-center gap-3">
                                                        <button
                                                            onClick={() => handleSendDraft(reply.id)}
                                                            disabled={state.sending}
                                                            className="btn-primary disabled:opacity-50"
                                                        >
                                                            {state.sending ? 'Sending...' : '📤 Send Reply'}
                                                        </button>
                                                        <button
                                                            onClick={() => handleGenerateDraft(reply.id, true)}
                                                            disabled={state.generatingDraft}
                                                            className="btn bg-slate-200 text-slate-700 hover:bg-slate-300"
                                                        >
                                                            🔄 Regenerate Draft
                                                        </button>
                                                    </div>
                                                </>
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
