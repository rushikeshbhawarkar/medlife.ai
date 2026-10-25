import { useState, useEffect, useCallback } from 'react';
import Button from '../../components/Button/index.js';
import Spinner from '../../components/Spinner/index.js';
import Banner from '../../components/Banner/index.js';
import Modal from '../../components/Modal/index.js';
import {
  getAdminApplications,
  reviewDoctorApplication,
  getAdminInvitations,
  sendDoctorInvitation,
  downloadAdminApplicationDocument,
} from '../../services/api.js';
import { Shield, UserCheck, Mail, Check, XCircle, Search, Clock, CheckCircle2, FileText, Download, Phone, MapPin } from 'lucide-react';
import './doctor.css';

export default function AdminPortalView({ email, initialTab = 'applications' }) {
  const [activeTab, setActiveTab] = useState(initialTab); // 'applications' | 'invitations'

  useEffect(() => {
    if (initialTab) setActiveTab(initialTab);
  }, [initialTab]);
  const [appStatusFilter, setAppStatusFilter] = useState('pending'); // 'pending', 'approved', 'rejected', 'all'
  const [applications, setApplications] = useState([]);
  const [loadingApps, setLoadingApps] = useState(false);
  const [downloadingDocId, setDownloadingDocId] = useState(null);

  const [invitations, setInvitations] = useState([]);
  const [loadingInvs, setLoadingInvs] = useState(false);
  const [canInvite, setCanInvite] = useState(true); // Super Admin only

  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Review modal
  const [reviewingApp, setReviewingApp] = useState(null);
  const [decision, setDecision] = useState('approve');
  const [reviewNote, setReviewNote] = useState('');
  const [submittingReview, setSubmittingReview] = useState(false);

  const handleDownloadDoc = async (docId, docType) => {
    try {
      setDownloadingDocId(docId);
      setError('');
      await downloadAdminApplicationDocument(docId, `doctor_application_doc_${docId}_${docType}`);
    } catch (err) {
      setError(err.message || 'Unable to download document.');
    } finally {
      setDownloadingDocId(null);
    }
  };

  // Invite modal
  const [inviteModalOpen, setInviteModalOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [submittingInvite, setSubmittingInvite] = useState(false);
  const [inviteModalError, setInviteModalError] = useState('');

  const handleCloseInviteModal = useCallback(() => {
    setInviteModalOpen(false);
    setInviteEmail('');
    setInviteModalError('');
  }, []);

  // Load applications
  const loadApplications = useCallback(async () => {
    try {
      setLoadingApps(true);
      setError('');
      const data = await getAdminApplications(appStatusFilter);
      setApplications(data?.applications || []);
    } catch (e) {
      if (e.status === 403) {
        setError('You are not authorized to review doctor applications. Staff role is required.');
      } else {
        setError(e.message || 'Unable to load doctor applications.');
      }
    } finally {
      setLoadingApps(false);
    }
  }, [appStatusFilter]);

  // Load invitations
  const loadInvitations = useCallback(async () => {
    try {
      setLoadingInvs(true);
      const data = await getAdminInvitations();
      setInvitations(data?.invitations || []);
      setCanInvite(true);
    } catch (e) {
      if (e.status === 403) {
        setCanInvite(false);
      }
    } finally {
      setLoadingInvs(false);
    }
  }, []);

  useEffect(() => {
    if (activeTab === 'applications') loadApplications();
    if (activeTab === 'invitations') loadInvitations();
  }, [activeTab, loadApplications, loadInvitations]);

  // Handle review submit
  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    if (!reviewingApp) return;

    if (decision === 'reject' && !reviewNote.trim()) {
      setError('Please provide a rejection reason. This reason will be emailed directly to the applicant.');
      return;
    }

    setSubmittingReview(true);
    setError('');
    setSuccess('');
    try {
      const res = await reviewDoctorApplication(reviewingApp.id, decision, reviewNote.trim());
      if (decision === 'approve') {
        setSuccess(`Application #${reviewingApp.id} for ${reviewingApp.full_name} approved! An activation link has been sent to ${reviewingApp.email}. The doctor account will be created once the applicant completes password and authenticator activation.`);
      } else {
        setSuccess(`Application #${reviewingApp.id} for ${reviewingApp.full_name} rejected. Decision notification emailed to ${reviewingApp.email}.`);
      }
      setReviewingApp(null);
      setReviewNote('');
      loadApplications();
    } catch (err) {
      setError(err.message || 'Unable to submit application review.');
    } finally {
      setSubmittingReview(false);
    }
  };

  // Handle invite submit
  const handleInviteSubmit = async (e) => {
    e.preventDefault();
    if (!inviteEmail.trim()) return;
    setSubmittingInvite(true);
    setInviteModalError('');
    setError('');
    setSuccess('');
    try {
      const res = await sendDoctorInvitation(inviteEmail.trim().toLowerCase());
      setSuccess(res.message || `Invitation successfully sent to ${inviteEmail}.`);
      setInviteModalOpen(false);
      setInviteEmail('');
      setInviteModalError('');
      loadInvitations();
    } catch (err) {
      const msg = err.message || 'Unable to send invitation.';
      setInviteModalError(msg);
      setError(msg);
    } finally {
      setSubmittingInvite(false);
    }
  };

  return (
    <div className="doctor-system-container">
      {/* Header */}
      <div className="doctor-header-card">
        <div>
          <h2>Medical Administration & Doctor Verification</h2>
          <p>Review credentials, verify medical practitioner licenses, and manage onboarding invitations</p>
        </div>
        {canInvite && (
          <Button variant="primary" size="md" onClick={() => setInviteModalOpen(true)}>
            <Mail size={16} /> Send Doctor Invitation
          </Button>
        )}
      </div>

      {error && <Banner variant="error">{error}</Banner>}
      {success && <Banner variant="info">{success}</Banner>}

      {/* Tabs */}
      <div className="doctor-nav-tabs">
        <button
          className={`doctor-tab-btn ${activeTab === 'applications' ? 'active' : ''}`}
          onClick={() => setActiveTab('applications')}
        >
          <UserCheck size={17} /> Doctor Applications
          {applications.length > 0 && <span className="doctor-badge-count">{applications.length}</span>}
        </button>
        {canInvite && (
          <button
            className={`doctor-tab-btn ${activeTab === 'invitations' ? 'active' : ''}`}
            onClick={() => setActiveTab('invitations')}
          >
            <Mail size={17} /> Sent Invitations
            {invitations.length > 0 && <span className="doctor-badge-count">{invitations.length}</span>}
          </button>
        )}
      </div>

      {/* TAB 1: APPLICATIONS */}
      {activeTab === 'applications' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Status Filter */}
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Filter by Status:</span>
            {['pending', 'approved', 'rejected', 'all'].map((st) => (
              <button
                key={st}
                type="button"
                className={`btn btn-sm ${appStatusFilter === st ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setAppStatusFilter(st)}
                style={{ textTransform: 'capitalize' }}
              >
                {st}
              </button>
            ))}
          </div>

          {loadingApps ? (
            <Spinner />
          ) : applications.length === 0 ? (
            <div className="doctor-empty-state">
              <UserCheck size={48} />
              <h3>No applications in this category</h3>
              <p>No doctor applications found matching the selected filter ({appStatusFilter}).</p>
            </div>
          ) : (
            <div className="requests-list">
              {applications.map((app) => (
                <div key={app.id} className="request-item-card">
                  <div className="request-item-header">
                    <div className="request-item-title">
                      <span>{app.full_name}</span>
                      <span className={`status-pill status-${app.status}`}>{app.status}</span>
                    </div>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      Submitted: {new Date(app.created_at).toLocaleDateString()}
                    </span>
                  </div>

                  <div className="request-details-grid">
                    <div className="request-detail-item">
                      <span className="request-detail-label">Account Email</span>
                      <span className="request-detail-val">{app.email}</span>
                    </div>
                    {app.phone && (
                      <div className="request-detail-item">
                        <span className="request-detail-label">Contact Phone</span>
                        <span className="request-detail-val">{app.phone}</span>
                      </div>
                    )}
                    <div className="request-detail-item">
                      <span className="request-detail-label">Specialty</span>
                      <span className="request-detail-val">{app.specialty}</span>
                    </div>
                    <div className="request-detail-item">
                      <span className="request-detail-label">Experience</span>
                      <span className="request-detail-val">{app.years_experience} years</span>
                    </div>
                    <div className="request-detail-item">
                      <span className="request-detail-label">Registration No.</span>
                      <span className="request-detail-val">{app.registration_number}</span>
                    </div>
                    {app.registration_authority && (
                      <div className="request-detail-item">
                        <span className="request-detail-label">Registration Authority</span>
                        <span className="request-detail-val">{app.registration_authority}</span>
                      </div>
                    )}
                    <div className="request-detail-item">
                      <span className="request-detail-label">Qualifications</span>
                      <span className="request-detail-val">{app.qualifications}</span>
                    </div>
                    {app.clinic_name && (
                      <div className="request-detail-item">
                        <span className="request-detail-label">Clinic / Hospital</span>
                        <span className="request-detail-val">{app.clinic_name}</span>
                      </div>
                    )}
                    {app.address && (
                      <div className="request-detail-item" style={{ gridColumn: '1 / -1' }}>
                        <span className="request-detail-label">Practice Address</span>
                        <span className="request-detail-val">{app.address}</span>
                      </div>
                    )}
                  </div>

                  {app.bio && (
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', margin: 0 }}>
                      <strong>Clinical Bio: </strong> {app.bio}
                    </p>
                  )}

                  {/* Supporting Documents Section */}
                  {app.documents && app.documents.length > 0 && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                      <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                        Supporting Documents ({app.documents.length})
                      </span>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                        {app.documents.map((doc) => (
                          <div
                            key={doc.id}
                            style={{
                              background: 'var(--bg-tertiary)',
                              border: '1px solid var(--border-subtle)',
                              borderRadius: '6px',
                              padding: '0.35rem 0.65rem',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '0.5rem',
                              fontSize: '0.8rem',
                            }}
                          >
                            <FileText size={14} color="var(--red-primary)" />
                            <span style={{ textTransform: 'capitalize' }}>
                              {String(doc.document_type || 'document').replace('_', ' ')}
                            </span>
                            <button
                              type="button"
                              onClick={() => handleDownloadDoc(doc.id, doc.document_type)}
                              disabled={downloadingDocId === doc.id}
                              style={{
                                background: 'transparent',
                                border: 'none',
                                color: 'var(--red-primary)',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                padding: '2px',
                              }}
                              title="Download document file"
                            >
                              <Download size={13} />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {app.review_note && (
                    <div className="request-note-box">
                      <strong>Review Note: </strong> {app.review_note}
                    </div>
                  )}

                  {app.status === 'pending' && (
                    <div className="request-item-actions">
                      <Button
                        type="button"
                        variant="primary"
                        size="sm"
                        onClick={() => {
                          setReviewingApp(app);
                          setDecision('approve');
                          setReviewNote('');
                        }}
                      >
                        <Check size={15} /> Approve Credentials
                      </Button>
                      <Button
                        type="button"
                        variant="danger"
                        size="sm"
                        onClick={() => {
                          setReviewingApp(app);
                          setDecision('reject');
                          setReviewNote('');
                        }}
                      >
                        <XCircle size={15} /> Reject Application
                      </Button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 2: INVITATIONS (Super Admin) */}
      {activeTab === 'invitations' && canInvite && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {loadingInvs ? (
            <Spinner />
          ) : invitations.length === 0 ? (
            <div className="doctor-empty-state">
              <Mail size={48} />
              <h3>No invitations issued yet</h3>
              <p>Super Admins can send onboarding invitations to doctors via email.</p>
              <Button variant="primary" size="md" onClick={() => setInviteModalOpen(true)}>
                Send Doctor Invitation
              </Button>
            </div>
          ) : (
            <div className="consent-table-container">
              <table className="consent-table">
                <thead>
                  <tr>
                    <th>Invited Email</th>
                    <th>Status</th>
                    <th>Expires At</th>
                    <th>Created At</th>
                    <th>Invited By</th>
                  </tr>
                </thead>
                <tbody>
                  {invitations.map((inv) => (
                    <tr key={inv.id}>
                      <td>
                        <strong>{inv.email}</strong>
                      </td>
                      <td>
                        <span className={`status-pill status-${inv.status}`}>{inv.status}</span>
                      </td>
                      <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        {new Date(inv.expires_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}
                      </td>
                      <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        {new Date(inv.created_at).toLocaleDateString()}
                      </td>
                      <td>{inv.invited_by}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* REVIEW APPLICATION MODAL */}
      {reviewingApp && (
        <Modal
          title={`${decision === 'approve' ? 'Approve' : 'Reject'} Doctor Application #${reviewingApp.id}`}
          subtitle={`Applicant: ${reviewingApp.full_name} (${reviewingApp.email})`}
          onClose={() => setReviewingApp(null)}
          wide={true}
        >
          <form onSubmit={handleReviewSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="doctor-form-group">
              <label htmlFor="review-decision">Verification Decision *</label>
              <select
                id="review-decision"
                className="doctor-form-select"
                value={decision}
                onChange={(e) => setDecision(e.target.value)}
              >
                <option value="approve">Approve (Grants Doctor Profile & Public Listing)</option>
                <option value="reject">Reject Application</option>
              </select>
            </div>

            <div className="doctor-form-group">
              <label htmlFor="review-note">
                {decision === 'reject'
                  ? 'Rejection Reason (Emailed Directly to Applicant) *'
                  : 'Reviewer Audit & Feedback Note (Optional)'}
              </label>
              <textarea
                id="review-note"
                rows={3}
                className="doctor-form-textarea"
                placeholder={
                  decision === 'reject'
                    ? 'State the reason for rejection clearly. This explanation will be included in the decision email sent to the applicant...'
                    : 'Optional audit note or internal reviewer comment...'
                }
                required={decision === 'reject'}
                maxLength={1000}
                value={reviewNote}
                onChange={(e) => setReviewNote(e.target.value)}
                disabled={submittingReview}
              />
              {decision === 'reject' && (
                <small style={{ color: 'var(--red-primary)' }}>
                  A clear reason is required and will be delivered to the applicant via email.
                </small>
              )}
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
              <Button type="button" variant="secondary" onClick={() => setReviewingApp(null)} disabled={submittingReview}>
                Cancel
              </Button>
              <Button type="submit" variant={decision === 'approve' ? 'primary' : 'danger'} disabled={submittingReview}>
                {submittingReview ? 'Submitting Decision...' : `Confirm ${decision === 'approve' ? 'Approval' : 'Rejection'}`}
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* SEND INVITATION MODAL */}
      {inviteModalOpen && (
        <Modal
          title="Send Doctor Onboarding Invitation"
          subtitle="Generate a single-use onboarding link sent directly to the physician's email"
          onClose={handleCloseInviteModal}
        >
          {inviteModalError && <Banner variant="error">{inviteModalError}</Banner>}
          <form onSubmit={handleInviteSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="doctor-form-group">
              <label htmlFor="invite-email">Doctor Email Address *</label>
              <input
                id="invite-email"
                type="email"
                className="doctor-form-input"
                placeholder="doctor@example.com"
                required
                maxLength={254}
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
                disabled={submittingInvite}
              />
              <small style={{ color: 'var(--text-muted)' }}>
                The doctor must sign in or register with this exact email to accept the invitation.
              </small>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
              <Button type="button" variant="secondary" onClick={handleCloseInviteModal} disabled={submittingInvite}>
                Cancel
              </Button>
              <Button type="submit" variant="primary" disabled={submittingInvite || !inviteEmail.trim()}>
                {submittingInvite ? 'Sending...' : 'Send Invitation Email'}
              </Button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
