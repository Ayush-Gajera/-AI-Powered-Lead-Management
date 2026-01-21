import { useState, useEffect } from 'react';
import { getLeads, sendEmail } from '../api';

export default function SendEmail() {
  const [leads, setLeads] = useState([]);
  const [formData, setFormData] = useState({
    lead_id: '',
    subject: '',
    body: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    loadLeads();
  }, []);

  const loadLeads = async () => {
    try {
      const data = await getLeads();
      setLeads(data);
    } catch (error) {
      console.error('Error loading leads:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage(null);

    try {
      const result = await sendEmail(formData);
      setMessage({
        type: 'success',
        text: result.message || 'Email sent successfully!',
      });
      setFormData({ lead_id: '', subject: '', body: '' });
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.message || 'Failed to send email',
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

  const selectedLead = leads.find((l) => l.id === formData.lead_id);

  return (
    <div className="container mx-auto px-6 py-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-slate-900 mb-2">Send Email</h2>
        <p className="text-slate-600">Compose and send emails to your leads</p>
      </div>

      <div className="max-w-3xl mx-auto">
        <div className="card">
          {message && (
            <div
              className={`mb-6 p-4 rounded-lg ${
                message.type === 'success'
                  ? 'bg-success-50 text-success-800 border border-success-200'
                  : 'bg-danger-50 text-danger-800 border border-danger-200'
              }`}
            >
              {message.text}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Lead Selection */}
            <div>
              <label className="label">Select Lead *</label>
              <select
                name="lead_id"
                value={formData.lead_id}
                onChange={handleChange}
                className="input"
                required
              >
                <option value="">Choose a lead...</option>
                {leads.map((lead) => (
                  <option key={lead.id} value={lead.id}>
                    {lead.name} ({lead.email}) - {lead.company || 'No Company'}
                  </option>
                ))}
              </select>
              {selectedLead && (
                <p className="mt-2 text-sm text-slate-600">
                  Status:{' '}
                  <span className={`badge-${selectedLead.status.toLowerCase().replace('_', '-')}`}>
                    {selectedLead.status}
                  </span>
                </p>
              )}
            </div>

            {/* Subject */}
            <div>
              <label className="label">Email Subject *</label>
              <input
                type="text"
                name="subject"
                value={formData.subject}
                onChange={handleChange}
                className="input"
                required
                placeholder="Quick question about..."
              />
            </div>

            {/* Body */}
            <div>
              <label className="label">Email Body *</label>
              <textarea
                name="body"
                value={formData.body}
                onChange={handleChange}
                className="input"
                required
                rows="10"
                placeholder={`Hi [Name],\n\nI hope this email finds you well...\n\nBest regards,\nYour Name`}
              />
              <p className="mt-2 text-sm text-slate-500">
                Tip: Personalize your email for better response rates
              </p>
            </div>

            {/* Submit Button */}
            <div className="flex items-center space-x-4">
              <button
                type="submit"
                disabled={submitting}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {submitting ? (
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
                    Sending...
                  </>
                ) : (
                  'Send Email'
                )}
              </button>
              <button
                type="button"
                onClick={() => setFormData({ lead_id: '', subject: '', body: '' })}
                className="btn-secondary"
              >
                Clear Form
              </button>
            </div>
          </form>
        </div>

        {/* Info Box */}
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h4 className="font-semibold text-blue-900 mb-2">📧 How Reply Tracking Works</h4>
          <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
            <li>Each email is sent with a unique Message-ID header</li>
            <li>When recipients reply, their email client includes this ID in reply headers</li>
            <li>Click "Sync Replies" on the Dashboard to scan your inbox</li>
            <li>Matching replies automatically update lead status to "REPLIED"</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
