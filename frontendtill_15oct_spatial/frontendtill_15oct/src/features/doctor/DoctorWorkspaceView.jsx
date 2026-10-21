import { useState, useEffect, useCallback } from 'react';
import Button from '../../components/Button/index.js';
import Spinner from '../../components/Spinner/index.js';
import Banner from '../../components/Banner/index.js';
import Modal from '../../components/Modal/index.js';
import DoctorChatModal from './DoctorChatModal.jsx';
import ConsultationNotesModal from './ConsultationNotesModal.jsx';
import SharedRecordsModal from './SharedRecordsModal.jsx';
import {
  getDoctorProfile,
  updateDoctorProfile,
  getAppointments,
  decideAppointment,
  cancelAppointment,
  completeAppointment,
  getChatRequests,
  decideChatRequest,
  cancelChatRequest,
} from '../../services/api.js';
import {
  Stethoscope,
  Calendar,
  MessageSquare,
  CheckCircle,
  XCircle,
  FileText,
  Clock,
  User,
  Shield,
  Activity,
  Check,
  Ban,
  Settings,
} from 'lucide-react';
import './doctor.css';

export default function DoctorWorkspaceView({ email, initialTab = 'requests' }) {
  const [activeTab, setActiveTab] = useState(initialTab); // 'requests', 'upcoming', 'completed', 'chats', 'profile'

  useEffect(() => {
    if (initialTab) setActiveTab(initialTab);
  }, [initialTab]);

  // Doctor profile
  const [profile, setProfile] = useState(null);
  const [loadingProfile, setLoadingProfile] = useState(true);
  const [savingProfile, setSavingProfile] = useState(false);

  // Appointments
  const [appointments, setAppointments] = useState([]);
  const [loadingAppointments, setLoadingAppointments] = useState(false);

  // Chat Requests
  const [chatRequests, setChatRequests] = useState([]);
  const [loadingChats, setLoadingChats] = useState(false);

  // Errors and feedback
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Modals
  const [decideModalApt, setDecideModalApt] = useState(null); // appointment to accept/reject
  const [decisionType, setDecisionType] = useState('accept'); // 'accept' | 'reject'
  const [scheduledAt, setScheduledAt] = useState('');
  const [doctorResponse, setDoctorResponse] = useState('');
  const [submittingDecision, setSubmittingDecision] = useState(false);

  const [activeChatRequest, setActiveChatRequest] = useState(null);
  const [activeNoteAppointment, setActiveNoteAppointment] = useState(null);
  const [viewingRecordMember, setViewingRecordMember] = useState(null); // { id, name }

  // Load doctor profile
  const loadProfile = useCallback(async () => {
    try {
      setLoadingProfile(true);
      setError('');
      const data = await getDoctorProfile();
      setProfile(data);
    } catch (e) {
      setError(e.message || 'Unable to load doctor profile.');
    } finally {
      setLoadingProfile(false);
    }
  }, []);

  // Load appointments
  const loadAppointments = useCallback(async () => {
    try {
      setLoadingAppointments(true);
      const data = await getAppointments('doctor');
      setAppointments(data?.appointments || []);
    } catch (e) {
      // Non-blocking
    } finally {
      setLoadingAppointments(false);
    }
  }, []);

  // Load chat requests
  const loadChats = useCallback(async () => {
    try {
      setLoadingChats(true);
      const data = await getChatRequests('doctor');
      setChatRequests(data?.chat_requests || []);
    } catch (e) {
      // Non-blocking
    } finally {
      setLoadingChats(false);
    }
  }, []);

  useEffect(() => {
    loadProfile();
    loadAppointments();
    loadChats();
  }, [loadProfile, loadAppointments, loadChats]);

  // Appointment Decision submit (accept / reject)
  const handleDecisionSubmit = async (e) => {
    e.preventDefault();
    if (!decideModalApt) return;
    setError('');
    setSuccess('');
    setSubmittingDecision(true);

    let isoScheduled = null;
    if (decisionType === 'accept') {
      try {
        const dt = new Date(scheduledAt);
        if (isNaN(dt.getTime())) throw new Error();
        if (dt <= new Date()) {
          setError('Scheduled appointment date and time must be in the future.');
          setSubmittingDecision(false);
          return;
        }
        isoScheduled = dt.toISOString();
      } catch {
        setError('Please provide a valid ISO date-time for scheduled appointment.');
        setSubmittingDecision(false);
        return;
      }
    }

    try {
      await decideAppointment(
        decideModalApt.id,
        decisionType,
        isoScheduled,
        doctorResponse.trim()
      );
      setSuccess(`Appointment #${decideModalApt.id} was ${decisionType === 'accept' ? 'accepted' : 'rejected'}.`);
      setDecideModalApt(null);
      setScheduledAt('');
      setDoctorResponse('');
      loadAppointments();
    } catch (err) {
      setError(err.message || 'Unable to update appointment decision.');
    } finally {
      setSubmittingDecision(false);
    }
  };

  // Complete appointment
  const handleComplete = async (aptId) => {
    if (!window.confirm('Mark this consultation appointment as completed?')) return;
    setError('');
    setSuccess('');
    try {
      await completeAppointment(aptId);
      setSuccess(`Appointment #${aptId} marked as completed.`);
      loadAppointments();
    } catch (err) {
      setError(err.message || 'Unable to complete appointment.');
    }
  };

  // Cancel appointment
  const handleCancelApt = async (aptId) => {
    const reason = window.prompt('Provide a reason for cancellation (optional):', '');
    if (reason === null) return;
    setError('');
    setSuccess('');
    try {
      await cancelAppointment(aptId, reason);
      setSuccess(`Appointment #${aptId} cancelled.`);
      loadAppointments();
    } catch (err) {
      setError(err.message || 'Unable to cancel appointment.');
    }
  };

  // Chat request decision
  const handleChatDecision = async (chatId, decision) => {
    setError('');
    setSuccess('');
    try {
      await decideChatRequest(chatId, decision);
      setSuccess(`Online consultation request #${chatId} ${decision === 'accept' ? 'accepted' : 'rejected'}.`);
      loadChats();
    } catch (err) {
      setError(err.message || 'Unable to update chat request.');
    }
  };

  // Cancel chat request
  const handleCancelChat = async (chatId) => {
    if (!window.confirm('Cancel this chat consultation request?')) return;
    setError('');
    setSuccess('');
    try {
      await cancelChatRequest(chatId);
      setSuccess(`Chat consultation #${chatId} cancelled.`);
      loadChats();
    } catch (err) {
      setError(err.message || 'Unable to cancel chat request.');
    }
  };

  // Toggle availability
  const handleToggleAvailability = async () => {
    if (!profile) return;
    setSavingProfile(true);
    setError('');
    try {
      const updated = await updateDoctorProfile({ is_available: !profile.is_available });
      setProfile((prev) => ({ ...prev, is_available: updated.is_available }));
      setSuccess(`Availability updated to ${updated.is_available ? 'Available' : 'Unavailable'}.`);
    } catch (err) {
      setError(err.message || 'Unable to update availability.');
    } finally {
      setSavingProfile(false);
    }
  };

  // Filtered lists
  const pendingRequests = appointments.filter((a) => a.status === 'requested');
  const upcomingAppointments = appointments.filter((a) => a.status === 'accepted');
  const completedAppointments = appointments.filter((a) => a.status === 'completed');
  const pendingChats = chatRequests.filter((c) => c.status === 'requested');
  const acceptedChats = chatRequests.filter((c) => c.status === 'accepted');

  return (
    <div className="doctor-system-container">
      {/* Header Card */}
      <div className="doctor-header-card">
        <div>
          <h2>Doctor Clinical Workspace</h2>
          <p>
            {profile?.full_name ? `Welcome, ${profile.full_name}` : 'Practitioner Portal'} • {profile?.specialty}
          </p>
        </div>
        {profile && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <span
              style={{
                fontSize: '0.85rem',
                color: profile.is_available ? 'var(--emerald)' : 'var(--text-muted)',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
              }}
            >
              <span
                style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  background: profile.is_available ? 'var(--emerald)' : 'var(--text-muted)',
                }}
              />
              {profile.is_available ? 'Accepting Patients' : 'Unavailable'}
            </span>
            <Button
              variant={profile.is_available ? 'secondary' : 'primary'}
              size="sm"
              onClick={handleToggleAvailability}
              disabled={savingProfile}
            >
              {profile.is_available ? 'Set Unavailable' : 'Set Available'}
            </Button>
          </div>
        )}
      </div>

      {error && <Banner variant="error">{error}</Banner>}
      {success && <Banner variant="info">{success}</Banner>}

      {/* Tabs */}
      <div className="doctor-nav-tabs">
        <button
          className={`doctor-tab-btn ${activeTab === 'requests' ? 'active' : ''}`}
          onClick={() => setActiveTab('requests')}
        >
          <Calendar size={17} /> Appointment Requests
          {pendingRequests.length > 0 && <span className="doctor-badge-count">{pendingRequests.length}</span>}
        </button>
        <button
          className={`doctor-tab-btn ${activeTab === 'upcoming' ? 'active' : ''}`}
          onClick={() => setActiveTab('upcoming')}
        >
          <Clock size={17} /> Upcoming Appointments
          {upcomingAppointments.length > 0 && (
            <span className="doctor-badge-count">{upcomingAppointments.length}</span>
          )}
        </button>
        <button
          className={`doctor-tab-btn ${activeTab === 'completed' ? 'active' : ''}`}
          onClick={() => setActiveTab('completed')}
        >
          <CheckCircle size={17} /> Completed ({completedAppointments.length})
        </button>
        <button
          className={`doctor-tab-btn ${activeTab === 'chats' ? 'active' : ''}`}
          onClick={() => setActiveTab('chats')}
        >
          <MessageSquare size={17} /> Chat Consultations
          {(pendingChats.length > 0 || acceptedChats.length > 0) && (
            <span className="doctor-badge-count">{pendingChats.length + acceptedChats.length}</span>
          )}
        </button>
        <button
          className={`doctor-tab-btn ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          <Settings size={17} /> Profile & Settings
        </button>
      </div>

      {/* TAB 1: PENDING APPOINTMENT REQUESTS */}
      {activeTab === 'requests' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {loadingAppointments ? (
            <Spinner />
          ) : pendingRequests.length === 0 ? (
            <div className="doctor-empty-state">
              <CheckCircle size={48} color="var(--emerald)" />
              <h3>All appointment requests reviewed</h3>
              <p>No pending appointment requests awaiting your decision.</p>
            </div>
          ) : (
            <div className="requests-list">
              {pendingRequests.map((apt) => (
                <div key={apt.id} className="request-item-card">
                  <div className="request-item-header">
                    <div className="request-item-title">
                      <Calendar size={18} color="var(--red-primary)" />
                      <span>Request #{apt.id} — Patient: {apt.member_name}</span>
                      <span className="status-pill status-requested">Awaiting Decision</span>
                    </div>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      Requested: {new Date(apt.created_at).toLocaleString()}
                    </span>
                  </div>

                  <div className="request-details-grid">
                    <div className="request-detail-item">
                      <span className="request-detail-label">Patient Member</span>
                      <span className="request-detail-val">{apt.member_name}</span>
                    </div>
                    <div className="request-detail-item">
                      <span className="request-detail-label">Patient Preferred Time</span>
                      <span className="request-detail-val" style={{ color: 'var(--warning)', fontWeight: 600 }}>
                        {new Date(apt.preferred_at).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })}
                      </span>
                    </div>
                    <div className="request-detail-item">
                      <span className="request-detail-label">Reason</span>
                      <span className="request-detail-val">{apt.reason || 'General Consultation'}</span>
                    </div>
                  </div>

                  {apt.patient_note && (
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                      <strong>Patient Note: </strong> {apt.patient_note}
                    </div>
                  )}

                  <div className="request-item-actions">
                    <Button
                      type="button"
                      variant="primary"
                      size="sm"
                      onClick={() => {
                        setDecideModalApt(apt);
                        setDecisionType('accept');
                        // Pre-populate with preferred_at formatted for input
                        try {
                          const pref = new Date(apt.preferred_at);
                          const localIso = new Date(pref.getTime() - pref.getTimezoneOffset() * 60000)
                            .toISOString()
                            .slice(0, 16);
                          setScheduledAt(localIso);
                        } catch {
                          setScheduledAt('');
                        }
                      }}
                    >
                      <Check size={15} /> Accept & Schedule
                    </Button>
                    <Button
                      type="button"
                      variant="danger"
                      size="sm"
                      onClick={() => {
                        setDecideModalApt(apt);
                        setDecisionType('reject');
                        setScheduledAt('');
                      }}
                    >
                      <XCircle size={15} /> Reject Request
                    </Button>
                    <Button
                      type="button"
                      variant="secondary"
                      size="sm"
                      onClick={() => setViewingRecordMember({ id: apt.member_id, name: apt.member_name })}
                    >
                      <Activity size={15} /> View Shared Medical Records
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 2: UPCOMING ACCEPTED APPOINTMENTS */}
      {activeTab === 'upcoming' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {loadingAppointments ? (
            <Spinner />
          ) : upcomingAppointments.length === 0 ? (
            <div className="doctor-empty-state">
              <Calendar size={48} />
              <h3>No upcoming scheduled consultations</h3>
              <p>Accepted appointments will appear here.</p>
            </div>
          ) : (
            <div className="requests-list">
              {upcomingAppointments.map((apt) => (
                <div key={apt.id} className="request-item-card">
                  <div className="request-item-header">
                    <div className="request-item-title">
                      <Clock size={18} color="var(--emerald)" />
                      <span>Appointment #{apt.id} — {apt.member_name}</span>
                      <span className="status-pill status-accepted">Accepted</span>
                    </div>
                    <span style={{ fontSize: '0.85rem', color: 'var(--emerald)', fontWeight: 600 }}>
                      Scheduled: {apt.scheduled_at ? new Date(apt.scheduled_at).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' }) : 'Pending'}
                    </span>
                  </div>

                  <div className="request-details-grid">
                    <div className="request-detail-item">
                      <span className="request-detail-label">Reason</span>
                      <span className="request-detail-val">{apt.reason || 'General Consultation'}</span>
                    </div>
                    {apt.doctor_response && (
                      <div className="request-detail-item">
                        <span className="request-detail-label">Your Confirmation Note</span>
                        <span className="request-detail-val">{apt.doctor_response}</span>
                      </div>
                    )}
                  </div>

                  <div className="request-item-actions">
                    <Button
                      type="button"
                      variant="primary"
                      size="sm"
                      onClick={() => setActiveNoteAppointment(apt)}
                    >
                      <FileText size={15} /> Consultation Notes
                    </Button>
                    <Button
                      type="button"
                      variant="secondary"
                      size="sm"
                      onClick={() => setViewingRecordMember({ id: apt.member_id, name: apt.member_name })}
                    >
                      <Activity size={15} /> Patient Records
                    </Button>
                    <Button
                      type="button"
                      variant="secondary"
                      size="sm"
                      onClick={() => handleComplete(apt.id)}
                    >
                      <CheckCircle size={15} /> Mark Complete
                    </Button>
                    <Button
                      type="button"
                      variant="danger"
                      size="sm"
                      onClick={() => handleCancelApt(apt.id)}
                    >
                      <Ban size={15} /> Cancel Appointment
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 3: COMPLETED CONSULTATIONS */}
      {activeTab === 'completed' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {completedAppointments.length === 0 ? (
            <div className="doctor-empty-state">
              <CheckCircle size={48} />
              <h3>No completed consultations yet</h3>
            </div>
          ) : (
            <div className="requests-list">
              {completedAppointments.map((apt) => (
                <div key={apt.id} className="request-item-card">
                  <div className="request-item-header">
                    <div className="request-item-title">
                      <span>Appointment #{apt.id} — {apt.member_name}</span>
                      <span className="status-pill status-completed">Completed</span>
                    </div>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      Completed on: {apt.completed_at ? new Date(apt.completed_at).toLocaleDateString() : 'N/A'}
                    </span>
                  </div>
                  <div className="request-item-actions">
                    <Button
                      type="button"
                      variant="secondary"
                      size="sm"
                      onClick={() => setActiveNoteAppointment(apt)}
                    >
                      <FileText size={15} /> View / Edit Consultation Notes
                    </Button>
                    <Button
                      type="button"
                      variant="secondary"
                      size="sm"
                      onClick={() => setViewingRecordMember({ id: apt.member_id, name: apt.member_name })}
                    >
                      <Activity size={15} /> Patient Records
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 4: CHAT REQUESTS & ACTIVE CONVERSATIONS */}
      {activeTab === 'chats' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Pending Chat Requests */}
          <div>
            <h3 style={{ fontSize: '1.1rem', color: 'var(--text-primary)', marginBottom: '0.75rem' }}>
              Pending Chat Inquiries ({pendingChats.length})
            </h3>
            {pendingChats.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No pending chat requests.</p>
            ) : (
              <div className="requests-list">
                {pendingChats.map((c) => (
                  <div key={c.id} className="request-item-card">
                    <div className="request-item-header">
                      <div className="request-item-title">
                        <span>Chat Request #{c.id} — {c.member_name}</span>
                        <span className="status-pill status-requested">Awaiting Decision</span>
                      </div>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        {new Date(c.created_at).toLocaleString()}
                      </span>
                    </div>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0 }}>
                      <strong>Inquiry: </strong> {c.message || 'General online consultation inquiry'}
                    </p>
                    <div className="request-item-actions">
                      <Button
                        type="button"
                        variant="primary"
                        size="sm"
                        onClick={() => handleChatDecision(c.id, 'accept')}
                      >
                        <Check size={15} /> Accept Chat
                      </Button>
                      <Button
                        type="button"
                        variant="danger"
                        size="sm"
                        onClick={() => handleChatDecision(c.id, 'reject')}
                      >
                        <XCircle size={15} /> Reject
                      </Button>
                      <Button
                        type="button"
                        variant="secondary"
                        size="sm"
                        onClick={() => setViewingRecordMember({ id: c.member_id, name: c.member_name })}
                      >
                        <Activity size={15} /> Patient Records
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Active Chat Conversations */}
          <div style={{ marginTop: '1rem' }}>
            <h3 style={{ fontSize: '1.1rem', color: 'var(--text-primary)', marginBottom: '0.75rem' }}>
              Active Online Consultations ({acceptedChats.length})
            </h3>
            {acceptedChats.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No active chat consultations.</p>
            ) : (
              <div className="requests-list">
                {acceptedChats.map((c) => (
                  <div key={c.id} className="request-item-card">
                    <div className="request-item-header">
                      <div className="request-item-title">
                        <MessageSquare size={17} color="var(--emerald)" />
                        <span>Consultation #{c.id} — {c.member_name}</span>
                        <span className="status-pill status-accepted">Active Chat</span>
                      </div>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        Accepted {new Date(c.updated_at).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="request-item-actions">
                      <Button
                        type="button"
                        variant="primary"
                        size="sm"
                        onClick={() => setActiveChatRequest(c)}
                      >
                        <MessageSquare size={15} /> Open Messaging Window
                      </Button>
                      <Button
                        type="button"
                        variant="secondary"
                        size="sm"
                        onClick={() => setViewingRecordMember({ id: c.member_id, name: c.member_name })}
                      >
                        <Activity size={15} /> Patient Records
                      </Button>
                      <Button
                        type="button"
                        variant="danger"
                        size="sm"
                        onClick={() => handleCancelChat(c.id)}
                      >
                        <Ban size={15} /> End / Cancel
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 5: DOCTOR PROFILE & CLINICAL SETTINGS */}
      {activeTab === 'profile' && profile && (
        <div style={{ maxWidth: '640px', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="request-item-card">
            <h3 style={{ margin: '0 0 1rem 0', color: 'var(--text-primary)' }}>Professional Details</h3>
            <div className="request-details-grid">
              <div className="request-detail-item">
                <span className="request-detail-label">Full Name</span>
                <span className="request-detail-val">{profile.full_name}</span>
              </div>
              <div className="request-detail-item">
                <span className="request-detail-label">Medical Specialty</span>
                <span className="request-detail-val">{profile.specialty}</span>
              </div>
              <div className="request-detail-item">
                <span className="request-detail-label">Medical Registration No.</span>
                <span className="request-detail-val">{profile.registration_number}</span>
              </div>
              <div className="request-detail-item">
                <span className="request-detail-label">Qualifications</span>
                <span className="request-detail-val">{profile.qualifications}</span>
              </div>
            </div>

            <div style={{ marginTop: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div className="doctor-form-group">
                <label htmlFor="prof-clinic">Clinic / Hospital Affiliation</label>
                <input
                  id="prof-clinic"
                  type="text"
                  className="doctor-form-input"
                  value={profile.clinic_name || ''}
                  onChange={(e) => setProfile({ ...profile, clinic_name: e.target.value })}
                  maxLength={200}
                />
              </div>

              <div className="doctor-form-group">
                <label htmlFor="prof-bio">Bio & Clinical Focus</label>
                <textarea
                  id="prof-bio"
                  rows={4}
                  className="doctor-form-textarea"
                  value={profile.bio || ''}
                  onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
                  maxLength={5000}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
                <Button
                  type="button"
                  variant="primary"
                  onClick={async () => {
                    setSavingProfile(true);
                    setError('');
                    try {
                      await updateDoctorProfile({
                        clinic_name: profile.clinic_name,
                        bio: profile.bio,
                      });
                      setSuccess('Doctor profile updated successfully.');
                    } catch (err) {
                      setError(err.message || 'Unable to update profile.');
                    } finally {
                      setSavingProfile(false);
                    }
                  }}
                  disabled={savingProfile}
                >
                  {savingProfile ? 'Saving...' : 'Save Profile Changes'}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* APPOINTMENT DECISION MODAL */}
      {decideModalApt && (
        <Modal
          title={`${decisionType === 'accept' ? 'Accept & Schedule' : 'Reject'} Appointment #${decideModalApt.id}`}
          subtitle={`Patient: ${decideModalApt.member_name} • Requested Preferred Time: ${new Date(decideModalApt.preferred_at).toLocaleString()}`}
          onClose={() => setDecideModalApt(null)}
          wide={true}
        >
          <form onSubmit={handleDecisionSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {decisionType === 'accept' && (
              <div className="doctor-form-group">
                <label htmlFor="decide-scheduled-time">Confirmed Consultation Date & Time *</label>
                <input
                  id="decide-scheduled-time"
                  type="datetime-local"
                  className="doctor-form-input"
                  required
                  value={scheduledAt}
                  onChange={(e) => setScheduledAt(e.target.value)}
                />
                <small style={{ color: 'var(--text-muted)' }}>
                  Must be in the future and not conflict with existing accepted appointments.
                </small>
              </div>
            )}

            <div className="doctor-form-group">
              <label htmlFor="decide-response">
                {decisionType === 'accept' ? 'Confirmation Instructions for Patient' : 'Reason for Rejection *'}
              </label>
              <textarea
                id="decide-response"
                rows={3}
                className="doctor-form-textarea"
                placeholder={
                  decisionType === 'accept'
                    ? 'e.g. Please bring recent blood test reports. Video link will be provided.'
                    : 'Provide the reason why this consultation request could not be accepted...'
                }
                value={doctorResponse}
                onChange={(e) => setDoctorResponse(e.target.value)}
                maxLength={1000}
                required={decisionType === 'reject'}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
              <Button type="button" variant="secondary" onClick={() => setDecideModalApt(null)} disabled={submittingDecision}>
                Cancel
              </Button>
              <Button type="submit" variant={decisionType === 'accept' ? 'primary' : 'danger'} disabled={submittingDecision}>
                {submittingDecision ? 'Submitting...' : decisionType === 'accept' ? 'Confirm & Schedule' : 'Reject Request'}
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* CHAT MODAL */}
      {activeChatRequest && (
        <DoctorChatModal
          chatRequest={activeChatRequest}
          myEmail={email}
          onClose={() => setActiveChatRequest(null)}
        />
      )}

      {/* CONSULTATION NOTES MODAL */}
      {activeNoteAppointment && (
        <ConsultationNotesModal
          appointment={activeNoteAppointment}
          isDoctor={true}
          onClose={() => setActiveNoteAppointment(null)}
        />
      )}

      {/* SHARED RECORDS MODAL */}
      {viewingRecordMember && (
        <SharedRecordsModal
          memberId={viewingRecordMember.id}
          memberName={viewingRecordMember.name}
          onClose={() => setViewingRecordMember(null)}
        />
      )}
    </div>
  );
}
