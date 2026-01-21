/**
 * API client for backend communication
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Create a new lead
 */
export async function createLead(leadData) {
  const response = await fetch(`${API_BASE_URL}/leads`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(leadData),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create lead');
  }

  return response.json();
}

/**
 * Get all leads
 */
export async function getLeads() {
  const response = await fetch(`${API_BASE_URL}/leads`);

  if (!response.ok) {
    throw new Error('Failed to fetch leads');
  }

  return response.json();
}

/**
 * Send email to a lead
 */
export async function sendEmail(emailData) {
  const response = await fetch(`${API_BASE_URL}/emails/send`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(emailData),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to send email');
  }

  return response.json();
}

/**
 * Get all outbound emails
 */
export async function getOutboundEmails() {
  const response = await fetch(`${API_BASE_URL}/emails/outbound`);

  if (!response.ok) {
    throw new Error('Failed to fetch outbound emails');
  }

  return response.json();
}

/**
 * Sync replies from inbox
 */
export async function syncReplies() {
  const response = await fetch(`${API_BASE_URL}/sync/replies`, {
    method: 'POST',
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to sync replies');
  }

  return response.json();
}

// ============================================
// Replies API
// ============================================

/**
 * Get all inbound replies
 */
export async function getInboundReplies() {
  const response = await fetch(`${API_BASE_URL}/replies/inbound-replies`);

  if (!response.ok) {
    throw new Error('Failed to fetch replies');
  }

  return response.json();
}

/**
 * Generate next best action for a reply
 */
export async function generateNextAction(replyId, force = false) {
  const response = await fetch(
    `${API_BASE_URL}/replies/${replyId}/generate-next-action?force=${force}`,
    { method: 'POST' }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to generate next action');
  }

  return response.json();
}

/**
 * Generate draft reply
 */
export async function generateDraft(replyId, tone = 'FRIENDLY', force = false) {
  const response = await fetch(
    `${API_BASE_URL}/replies/${replyId}/generate-draft?tone=${tone}&force=${force}`,
    { method: 'POST' }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to generate draft');
  }

  return response.json();
}

/**
 * Upload attachment
 */
export async function uploadAttachment(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/replies/upload-attachment`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to upload file');
  }

  return response.json();
}

/**
 * Send draft reply
 */
export async function sendDraftReply(replyId, data) {
  const response = await fetch(`${API_BASE_URL}/replies/${replyId}/send-draft`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to send draft');
  }

  return response.json();
}

