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
  getDoctorDashboardOverview,
  getDoctorPatients,
  getDoctorAvailability,
  createDoctorAvailabilitySlot,
  deleteDoctorAvailabilitySlot,
  getAppointments,
  decideAppointment,
  cancelAppointment,
  completeAppointment,
  requestAppointmentReschedule,
  getRescheduleRequests,
  decideRescheduleRequest,
  getChatRequests,
  decideChatRequest,
  cancelChatRequest,
  closeChatRequest,
  downloadConsultationSummary,
} from '../../services/api.js';
import {
  Stethoscope,
  Calendar,
  MessageSquare,
  CheckCircle,
  CheckCircle2,
  XCircle,
  FileText,
  Clock,
  User,
  Users,
  Shield,
  Activity,
  Check,
  Ban,
  Settings,
  Plus,
  Trash2,
  RefreshCw,
  AlertCircle,
  LayoutDashboard,
  Download,
  Lock,
  ArrowRight,
  ShieldCheck,
  ShieldAlert,
} from 'lucide-react';
import './doctor.css';

const WEEKDAYS = [
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
  'Sunday',
];

export default function DoctorWorkspaceView({ email, initialTab = 'overview' }) {
  const [activeTab, setActiveTab] = useState(initialTab);

  useEffect(() => {
    if (initialTab) setActiveTab(initialTab);
  }, [initialTab]);

  // Doctor profile & overview
  const [profile, setProfile] = useState(null);
  const [loadingProfile, setLoadingProfile] = useState(true);
  const [savingProfile, setSavingProfile] = useState(false);

  const [overview, setOverview] = useState(null);
  const [loadingOverview, setLoadingOverview] = useState(false);

  // Appointments & Reschedules
  const [appointments, setAppointments] = useState([]);
  const [loadingAppointments, setLoadingAppointments] = useState(false);

  const [rescheduleRequests, setRescheduleRequests] = useState([]);
  const [loadingReschedules, setLoadingReschedules] = useState(false);

  // Assigned Patients
  const [patients, setPatients] = useState([]);
  const [loadingPatients, setLoadingPatients] = useState(false);

  // Doctor Availability Slots
  const [availability, setAvailability] = useState({ doctor_id: null, is_available: true, slots: [] });
  const [loadingAvailability, setLoadingAvailability] = useState(false);
  const [newSlot, setNewSlot] = useState({ weekday: 0, start_time: '09:00', end_time: '12:00' });
  const [submittingSlot, setSubmittingSlot] = useState(false);

  // Chat Requests
  const [chatRequests, setChatRequests] = useState([]);
  const [loadingChats, setLoadingChats] = useState(false);

  // Feedback states
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Modals & Active Actions
  const [decideModalApt, setDecideModalApt] = useState(null);
  const [decisionType, setDecisionType] = useState('accept'); // 'accept' | 'reject'
  const [scheduledAt, setScheduledAt] = useState('');
  const [doctorResponse, setDoctorResponse] = useState('');
  const [submittingDecision, setSubmittingDecision] = useState(false);

  const [rescheduleModalApt, setRescheduleModalApt] = useState(null);
  const [proposedRescheduleAt, setProposedRescheduleAt] = useState('');
  const [rescheduleReason, setRescheduleReason] = useState('');
  const [submittingReschedule, setSubmittingReschedule] = useState(false);

  const [cancelModalApt, setCancelModalApt] = useState(null);
  const [cancellationReason, setCancellationReason] = useState('');
  const [submittingCancel, setSubmittingCancel] = useState(false);

  const [activeChatRequest, setActiveChatRequest] = useState(null);
  const [activeNoteAppointment, setActiveNoteAppointment] = useState(null);
  const [viewingRecordMember, setViewingRecordMember] = useState(null); // { id, name }

  // Loaders
  const loadProfile = useCallback(async () => {
    try {
      setLoadingProfile(true);
      const data = await getDoctorProfile();
      setProfile(data);
    } catch (e) {
      setError(e.message || 'Unable to load doctor profile.');
    } finally {
      setLoadingProfile(false);
    }
  }, []);

  const loadOverview = useCallback(async () => {
    try {
      setLoadingOverview(true);
      const data = await getDoctorDashboardOverview();
      setOverview(data);
    } catch {
      // Non-blocking
    } finally {
      setLoadingOverview(false);
    }
  }, []);

  const loadAppointments = useCallback(async () => {
    try {
      setLoadingAppointments(true);
      const data = await getAppointments('doctor');
      setAppointments(data?.appointments || []);
    } catch {
      // Non-blocking
    } finally {
      setLoadingAppointments(false);
    }
  }, []);

  const loadReschedules = useCallback(async () => {
    try {
      setLoadingReschedules(true);
      const data = await getRescheduleRequests('doctor');
      setRescheduleRequests(data?.reschedule_requests || []);
    } catch {
      // Non-blocking
    } finally {
      setLoadingReschedules(false);
    }
  }, []);

  const loadPatients = useCallback(async () => {
    try {
      setLoadingPatients(true);
      const data = await getDoctorPatients();
      setPatients(data?.patients || []);
    } catch {
      // Non-blocking
    } finally {
      setLoadingPatients(false);
    }
  }, []);

  const loadAvailability = useCallback(async () => {
    try {
      setLoadingAvailability(true);
      const data = await getDoctorAvailability();
      setAvailability(data || { doctor_id: null, is_available: true, slots: [] });
    } catch {
      // Non-blocking
    } finally {
      setLoadingAvailability(false);
    }
  }, []);

  const loadChats = useCallback(async () => {
    try {
      setLoadingChats(true);
      const data = await getChatRequests('doctor');
      setChatRequests(data?.chat_requests || []);
    } catch {
      // Non-blocking
    } finally {
      setLoadingChats(false);
    }
  }, []);

  const refreshAll = useCallback(() => {
    setError('');
    loadProfile();
    loadOverview();
    loadAppointments();
    loadReschedules();
    loadPatients();
    loadAvailability();
    loadChats();
  }, [
    loadProfile,
    loadOverview,
    loadAppointments,
    loadReschedules,
    loadPatients,
    loadAvailability,
    loadChats,
  ]);

  useEffect(() => {
    refreshAll();
  }, [refreshAll]);

  // Handle appointment decision (accept/reject)
  const handleDecisionSubmit = async (e) => {
    e.preventDefault();
    if (!decideModalApt || submittingDecision) return;
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
        setError('Please provide a valid date-time for scheduled appointment.');
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
      setSuccess(
        `Appointment #${decideModalApt.id} was ${
          decisionType === 'accept' ? 'accepted and scheduled' : 'rejected'
        }.`
      );
      setDecideModalApt(null);
      setScheduledAt('');
      setDoctorResponse('');
      loadAppointments();
      loadOverview();
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
      loadOverview();
    } catch (err) {
      setError(err.message || 'Unable to complete appointment.');
    }
  };

  // Cancel appointment submit
  const handleCancelSubmit = async (e) => {
    e.preventDefault();
    if (!cancelModalApt || submittingCancel) return;
    setError('');
    setSuccess('');
    setSubmittingCancel(true);
    try {
      await cancelAppointment(cancelModalApt.id, cancellationReason.trim());
      setSuccess(`Appointment #${cancelModalApt.id} has been cancelled.`);
      setCancelModalApt(null);
      setCancellationReason('');
      loadAppointments();
      loadOverview();
    } catch (err) {
      setError(err.message || 'Unable to cancel appointment.');
    } finally {
      setSubmittingCancel(false);
    }
  };

  // Propose reschedule submit
  const handleRescheduleSubmit = async (e) => {
    e.preventDefault();
    if (!rescheduleModalApt || submittingReschedule) return;
    setError('');
    setSuccess('');

    let isoProposed = null;
    try {
      const dt = new Date(proposedRescheduleAt);
      if (isNaN(dt.getTime())) throw new Error();
      if (dt <= new Date()) {
        setError('Proposed appointment date and time must be in the future.');
        return;
      }
      isoProposed = dt.toISOString();
    } catch {
      setError('Please provide a valid date and time for proposed reschedule.');
      return;
    }

    setSubmittingReschedule(true);
    try {
      await requestAppointmentReschedule(
        rescheduleModalApt.id,
        isoProposed,
        rescheduleReason.trim()
      );
      setSuccess(`Reschedule proposed for Appointment #${rescheduleModalApt.id}.`);
      setRescheduleModalApt(null);
      setProposedRescheduleAt('');
      setRescheduleReason('');
      loadAppointments();
      loadReschedules();
      loadOverview();
    } catch (err) {
      setError(err.message || 'Unable to propose rescheduling.');
    } finally {
      setSubmittingReschedule(false);
    }
  };

  // Decide reschedule request (accept/reject patient proposal)
  const handleRescheduleDecision = async (requestId, decision) => {
    if (!window.confirm(`Are you sure you want to ${decision} this rescheduling request?`)) return;
    setError('');
    setSuccess('');
    try {
      await decideRescheduleRequest(requestId, decision);
      setSuccess(`Rescheduling request #${requestId} was ${decision}ed.`);
      loadReschedules();
      loadAppointments();
      loadOverview();
    } catch (err) {
      setError(err.message || 'Unable to update rescheduling request.');
    }
  };

  // Chat request decision
  const handleChatDecision = async (chatId, decision) => {
    setError('');
    setSuccess('');
    try {
      await decideChatRequest(chatId, decision);
      setSuccess(
        `Online consultation request #${chatId} ${
          decision === 'accept' ? 'accepted' : 'rejected'
        }.`
      );
      loadChats();
      loadOverview();
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
      loadOverview();
    } catch (err) {
      setError(err.message || 'Unable to cancel chat request.');
    }
  };

  // Close chat conversation
  const handleCloseChat = async (chatId) => {
    if (!window.confirm('Conclude and close this online consultation?')) return;
    setError('');
    setSuccess('');
    try {
      await closeChatRequest(chatId);
      setSuccess(`Online consultation #${chatId} has been closed.`);
      loadChats();
      loadOverview();
    } catch (err) {
      setError(err.message || 'Unable to close chat consultation.');
    }
  };

  // Availability toggle
  const handleToggleAvailability = async () => {
    if (!profile || savingProfile) return;
    setSavingProfile(true);
    setError('');
    try {
      const updated = await updateDoctorProfile({ is_available: !profile.is_available });
      setProfile((prev) => ({ ...prev, is_available: updated.is_available }));
      setAvailability((prev) => ({ ...prev, is_available: updated.is_available }));
      setSuccess(
        `Availability updated to ${updated.is_available ? 'Available' : 'Unavailable'}.`
      );
    } catch (err) {
      setError(err.message || 'Unable to update availability.');
    } finally {
      setSavingProfile(false);
    }
  };

  // Add availability slot
  const handleAddSlot = async (e) => {
    e.preventDefault();
    if (submittingSlot) return;
    setError('');
    setSuccess('');

    if (newSlot.start_time >= newSlot.end_time) {
      setError('Start time must be strictly before end time.');
      return;
    }

    setSubmittingSlot(true);
    try {
      await createDoctorAvailabilitySlot({
        weekday: newSlot.weekday,
        start_time: newSlot.start_time,
        end_time: newSlot.end_time,
      });
      setSuccess('Weekly availability slot added successfully.');
      loadAvailability();
    } catch (err) {
      setError(err.message || 'Unable to add availability slot.');
    } finally {
      setSubmittingSlot(false);
    }
  };

  // Delete availability slot
  const handleDeleteSlot = async (slotId) => {
    if (!window.confirm('Remove this recurring availability slot?')) return;
    setError('');
    setSuccess('');
    try {
      await deleteDoctorAvailabilitySlot(slotId);
      setSuccess('Availability slot removed.');
      loadAvailability();
    } catch (err) {
      setError(err.message || 'Unable to delete availability slot.');
    }
  };

  // Filtered lists
  const pendingRequests = appointments.filter((a) => a.status === 'requested');
  const upcomingAppointments = appointments.filter((a) => a.status === 'accepted');
  const completedAppointments = appointments.filter((a) => a.status === 'completed');
  const pendingReschedules = rescheduleRequests.filter((r) => r.status === 'pending');
  const pendingChats = chatRequests.filter((c) => c.status === 'requested');
  const activeChats = chatRequests.filter((c) => c.status === 'accepted');
  const closedChats = chatRequests.filter((c) => c.status === 'closed');

  return (
    <div className="doctor-system-container">
      {/* Header Card */}
      <div className="doctor-header-card">
        <div>
          <h2>Doctor Clinical Workspace</h2>
          <p>
            {profile?.full_name ? `Welcome, ${profile.full_name}` : 'Practitioner Portal'}
            {profile?.specialty ? ` • ${profile.specialty}` : ''}
            {profile?.registration_number ? ` • Reg #${profile.registration_number}` : ''}
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          {profile && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
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

          <Button variant="secondary" size="sm" onClick={refreshAll} title="Refresh Workspace Data">
            <RefreshCw size={15} /> Refresh
          </Button>
        </div>
      </div>

      {error && <Banner variant="error">{error}</Banner>}
      {success && <Banner variant="info">{success}</Banner>}

      {/* Tabs */}
      <div className="doctor-nav-tabs">
        <button
          className={`doctor-tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <LayoutDashboard size={17} /> Overview
        </button>

        <button
          className={`doctor-tab-btn ${activeTab === 'requests' ? 'active' : ''}`}
          onClick={() => setActiveTab('requests')}
        >
          <Clock size={17} /> Appointment Requests
          {pendingRequests.length > 0 && (
            <span className="doctor-badge-count">{pendingRequests.length}</span>
          )}
        </button>

        <button
          className={`doctor-tab-btn ${activeTab === 'upcoming' ? 'active' : ''}`}
          onClick={() => setActiveTab('upcoming')}
        >
          <Calendar size={17} /> Upcoming Appointments
          {upcomingAppointments.length > 0 && (
            <span className="doctor-badge-count">{upcomingAppointments.length}</span>
          )}
        </button>

        <button
          className={`doctor-tab-btn ${activeTab === 'reschedule' ? 'active' : ''}`}
          onClick={() => setActiveTab('reschedule')}
        >
          <Activity size={17} /> Reschedule Requests
          {pendingReschedules.length > 0 && (
            <span className="doctor-badge-count">{pendingReschedules.length}</span>
          )}
        </button>

        <button
          className={`doctor-tab-btn ${activeTab === 'patients' ? 'active' : ''}`}
          onClick={() => setActiveTab('patients')}
        >
          <Users size={17} /> Assigned Patients
          {patients.length > 0 && (
            <span className="doctor-badge-count" style={{ background: 'var(--purple-500, #a855f7)' }}>
              {patients.length}
            </span>
          )}
        </button>

        <button
          className={`doctor-tab-btn ${activeTab === 'availability' ? 'active' : ''}`}
          onClick={() => setActiveTab('availability')}
        >
          <Clock size={17} /> Weekly Availability
          {availability.slots?.length > 0 && (
            <span className="doctor-badge-count" style={{ background: 'var(--cyan-500, #06b6d4)' }}>
              {availability.slots.length}
            </span>
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
          {(pendingChats.length > 0 || activeChats.length > 0) && (
            <span className="doctor-badge-count">
              {pendingChats.length + activeChats.length}
            </span>
          )}
        </button>

        <button
          className={`doctor-tab-btn ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          <Settings size={17} /> Profile & Settings
        </button>
      </div>

      {/* TAB 1: OVERVIEW */}
      {activeTab === 'overview' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {loadingOverview && !overview ? (
            <Spinner />
          ) : (
            <>
              {/* Stat Cards Grid */}
              <div className="doctor-stats-grid">
                <div className="doctor-stat-card">
                  <div className="doctor-stat-icon" style={{ background: 'rgba(59, 130, 246, 0.15)', color: '#3b82f6' }}>
                    <Calendar size={24} />
                  </div>
                  <div className="doctor-stat-content">
                    <span className="doctor-stat-value">
                      {overview?.counts?.appointments_today ?? 0}
                    </span>
                    <span className="doctor-stat-label">Appointments Today</span>
                  </div>
                </div>

                <div className="doctor-stat-card">
                  <div className="doctor-stat-icon" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#10b981' }}>
                    <Clock size={24} />
                  </div>
                  <div className="doctor-stat-content">
                    <span className="doctor-stat-value">
                      {overview?.counts?.upcoming_appointments ?? 0}
                    </span>
                    <span className="doctor-stat-label">Upcoming Scheduled</span>
                  </div>
                </div>

                <div className="doctor-stat-card">
                  <div className="doctor-stat-icon" style={{ background: 'rgba(234, 179, 8, 0.15)', color: '#eab308' }}>
                    <AlertCircle size={24} />
                  </div>
                  <div className="doctor-stat-content">
                    <span className="doctor-stat-value">
                      {overview?.counts?.pending_appointment_requests ?? 0}
                    </span>
                    <span className="doctor-stat-label">Pending Requests</span>
                  </div>
                </div>

                <div className="doctor-stat-card">
                  <div className="doctor-stat-icon" style={{ background: 'rgba(168, 85, 247, 0.15)', color: '#a855f7' }}>
                    <Activity size={24} />
                  </div>
                  <div className="doctor-stat-content">
                    <span className="doctor-stat-value">
                      {overview?.counts?.pending_reschedule_requests ?? 0}
                    </span>
                    <span className="doctor-stat-label">Pending Reschedules</span>
                  </div>
                </div>

                <div className="doctor-stat-card">
                  <div className="doctor-stat-icon" style={{ background: 'rgba(239, 68, 68, 0.15)', color: '#ef4444' }}>
                    <MessageSquare size={24} />
                  </div>
                  <div className="doctor-stat-content">
                    <span className="doctor-stat-value">
                      {overview?.counts?.active_chats ?? 0}
                    </span>
                    <span className="doctor-stat-label">Active Chat Sessions</span>
                  </div>
                </div>

                <div className="doctor-stat-card">
                  <div className="doctor-stat-icon" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#10b981' }}>
                    <CheckCircle2 size={24} />
                  </div>
                  <div className="doctor-stat-content">
                    <span className="doctor-stat-value">
                      {overview?.counts?.completed_appointments ?? 0}
                    </span>
                    <span className="doctor-stat-label">Completed Consultations</span>
                  </div>
                </div>
              </div>

              {/* Status Breakdown Pills */}
              {overview?.appointments_by_status && (
                <div
                  style={{
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '12px',
                    padding: '1rem 1.25rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '1rem',
                    flexWrap: 'wrap',
                  }}
                >
                  <strong style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                    All-Time Appointments:
                  </strong>
                  <span className="status-pill status-requested">
                    Requested: {overview.appointments_by_status.requested || 0}
                  </span>
                  <span className="status-pill status-accepted">
                    Accepted: {overview.appointments_by_status.accepted || 0}
                  </span>
                  <span className="status-pill status-completed">
                    Completed: {overview.appointments_by_status.completed || 0}
                  </span>
                  <span className="status-pill status-cancelled">
                    Cancelled: {overview.appointments_by_status.cancelled || 0}
                  </span>
                  <span className="status-pill status-rejected">
                    Rejected: {overview.appointments_by_status.rejected || 0}
                  </span>
                </div>
              )}

              {/* Immediate Upcoming Sessions from Overview */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                  <h3 style={{ margin: 0, fontSize: '1.1rem', color: 'var(--text-primary)' }}>
                    Upcoming Consultations
                  </h3>
                  <Button variant="secondary" size="sm" onClick={() => setActiveTab('upcoming')}>
                    View All ({upcomingAppointments.length})
                  </Button>
                </div>

                {(overview?.upcoming || []).length === 0 ? (
                  <div className="doctor-empty-state">
                    <Calendar size={40} />
                    <p>No upcoming appointments scheduled.</p>
                  </div>
                ) : (
                  <div className="requests-list">
                    {(overview?.upcoming || []).slice(0, 5).map((apt) => (
                      <div key={apt.id} className="request-item-card">
                        <div className="request-item-header">
                          <div className="request-item-title">
                            <Clock size={17} color="var(--emerald)" />
                            <span>Appointment #{apt.id} — {apt.member_name}</span>
                            <span className="status-pill status-accepted">Accepted</span>
                          </div>
                          <span style={{ fontSize: '0.85rem', color: 'var(--emerald)', fontWeight: 600 }}>
                            {apt.scheduled_at
                              ? new Date(apt.scheduled_at).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })
                              : 'Pending schedule'}
                          </span>
                        </div>
                        <div className="request-item-actions">
                          <Button
                            type="button"
                            variant="primary"
                            size="sm"
                            onClick={() => setActiveNoteAppointment(apt)}
                          >
                            <FileText size={14} /> Notes
                          </Button>
                          <Button
                            type="button"
                            variant="secondary"
                            size="sm"
                            onClick={() => setViewingRecordMember({ id: apt.member_id, name: apt.member_name })}
                          >
                            <Activity size={14} /> Records
                          </Button>
                          <Button
                            type="button"
                            variant="secondary"
                            size="sm"
                            onClick={() => {
                              setRescheduleModalApt(apt);
                              setProposedRescheduleAt('');
                              setRescheduleReason('');
                            }}
                          >
                            <Clock size={14} /> Reschedule
                          </Button>
                          <Button
                            type="button"
                            variant="secondary"
                            size="sm"
                            onClick={() => handleComplete(apt.id)}
                          >
                            <CheckCircle size={14} /> Complete
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Recent History from Overview */}
              <div>
                <h3 style={{ margin: '0 0 0.75rem 0', fontSize: '1.1rem', color: 'var(--text-primary)' }}>
                  Recent History
                </h3>
                {(overview?.recent_history || []).length === 0 ? (
                  <div className="doctor-empty-state">
                    <p>No recent appointment history.</p>
                  </div>
                ) : (
                  <div className="requests-list">
                    {(overview?.recent_history || []).slice(0, 5).map((apt) => (
                      <div key={apt.id} className="request-item-card">
                        <div className="request-item-header">
                          <div className="request-item-title">
                            <span>Appointment #{apt.id} — {apt.member_name}</span>
                            <span className={`status-pill status-${apt.status}`}>
                              {apt.status}
                            </span>
                          </div>
                          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                            Updated: {new Date(apt.updated_at).toLocaleDateString()}
                          </span>
                        </div>
                        <div className="request-item-actions">
                          <Button
                            type="button"
                            variant="secondary"
                            size="sm"
                            onClick={() => setActiveNoteAppointment(apt)}
                          >
                            <FileText size={14} /> View Notes
                          </Button>
                          <Button
                            type="button"
                            variant="secondary"
                            size="sm"
                            onClick={() => setViewingRecordMember({ id: apt.member_id, name: apt.member_name })}
                          >
                            <Activity size={14} /> Records
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      )}

      {/* TAB 2: PENDING APPOINTMENT REQUESTS */}
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
                      <span className="request-detail-label">Preferred Time</span>
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

      {/* TAB 3: UPCOMING ACCEPTED APPOINTMENTS */}
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
                      onClick={() => {
                        setRescheduleModalApt(apt);
                        setProposedRescheduleAt('');
                        setRescheduleReason('');
                      }}
                    >
                      <Clock size={15} /> Propose Reschedule
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
                      onClick={() => {
                        setCancelModalApt(apt);
                        setCancellationReason('');
                      }}
                    >
                      <Ban size={15} /> Cancel
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 4: RESCHEDULE REQUESTS */}
      {activeTab === 'reschedule' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {loadingReschedules ? (
            <Spinner />
          ) : rescheduleRequests.length === 0 ? (
            <div className="doctor-empty-state">
              <Activity size={48} />
              <h3>No reschedule requests</h3>
              <p>When you or a patient proposes a new time for an accepted consultation, it appears here.</p>
            </div>
          ) : (
            <div className="requests-list">
              {rescheduleRequests.map((req) => {
                const isProposedByDoctor =
                  req.requested_by &&
                  email &&
                  req.requested_by.toLowerCase() === email.toLowerCase();
                const isPending = req.status === 'pending';

                return (
                  <div key={req.id} className="request-item-card">
                    <div className="request-item-header">
                      <div className="request-item-title">
                        <Clock size={18} color="var(--blue-500, #3b82f6)" />
                        <span>Reschedule Request #{req.id} — Appointment #{req.appointment_id}</span>
                        <span className={`status-pill status-${req.status}`}>
                          {req.status}
                        </span>
                      </div>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        Requested: {new Date(req.created_at).toLocaleString()}
                      </span>
                    </div>

                    <div className="request-details-grid">
                      <div className="request-detail-item">
                        <span className="request-detail-label">Patient Member</span>
                        <span className="request-detail-val">{req.member_name}</span>
                      </div>
                      <div className="request-detail-item">
                        <span className="request-detail-label">Current Appointment Time</span>
                        <span className="request-detail-val">
                          {req.current_scheduled_at
                            ? new Date(req.current_scheduled_at).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })
                            : 'Not scheduled'}
                        </span>
                      </div>
                      <div className="request-detail-item">
                        <span className="request-detail-label">Proposed New Time</span>
                        <span className="request-detail-val" style={{ color: 'var(--warning)', fontWeight: 600 }}>
                          {new Date(req.proposed_at).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })}
                        </span>
                      </div>
                      <div className="request-detail-item">
                        <span className="request-detail-label">Proposed By</span>
                        <span className="request-detail-val">
                          {isProposedByDoctor ? 'You (Doctor)' : `Patient (${req.requested_by})`}
                        </span>
                      </div>
                    </div>

                    {req.reason && (
                      <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                        <strong>Reason: </strong> {req.reason}
                      </div>
                    )}

                    <div className="request-item-actions">
                      {isPending && !isProposedByDoctor && (
                        <>
                          <Button
                            type="button"
                            variant="primary"
                            size="sm"
                            onClick={() => handleRescheduleDecision(req.id, 'accept')}
                          >
                            <Check size={15} /> Accept Proposed Time
                          </Button>
                          <Button
                            type="button"
                            variant="danger"
                            size="sm"
                            onClick={() => handleRescheduleDecision(req.id, 'reject')}
                          >
                            <XCircle size={15} /> Reject
                          </Button>
                        </>
                      )}

                      {isPending && isProposedByDoctor && (
                        <span style={{ fontSize: '0.85rem', color: 'var(--warning)', fontStyle: 'italic' }}>
                          Awaiting patient review and confirmation.
                        </span>
                      )}

                      <Button
                        type="button"
                        variant="secondary"
                        size="sm"
                        onClick={() => setViewingRecordMember({ id: req.member_id, name: req.member_name })}
                      >
                        <Activity size={15} /> View Records
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* TAB 5: ASSIGNED PATIENTS */}
      {activeTab === 'patients' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {loadingPatients ? (
            <Spinner />
          ) : patients.length === 0 ? (
            <div className="doctor-empty-state">
              <Users size={48} />
              <h3>No assigned patients yet</h3>
              <p>Patients who have requested or booked appointments with you will appear here.</p>
            </div>
          ) : (
            <div className="requests-list">
              {patients.map((pat) => (
                <div key={pat.member_id} className="request-item-card">
                  <div className="request-item-header">
                    <div className="request-item-title">
                      <User size={18} color="var(--purple-500, #a855f7)" />
                      <span>{pat.member_name}</span>
                      {pat.latest_appointment_status && (
                        <span className={`status-pill status-${pat.latest_appointment_status}`}>
                          Appointment: {pat.latest_appointment_status}
                        </span>
                      )}
                    </div>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      Account ID #{pat.patient_account_id}
                    </span>
                  </div>

                  <div className="request-details-grid">
                    <div className="request-detail-item">
                      <span className="request-detail-label">Record Sharing Consent</span>
                      <span className="request-detail-val">
                        {pat.record_access_active ? (
                          <span style={{ color: 'var(--emerald)', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
                            <ShieldCheck size={15} /> Active
                          </span>
                        ) : (
                          <span style={{ color: 'var(--text-muted)', display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
                            <ShieldAlert size={15} /> Inactive / Revoked
                          </span>
                        )}
                      </span>
                    </div>

                    <div className="request-detail-item">
                      <span className="request-detail-label">Permitted Scopes</span>
                      <div className="scope-chips" style={{ marginTop: '3px' }}>
                        {(pat.record_scopes || []).length > 0 ? (
                          pat.record_scopes.map((sc) => (
                            <span key={sc} className="scope-chip">
                              {sc}
                            </span>
                          ))
                        ) : (
                          <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>None</span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="request-item-actions">
                    <Button
                      type="button"
                      variant="primary"
                      size="sm"
                      onClick={() => setViewingRecordMember({ id: pat.member_id, name: pat.member_name })}
                      disabled={!pat.record_access_active}
                      title={pat.record_access_active ? 'View shared clinical records' : 'Patient has revoked record access'}
                    >
                      <Activity size={15} />
                      {pat.record_access_active ? 'View Shared Medical Records' : 'Consent Inactive'}
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 6: DOCTOR AVAILABILITY SLOTS */}
      {activeTab === 'availability' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Status Bar */}
          <div
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '12px',
              padding: '1.25rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '1rem',
            }}
          >
            <div>
              <h3 style={{ margin: '0 0 0.25rem 0', color: 'var(--text-primary)' }}>
                Weekly Recurring Schedule
              </h3>
              <p style={{ margin: 0, fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                When slots are configured, patients can only book appointments within your defined working hours.
              </p>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <span
                style={{
                  fontSize: '0.9rem',
                  fontWeight: 600,
                  color: availability.is_available ? 'var(--emerald)' : 'var(--text-muted)',
                }}
              >
                {availability.is_available ? 'Accepting Patients' : 'Currently Unavailable'}
              </span>
              <Button
                variant={availability.is_available ? 'secondary' : 'primary'}
                size="sm"
                onClick={handleToggleAvailability}
                disabled={savingProfile}
              >
                {availability.is_available ? 'Set Unavailable' : 'Set Available'}
              </Button>
            </div>
          </div>

          {/* Add Slot Form */}
          <div
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '12px',
              padding: '1.25rem',
            }}
          >
            <h4 style={{ margin: '0 0 1rem 0', color: 'var(--text-primary)', fontSize: '1rem' }}>
              Add Weekly Availability Slot
            </h4>
            <form onSubmit={handleAddSlot} style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
              <div className="doctor-form-group" style={{ minWidth: '160px' }}>
                <label htmlFor="slot-weekday">Day of Week *</label>
                <select
                  id="slot-weekday"
                  className="doctor-form-input"
                  value={newSlot.weekday}
                  onChange={(e) => setNewSlot({ ...newSlot, weekday: Number(e.target.value) })}
                  disabled={submittingSlot}
                >
                  {WEEKDAYS.map((day, idx) => (
                    <option key={day} value={idx}>
                      {day}
                    </option>
                  ))}
                </select>
              </div>

              <div className="doctor-form-group" style={{ minWidth: '130px' }}>
                <label htmlFor="slot-start">Start Time *</label>
                <input
                  id="slot-start"
                  type="time"
                  className="doctor-form-input"
                  required
                  value={newSlot.start_time}
                  onChange={(e) => setNewSlot({ ...newSlot, start_time: e.target.value })}
                  disabled={submittingSlot}
                />
              </div>

              <div className="doctor-form-group" style={{ minWidth: '130px' }}>
                <label htmlFor="slot-end">End Time *</label>
                <input
                  id="slot-end"
                  type="time"
                  className="doctor-form-input"
                  required
                  value={newSlot.end_time}
                  onChange={(e) => setNewSlot({ ...newSlot, end_time: e.target.value })}
                  disabled={submittingSlot}
                />
              </div>

              <Button type="submit" variant="primary" disabled={submittingSlot}>
                <Plus size={16} /> {submittingSlot ? 'Adding...' : 'Add Slot'}
              </Button>
            </form>
          </div>

          {/* Existing Slots Table */}
          <div>
            <h4 style={{ margin: '0 0 0.75rem 0', color: 'var(--text-primary)', fontSize: '1rem' }}>
              Configured Slots ({(availability.slots || []).length})
            </h4>

            {loadingAvailability ? (
              <Spinner />
            ) : (availability.slots || []).length === 0 ? (
              <div className="doctor-empty-state">
                <Clock size={40} />
                <p>No availability slots configured. You are currently accepting appointments anytime.</p>
              </div>
            ) : (
              <div className="admin-table-container">
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>Day</th>
                      <th>Start Time</th>
                      <th>End Time</th>
                      <th>Status</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(availability.slots || []).map((slot) => (
                      <tr key={slot.id}>
                        <td style={{ fontWeight: 600 }}>{WEEKDAYS[slot.weekday]}</td>
                        <td>{slot.start_time}</td>
                        <td>{slot.end_time}</td>
                        <td>
                          <span
                            className="status-pill status-accepted"
                            style={{ fontSize: '0.75rem' }}
                          >
                            Active
                          </span>
                        </td>
                        <td>
                          <Button
                            type="button"
                            variant="danger"
                            size="sm"
                            onClick={() => handleDeleteSlot(slot.id)}
                            title="Remove Slot"
                          >
                            <Trash2 size={14} /> Remove
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 7: COMPLETED CONSULTATIONS */}
      {activeTab === 'completed' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {completedAppointments.length === 0 ? (
            <div className="doctor-empty-state">
              <CheckCircle size={48} />
              <h3>No completed consultations yet</h3>
              <p>Consultations marked completed will appear here.</p>
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
                      onClick={() => downloadConsultationSummary(apt.id)}
                    >
                      <Download size={15} /> Download Summary
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

      {/* TAB 8: CHAT REQUESTS & ONLINE CONSULTATIONS */}
      {activeTab === 'chats' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Pending Chat Inquiries */}
          <div>
            <h3 style={{ fontSize: '1.1rem', color: 'var(--text-primary)', marginBottom: '0.75rem' }}>
              Pending Chat Inquiries ({pendingChats.length})
            </h3>
            {loadingChats && pendingChats.length === 0 ? (
              <Spinner />
            ) : pendingChats.length === 0 ? (
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

          {/* Active Online Consultations */}
          <div>
            <h3 style={{ fontSize: '1.1rem', color: 'var(--text-primary)', marginBottom: '0.75rem' }}>
              Active Online Consultations ({activeChats.length})
            </h3>
            {activeChats.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No active chat consultations.</p>
            ) : (
              <div className="requests-list">
                {activeChats.map((c) => (
                  <div key={c.id} className="request-item-card">
                    <div className="request-item-header">
                      <div className="request-item-title">
                        <MessageSquare size={17} color="var(--emerald)" />
                        <span>Consultation #{c.id} — {c.member_name}</span>
                        <span className="status-pill status-accepted">Active Chat</span>
                      </div>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        Accepted: {new Date(c.updated_at).toLocaleDateString()}
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
                        onClick={() => handleCloseChat(c.id)}
                      >
                        <CheckCircle2 size={15} color="var(--emerald)" /> Conclude & Close
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
                        <Ban size={15} /> Cancel Request
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Closed Consultations */}
          {closedChats.length > 0 && (
            <div>
              <h3 style={{ fontSize: '1.1rem', color: 'var(--text-primary)', marginBottom: '0.75rem' }}>
                Closed Consultations ({closedChats.length})
              </h3>
              <div className="requests-list">
                {closedChats.map((c) => (
                  <div key={c.id} className="request-item-card">
                    <div className="request-item-header">
                      <div className="request-item-title">
                        <Lock size={16} color="var(--text-muted)" />
                        <span>Consultation #{c.id} — {c.member_name}</span>
                        <span className="status-pill status-closed">Closed</span>
                      </div>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        Closed on: {new Date(c.updated_at).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="request-item-actions">
                      <Button
                        type="button"
                        variant="secondary"
                        size="sm"
                        onClick={() => setActiveChatRequest(c)}
                      >
                        <MessageSquare size={15} /> View Message History (Read-only)
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
            </div>
          )}
        </div>
      )}

      {/* TAB 9: DOCTOR PROFILE & CLINICAL SETTINGS */}
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
                  Must be in the future and fall within your weekly availability schedule.
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
                    ? 'e.g. Please bring recent lab reports. Video consultation link will be provided.'
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

      {/* PROPOSE RESCHEDULE MODAL */}
      {rescheduleModalApt && (
        <Modal
          title={`Propose Reschedule — Appointment #${rescheduleModalApt.id}`}
          subtitle={`Patient: ${rescheduleModalApt.member_name} • Current Time: ${
            rescheduleModalApt.scheduled_at ? new Date(rescheduleModalApt.scheduled_at).toLocaleString() : 'Not scheduled'
          }`}
          onClose={() => setRescheduleModalApt(null)}
          wide={true}
        >
          <form onSubmit={handleRescheduleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="doctor-form-group">
              <label htmlFor="reschedule-proposed-time">Proposed New Consultation Date & Time *</label>
              <input
                id="reschedule-proposed-time"
                type="datetime-local"
                className="doctor-form-input"
                required
                value={proposedRescheduleAt}
                onChange={(e) => setProposedRescheduleAt(e.target.value)}
              />
              <small style={{ color: 'var(--text-muted)' }}>
                Must be a future date & time matching your configured weekly availability slots.
              </small>
            </div>

            <div className="doctor-form-group">
              <label htmlFor="reschedule-reason-text">Reason for Rescheduling</label>
              <textarea
                id="reschedule-reason-text"
                rows={3}
                className="doctor-form-textarea"
                placeholder="e.g. Clinical conflict, emergency surgery, or doctor schedule update..."
                value={rescheduleReason}
                onChange={(e) => setRescheduleReason(e.target.value)}
                maxLength={1000}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
              <Button type="button" variant="secondary" onClick={() => setRescheduleModalApt(null)} disabled={submittingReschedule}>
                Cancel
              </Button>
              <Button type="submit" variant="primary" disabled={submittingReschedule || !proposedRescheduleAt}>
                {submittingReschedule ? 'Proposing...' : 'Submit Reschedule Proposal'}
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* CANCELLATION MODAL */}
      {cancelModalApt && (
        <Modal
          title={`Cancel Appointment #${cancelModalApt.id}`}
          subtitle={`Patient: ${cancelModalApt.member_name}`}
          onClose={() => setCancelModalApt(null)}
        >
          <form onSubmit={handleCancelSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0 }}>
              Are you sure you want to cancel this appointment? This action cannot be undone.
            </p>

            <div className="doctor-form-group">
              <label htmlFor="cancel-reason-input">Reason for Cancellation</label>
              <textarea
                id="cancel-reason-input"
                rows={3}
                className="doctor-form-textarea"
                placeholder="Provide a cancellation explanation for the patient..."
                value={cancellationReason}
                onChange={(e) => setCancellationReason(e.target.value)}
                maxLength={1000}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <Button type="button" variant="secondary" onClick={() => setCancelModalApt(null)} disabled={submittingCancel}>
                Keep Appointment
              </Button>
              <Button type="submit" variant="danger" disabled={submittingCancel}>
                {submittingCancel ? 'Cancelling...' : 'Confirm Cancellation'}
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
          onStatusChange={() => {
            loadChats();
            loadOverview();
          }}
        />
      )}

      {/* CONSULTATION NOTES MODAL */}
      {activeNoteAppointment && (
        <ConsultationNotesModal
          appointment={activeNoteAppointment}
          isDoctor={true}
          onClose={() => {
            setActiveNoteAppointment(null);
            loadAppointments();
            loadOverview();
          }}
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
