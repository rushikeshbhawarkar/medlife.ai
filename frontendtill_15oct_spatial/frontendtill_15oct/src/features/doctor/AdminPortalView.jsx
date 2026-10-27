import { useState, useEffect, useCallback } from 'react';
import Button from '../../components/Button/index.js';
import Spinner from '../../components/Spinner/index.js';
import Banner from '../../components/Banner/index.js';
import Modal from '../../components/Modal/index.js';
import {
  getAdminDashboardOverview,
  getAdminApplications,
  reviewDoctorApplication,
  downloadAdminApplicationDocument,
  getAdminDoctors,
  manageAdminDoctor,
  getAdminPatients,
  getAdminAppointments,
  getAdminAppointmentHistory,
  bookAdminAppointment,
  getAdminInvitations,
  sendDoctorInvitation,
  getAdminAnalytics,
  getAdminAuditLog,
} from '../../services/api.js';
import {
  LayoutDashboard,
  ShieldAlert,
  UserCheck,
  Calendar,
  Users,
  Mail,
  BarChart3,
  Activity,
  Search,
  Clock,
  CheckCircle2,
  XCircle,
  FileText,
  Download,
  Phone,
  MapPin,
  RefreshCw,
  Ban,
  ChevronRight,
  Eye,
  AlertTriangle,
  AlertCircle,
  Stethoscope,
  Info,
} from 'lucide-react';
import './doctor.css';

export default function AdminPortalView({ email, initialTab = 'overview', onTabChange }) {
  const [activeTab, setActiveTab] = useState(initialTab);

  useEffect(() => {
    if (initialTab) setActiveTab(initialTab);
  }, [initialTab]);

  const handleTabSwitch = (tab) => {
    setActiveTab(tab);
    if (onTabChange) onTabChange(tab);
  };

  const [globalError, setGlobalError] = useState('');
  const [globalSuccess, setGlobalSuccess] = useState('');

  // ---------------------------------------------------------------------------
  // TAB 1: OVERVIEW
  // ---------------------------------------------------------------------------
  const [overviewData, setOverviewData] = useState(null);
  const [loadingOverview, setLoadingOverview] = useState(false);

  const loadOverview = useCallback(async () => {
    try {
      setLoadingOverview(true);
      setGlobalError('');
      const data = await getAdminDashboardOverview();
      setOverviewData(data);
    } catch (err) {
      setGlobalError(err.message || 'Unable to load administrative overview.');
    } finally {
      setLoadingOverview(false);
    }
  }, []);

  // ---------------------------------------------------------------------------
  // TAB 2: DOCTOR APPLICATIONS
  // ---------------------------------------------------------------------------
  const [appStatusFilter, setAppStatusFilter] = useState('pending');
  const [applications, setApplications] = useState([]);
  const [loadingApps, setLoadingApps] = useState(false);
  const [downloadingDocId, setDownloadingDocId] = useState(null);

  // Review modal
  const [reviewingApp, setReviewingApp] = useState(null);
  const [decision, setDecision] = useState('approve');
  const [reviewNote, setReviewNote] = useState('');
  const [submittingReview, setSubmittingReview] = useState(false);

  const loadApplications = useCallback(async () => {
    try {
      setLoadingApps(true);
      setGlobalError('');
      const data = await getAdminApplications(appStatusFilter);
      setApplications(data?.applications || []);
    } catch (e) {
      if (e.status === 403) {
        setGlobalError('You are not authorized to review doctor applications. Staff role is required.');
      } else {
        setGlobalError(e.message || 'Unable to load doctor applications.');
      }
    } finally {
      setLoadingApps(false);
    }
  }, [appStatusFilter]);

  const handleDownloadDoc = async (docId, docType) => {
    try {
      setDownloadingDocId(docId);
      setGlobalError('');
      await downloadAdminApplicationDocument(docId, `doctor_application_doc_${docId}_${docType}`);
    } catch (err) {
      setGlobalError(err.message || 'Unable to download document.');
    } finally {
      setDownloadingDocId(null);
    }
  };

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    if (!reviewingApp) return;

    if (decision === 'reject' && !reviewNote.trim()) {
      setGlobalError('Please provide a rejection reason. This reason will be emailed directly to the applicant.');
      return;
    }

    setSubmittingReview(true);
    setGlobalError('');
    setGlobalSuccess('');
    try {
      const res = await reviewDoctorApplication(reviewingApp.id, decision, reviewNote.trim());
      if (decision === 'approve') {
        setGlobalSuccess(
          `Application #${reviewingApp.id} for ${reviewingApp.full_name} approved! An activation link has been emailed to ${reviewingApp.email}. The doctor account will be created once the applicant completes password and authenticator activation.`
        );
      } else {
        setGlobalSuccess(
          `Application #${reviewingApp.id} for ${reviewingApp.full_name} rejected. Decision notification emailed to ${reviewingApp.email}.`
        );
      }
      setReviewingApp(null);
      setReviewNote('');
      loadApplications();
      if (overviewData) loadOverview();
    } catch (err) {
      setGlobalError(err.message || 'Unable to submit application review.');
    } finally {
      setSubmittingReview(false);
    }
  };

  // ---------------------------------------------------------------------------
  // TAB 3: DOCTOR MANAGEMENT
  // ---------------------------------------------------------------------------
  const [doctors, setDoctors] = useState([]);
  const [loadingDoctors, setLoadingDoctors] = useState(false);
  const [doctorSearch, setDoctorSearch] = useState('');
  const [doctorStatusFilter, setDoctorStatusFilter] = useState('');
  const [doctorAvailFilter, setDoctorAvailFilter] = useState('');

  // Suspend / Reactivate Modal
  const [selectedDoctorForAction, setSelectedDoctorForAction] = useState(null);
  const [doctorActionType, setDoctorActionType] = useState('suspend');
  const [actionReason, setActionReason] = useState('');
  const [submittingDoctorAction, setSubmittingDoctorAction] = useState(false);

  const loadDoctors = useCallback(async () => {
    try {
      setLoadingDoctors(true);
      setGlobalError('');
      const params = {};
      if (doctorSearch.trim()) params.q = doctorSearch.trim();
      if (doctorStatusFilter) params.status = doctorStatusFilter;
      if (doctorAvailFilter) params.available = doctorAvailFilter;
      const data = await getAdminDoctors(params);
      setDoctors(data?.doctors || []);
    } catch (err) {
      setGlobalError(err.message || 'Unable to load doctor profiles.');
    } finally {
      setLoadingDoctors(false);
    }
  }, [doctorSearch, doctorStatusFilter, doctorAvailFilter]);

  const handleDoctorActionSubmit = async (e) => {
    e.preventDefault();
    if (!selectedDoctorForAction) return;
    setSubmittingDoctorAction(true);
    setGlobalError('');
    setGlobalSuccess('');
    try {
      await manageAdminDoctor(selectedDoctorForAction.id, doctorActionType, actionReason.trim());
      setGlobalSuccess(
        `Doctor ${selectedDoctorForAction.full_name} successfully ${
          doctorActionType === 'suspend' ? 'suspended' : 'reactivated'
        }.`
      );
      setSelectedDoctorForAction(null);
      setActionReason('');
      loadDoctors();
      if (overviewData) loadOverview();
    } catch (err) {
      setGlobalError(err.message || `Unable to ${doctorActionType} doctor.`);
    } finally {
      setSubmittingDoctorAction(false);
    }
  };

  // ---------------------------------------------------------------------------
  // TAB 4: APPOINTMENT MANAGEMENT
  // ---------------------------------------------------------------------------
  const [appointments, setAppointments] = useState([]);
  const [loadingAppointments, setLoadingAppointments] = useState(false);
  const [apptStatusFilter, setApptStatusFilter] = useState('');
  const [apptDoctorId, setApptDoctorId] = useState('');
  const [apptPatientId, setApptPatientId] = useState('');
  const [apptDateFrom, setApptDateFrom] = useState('');
  const [apptDateTo, setApptDateTo] = useState('');

  // Appointment History Modal
  const [historyAppointmentId, setHistoryAppointmentId] = useState(null);
  const [appointmentHistory, setAppointmentHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  // Admin Book Appointment Modal
  const [bookModalOpen, setBookModalOpen] = useState(false);
  const [bookMemberId, setBookMemberId] = useState('');
  const [bookDoctorId, setBookDoctorId] = useState('');
  const [bookPreferredAt, setBookPreferredAt] = useState('');
  const [bookReason, setBookReason] = useState('');
  const [bookPatientNote, setBookPatientNote] = useState('');
  const [submittingBooking, setSubmittingBooking] = useState(false);
  const [bookingModalError, setBookingModalError] = useState('');

  const loadAppointments = useCallback(async () => {
    try {
      setLoadingAppointments(true);
      setGlobalError('');
      const params = {};
      if (apptStatusFilter) params.status = apptStatusFilter;
      if (apptDoctorId.trim()) params.doctor_id = apptDoctorId.trim();
      if (apptPatientId.trim()) params.patient_id = apptPatientId.trim();
      if (apptDateFrom) params.date_from = apptDateFrom;
      if (apptDateTo) params.date_to = apptDateTo;
      const data = await getAdminAppointments(params);
      setAppointments(data?.appointments || []);
    } catch (err) {
      setGlobalError(err.message || 'Unable to load appointments.');
    } finally {
      setLoadingAppointments(false);
    }
  }, [apptStatusFilter, apptDoctorId, apptPatientId, apptDateFrom, apptDateTo]);

  const handleOpenHistory = async (apptId) => {
    try {
      setHistoryAppointmentId(apptId);
      setLoadingHistory(true);
      const data = await getAdminAppointmentHistory(apptId);
      setAppointmentHistory(data?.history || []);
    } catch (err) {
      setGlobalError(err.message || 'Unable to load appointment lifecycle history.');
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleBookAppointmentSubmit = async (e) => {
    e.preventDefault();
    if (!bookMemberId || !bookDoctorId || !bookPreferredAt) {
      setBookingModalError('Family profile ID, Doctor ID, and Preferred Date/Time are required.');
      return;
    }
    setSubmittingBooking(true);
    setBookingModalError('');
    try {
      // Backend expects ISO string with timezone offset
      const dt = new Date(bookPreferredAt);
      if (isNaN(dt.getTime())) {
        throw new Error('Invalid date and time selected.');
      }
      await bookAdminAppointment({
        member_id: parseInt(bookMemberId, 10),
        doctor_id: parseInt(bookDoctorId, 10),
        preferred_at: dt.toISOString(),
        reason: bookReason.trim(),
        patient_note: bookPatientNote.trim(),
      });
      setGlobalSuccess('Appointment successfully booked by Super Admin.');
      setBookModalOpen(false);
      setBookMemberId('');
      setBookDoctorId('');
      setBookPreferredAt('');
      setBookReason('');
      setBookPatientNote('');
      loadAppointments();
      if (overviewData) loadOverview();
    } catch (err) {
      setBookingModalError(err.message || 'Unable to book appointment.');
    } finally {
      setSubmittingBooking(false);
    }
  };

  // ---------------------------------------------------------------------------
  // TAB 5: PATIENT ACCOUNTS
  // ---------------------------------------------------------------------------
  const [patients, setPatients] = useState([]);
  const [loadingPatients, setLoadingPatients] = useState(false);
  const [patientSearch, setPatientSearch] = useState('');

  const loadPatients = useCallback(async () => {
    try {
      setLoadingPatients(true);
      setGlobalError('');
      const params = {};
      if (patientSearch.trim()) params.q = patientSearch.trim();
      const data = await getAdminPatients(params);
      setPatients(data?.patients || []);
    } catch (err) {
      setGlobalError(err.message || 'Unable to load patient directory.');
    } finally {
      setLoadingPatients(false);
    }
  }, [patientSearch]);

  // ---------------------------------------------------------------------------
  // TAB 6: DOCTOR INVITATIONS
  // ---------------------------------------------------------------------------
  const [invitations, setInvitations] = useState([]);
  const [loadingInvs, setLoadingInvs] = useState(false);
  const [inviteModalOpen, setInviteModalOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [submittingInvite, setSubmittingInvite] = useState(false);
  const [inviteModalError, setInviteModalError] = useState('');

  const loadInvitations = useCallback(async () => {
    try {
      setLoadingInvs(true);
      setGlobalError('');
      const data = await getAdminInvitations();
      setInvitations(data?.invitations || []);
    } catch (err) {
      setGlobalError(err.message || 'Unable to load doctor invitations.');
    } finally {
      setLoadingInvs(false);
    }
  }, []);

  const handleInviteSubmit = async (e) => {
    e.preventDefault();
    if (!inviteEmail.trim()) return;
    setSubmittingInvite(true);
    setInviteModalError('');
    try {
      const res = await sendDoctorInvitation(inviteEmail.trim().toLowerCase());
      setGlobalSuccess(res.message || `Invitation successfully sent to ${inviteEmail}.`);
      setInviteModalOpen(false);
      setInviteEmail('');
      loadInvitations();
      if (overviewData) loadOverview();
    } catch (err) {
      setInviteModalError(err.message || 'Unable to send invitation.');
    } finally {
      setSubmittingInvite(false);
    }
  };

  // ---------------------------------------------------------------------------
  // TAB 7: ANALYTICS
  // ---------------------------------------------------------------------------
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loadingAnalytics, setLoadingAnalytics] = useState(false);

  const loadAnalytics = useCallback(async () => {
    try {
      setLoadingAnalytics(true);
      setGlobalError('');
      const data = await getAdminAnalytics();
      setAnalyticsData(data);
    } catch (err) {
      setGlobalError(err.message || 'Unable to load administrative analytics.');
    } finally {
      setLoadingAnalytics(false);
    }
  }, []);

  // ---------------------------------------------------------------------------
  // TAB 8: AUDIT LOG
  // ---------------------------------------------------------------------------
  const [auditEvents, setAuditEvents] = useState([]);
  const [loadingAudit, setLoadingAudit] = useState(false);
  const [auditActionFilter, setAuditActionFilter] = useState('');
  const [auditActorFilter, setAuditActorFilter] = useState('');
  const [auditLimit, setAuditLimit] = useState('100');
  const [selectedMetaEvent, setSelectedMetaEvent] = useState(null);

  const loadAuditLog = useCallback(async () => {
    try {
      setLoadingAudit(true);
      setGlobalError('');
      const params = { limit: auditLimit };
      if (auditActionFilter.trim()) params.action = auditActionFilter.trim();
      if (auditActorFilter.trim()) params.actor = auditActorFilter.trim();
      const data = await getAdminAuditLog(params);
      setAuditEvents(data?.events || []);
    } catch (err) {
      setGlobalError(err.message || 'Unable to load administrative audit logs.');
    } finally {
      setLoadingAudit(false);
    }
  }, [auditActionFilter, auditActorFilter, auditLimit]);

  // Load data based on active tab
  useEffect(() => {
    if (activeTab === 'overview') loadOverview();
    if (activeTab === 'applications') loadApplications();
    if (activeTab === 'doctors') loadDoctors();
    if (activeTab === 'appointments') loadAppointments();
    if (activeTab === 'patients') loadPatients();
    if (activeTab === 'invitations') loadInvitations();
    if (activeTab === 'analytics') loadAnalytics();
    if (activeTab === 'audit_log') loadAuditLog();
  }, [
    activeTab,
    loadOverview,
    loadApplications,
    loadDoctors,
    loadAppointments,
    loadPatients,
    loadInvitations,
    loadAnalytics,
    loadAuditLog,
  ]);

  return (
    <div className="doctor-system-container">
      {/* Header */}
      <div className="doctor-header-card">
        <div>
          <h2>Super Admin Command Center</h2>
          <p>
            System-wide administration, credential verification, doctor onboarding, appointment audits, and analytics
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {activeTab === 'invitations' && (
            <Button variant="primary" size="md" onClick={() => setInviteModalOpen(true)}>
              <Mail size={16} /> Send Doctor Invitation
            </Button>
          )}
          {activeTab === 'appointments' && (
            <Button variant="primary" size="md" onClick={() => setBookModalOpen(true)}>
              <Calendar size={16} /> Book Appointment
            </Button>
          )}
          <Button
            variant="outline"
            size="md"
            onClick={() => {
              if (activeTab === 'overview') loadOverview();
              else if (activeTab === 'applications') loadApplications();
              else if (activeTab === 'doctors') loadDoctors();
              else if (activeTab === 'appointments') loadAppointments();
              else if (activeTab === 'patients') loadPatients();
              else if (activeTab === 'invitations') loadInvitations();
              else if (activeTab === 'analytics') loadAnalytics();
              else if (activeTab === 'audit_log') loadAuditLog();
            }}
          >
            <RefreshCw size={15} /> Refresh
          </Button>
        </div>
      </div>

      {globalError && <Banner variant="error">{globalError}</Banner>}
      {globalSuccess && <Banner variant="info">{globalSuccess}</Banner>}

      {/* Navigation Sub-Tabs */}
      <div className="doctor-nav-tabs">
        <button
          className={`doctor-tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => handleTabSwitch('overview')}
        >
          <LayoutDashboard size={17} /> Overview
        </button>
        <button
          className={`doctor-tab-btn ${activeTab === 'applications' ? 'active' : ''}`}
          onClick={() => handleTabSwitch('applications')}
        >
          <ShieldAlert size={17} /> Applications
          {overviewData?.totals?.pending_applications ? (
            <span className="doctor-badge-count">{overviewData.totals.pending_applications}</span>
          ) : null}
        </button>
        <button
          className={`doctor-tab-btn ${activeTab === 'doctors' ? 'active' : ''}`}
          onClick={() => handleTabSwitch('doctors')}
        >
          <UserCheck size={17} /> Doctors
        </button>
        <button
          className={`doctor-tab-btn ${activeTab === 'appointments' ? 'active' : ''}`}
          onClick={() => handleTabSwitch('appointments')}
        >
          <Calendar size={17} /> Appointments
        </button>
        <button
          className={`doctor-tab-btn ${activeTab === 'patients' ? 'active' : ''}`}
          onClick={() => handleTabSwitch('patients')}
        >
          <Users size={17} /> Patients
        </button>
        <button
          className={`doctor-tab-btn ${activeTab === 'invitations' ? 'active' : ''}`}
          onClick={() => handleTabSwitch('invitations')}
        >
          <Mail size={17} /> Invitations
        </button>
        <button
          className={`doctor-tab-btn ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => handleTabSwitch('analytics')}
        >
          <BarChart3 size={17} /> Analytics
        </button>
        <button
          className={`doctor-tab-btn ${activeTab === 'audit_log' ? 'active' : ''}`}
          onClick={() => handleTabSwitch('audit_log')}
        >
          <Activity size={17} /> Audit Log
        </button>
      </div>

      {/* =======================================================================
       * TAB 1: OVERVIEW
       * ======================================================================= */}
      {activeTab === 'overview' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {loadingOverview ? (
            <Spinner />
          ) : !overviewData ? (
            <div className="doctor-empty-state">
              <AlertCircle size={40} />
              <p>Overview metrics unavailable.</p>
            </div>
          ) : (
            <>
              {/* Stat Cards Grid */}
              <div className="admin-stats-grid">
                <div className="admin-stat-card">
                  <div className="admin-stat-icon" style={{ background: 'rgba(168, 85, 247, 0.15)', color: '#a855f7' }}>
                    <Users size={24} />
                  </div>
                  <div className="admin-stat-content">
                    <span className="admin-stat-value">{overviewData.totals?.patients ?? 0}</span>
                    <span className="admin-stat-label">Registered Patients</span>
                    <span className="admin-stat-sub">Accounts created</span>
                  </div>
                </div>

                <div className="admin-stat-card">
                  <div className="admin-stat-icon" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#10b981' }}>
                    <UserCheck size={24} />
                  </div>
                  <div className="admin-stat-content">
                    <span className="admin-stat-value">{overviewData.totals?.doctors ?? 0}</span>
                    <span className="admin-stat-label">Doctors in Network</span>
                    <span className="admin-stat-sub">
                      Approved: {overviewData.doctors_by_status?.approved ?? 0}
                    </span>
                  </div>
                </div>

                <div className="admin-stat-card">
                  <div className="admin-stat-icon" style={{ background: 'rgba(239, 68, 68, 0.15)', color: '#ef4444' }}>
                    <ShieldAlert size={24} />
                  </div>
                  <div className="admin-stat-content">
                    <span className="admin-stat-value">{overviewData.totals?.pending_applications ?? 0}</span>
                    <span className="admin-stat-label">Pending Applications</span>
                    <span className="admin-stat-sub">Requires credential review</span>
                  </div>
                </div>

                <div className="admin-stat-card">
                  <div className="admin-stat-icon" style={{ background: 'rgba(59, 130, 246, 0.15)', color: '#3b82f6' }}>
                    <Calendar size={24} />
                  </div>
                  <div className="admin-stat-content">
                    <span className="admin-stat-value">{overviewData.appointments_today ?? 0}</span>
                    <span className="admin-stat-label">Appointments Today</span>
                    <span className="admin-stat-sub">Month: {overviewData.appointments_this_month ?? 0}</span>
                  </div>
                </div>
              </div>

              {/* Status Breakdown Section */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
                <div className="admin-section-card">
                  <h3>Doctor Network Breakdown</h3>
                  <div style={{ display: 'flex', gap: '0.65rem', flexWrap: 'wrap' }}>
                    {Object.entries(overviewData.doctors_by_status || {}).map(([st, cnt]) => (
                      <span key={st} className={`status-pill status-${st}`} style={{ fontSize: '0.85rem', padding: '6px 12px' }}>
                        {st}: <strong>{cnt}</strong>
                      </span>
                    ))}
                    {!Object.keys(overviewData.doctors_by_status || {}).length && (
                      <span style={{ color: 'var(--text-muted)' }}>No doctor records</span>
                    )}
                  </div>
                </div>

                <div className="admin-section-card">
                  <h3>Appointment Status Breakdown</h3>
                  <div style={{ display: 'flex', gap: '0.65rem', flexWrap: 'wrap' }}>
                    {Object.entries(overviewData.appointments_by_status || {}).map(([st, cnt]) => (
                      <span key={st} className={`status-pill status-${st}`} style={{ fontSize: '0.85rem', padding: '6px 12px' }}>
                        {st}: <strong>{cnt}</strong>
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Pending Application Alerts */}
              {overviewData.pending_application_alerts && overviewData.pending_application_alerts.length > 0 && (
                <div className="admin-section-card" style={{ borderColor: 'var(--warning)' }}>
                  <h3>
                    <ShieldAlert size={20} color="var(--warning)" />
                    Pending Doctor Applications Awaiting Review ({overviewData.pending_application_alerts.length})
                  </h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {overviewData.pending_application_alerts.map((alert) => (
                      <div
                        key={alert.id}
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          padding: '0.85rem 1rem',
                          background: 'var(--bg-secondary)',
                          borderRadius: '8px',
                          border: '1px solid var(--border-subtle)',
                        }}
                      >
                        <div>
                          <strong>{alert.name}</strong> — <span style={{ color: 'var(--red-primary)' }}>{alert.specialty}</span>
                          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                            {alert.email} • Applied on {new Date(alert.created_at).toLocaleDateString()}
                          </div>
                        </div>
                        <Button
                          variant="primary"
                          size="sm"
                          onClick={() => {
                            setAppStatusFilter('pending');
                            handleTabSwitch('applications');
                          }}
                        >
                          Review <ChevronRight size={14} />
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recent Activity Stream */}
              <div className="admin-section-card">
                <h3>
                  <Activity size={20} color="var(--red-primary)" /> Recent Administrative Activity
                </h3>
                {!overviewData.recent_activity || overviewData.recent_activity.length === 0 ? (
                  <p style={{ color: 'var(--text-muted)' }}>No recent activity records found.</p>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
                    {overviewData.recent_activity.map((item) => (
                      <div key={item.id} className="audit-event-item">
                        <span
                          className={`audit-source-pill ${
                            item.source === 'admin_audit' ? 'source-admin-audit' : 'source-appointment-history'
                          }`}
                        >
                          {item.source === 'admin_audit' ? 'Admin Audit' : 'Appointment'}
                        </span>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '4px' }}>
                            <strong style={{ color: 'var(--text-primary)' }}>{item.action}</strong>
                            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                              {new Date(item.created_at).toLocaleString()}
                            </span>
                          </div>
                          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                            Actor: <strong>{item.actor || 'System'}</strong>
                            {item.appointment_id && <span> • Appt #{item.appointment_id}</span>}
                            {item.doctor_id && <span> • Doctor #{item.doctor_id}</span>}
                            {item.from_status && item.to_status && (
                              <span>
                                {' '}
                                • Status: <code>{item.from_status}</code> → <code>{item.to_status}</code>
                              </span>
                            )}
                            {item.reason && <span> • Reason: {item.reason}</span>}
                          </div>
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

      {/* =======================================================================
       * TAB 2: DOCTOR APPLICATIONS
       * ======================================================================= */}
      {activeTab === 'applications' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Status Filter */}
          <div className="admin-filter-toolbar">
            <div className="admin-filter-group">
              <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Application Status:</span>
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
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Showing {applications.length} applications
            </span>
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
                      <span className="request-detail-label">Qualifications</span>
                      <span className="request-detail-val">{app.qualifications}</span>
                    </div>
                    <div className="request-detail-item">
                      <span className="request-detail-label">Medical Registration No.</span>
                      <span className="request-detail-val">
                        <strong>{app.registration_number}</strong>
                      </span>
                    </div>
                    {app.registration_authority && (
                      <div className="request-detail-item">
                        <span className="request-detail-label">Registration Authority</span>
                        <span className="request-detail-val">{app.registration_authority}</span>
                      </div>
                    )}
                    <div className="request-detail-item">
                      <span className="request-detail-label">Clinical Experience</span>
                      <span className="request-detail-val">{app.years_experience} years</span>
                    </div>
                    {app.clinic_name && (
                      <div className="request-detail-item">
                        <span className="request-detail-label">Clinic / Hospital</span>
                        <span className="request-detail-val">{app.clinic_name}</span>
                      </div>
                    )}
                  </div>

                  {app.address && (
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                      <strong>Practice Address:</strong> {app.address}
                    </div>
                  )}

                  {app.bio && (
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                      <strong>Practitioner Bio:</strong> {app.bio}
                    </div>
                  )}

                  {/* Supporting Documents */}
                  {app.documents && app.documents.length > 0 && (
                    <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '0.75rem' }}>
                      <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                        Attached Verification Documents:
                      </span>
                      <div style={{ display: 'flex', gap: '0.65rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
                        {app.documents.map((doc) => (
                          <Button
                            key={doc.id}
                            variant="secondary"
                            size="sm"
                            disabled={downloadingDocId === doc.id}
                            onClick={() => handleDownloadDoc(doc.id, doc.document_type)}
                          >
                            <Download size={14} />
                            {doc.document_type.replace('_', ' ')}
                            {downloadingDocId === doc.id && ' ...'}
                          </Button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Review Outcome info */}
                  {app.reviewed_at && (
                    <div
                      style={{
                        background: 'var(--bg-secondary)',
                        padding: '0.75rem',
                        borderRadius: '8px',
                        fontSize: '0.85rem',
                        marginTop: '0.5rem',
                      }}
                    >
                      <div>
                        <strong>Reviewed by:</strong> {app.reviewed_by || 'Staff'} on{' '}
                        {new Date(app.reviewed_at).toLocaleString()}
                      </div>
                      {app.review_note && (
                        <div style={{ marginTop: '0.25rem' }}>
                          <strong>Review Note:</strong> {app.review_note}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Action Button for Pending */}
                  {app.status === 'pending' && (
                    <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
                      <Button
                        variant="primary"
                        size="md"
                        onClick={() => {
                          setReviewingApp(app);
                          setDecision('approve');
                          setReviewNote('');
                        }}
                      >
                        <ShieldAlert size={16} /> Review Application
                      </Button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* =======================================================================
       * TAB 3: DOCTOR MANAGEMENT
       * ======================================================================= */}
      {activeTab === 'doctors' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Filter Bar */}
          <div className="admin-filter-toolbar">
            <div className="admin-filter-group">
              <input
                type="text"
                className="admin-input-search"
                placeholder="Search name, email, specialty, ID..."
                value={doctorSearch}
                onChange={(e) => setDoctorSearch(e.target.value)}
              />
              <select
                className="admin-input-search"
                value={doctorStatusFilter}
                onChange={(e) => setDoctorStatusFilter(e.target.value)}
              >
                <option value="">All Statuses</option>
                <option value="approved">Approved</option>
                <option value="suspended">Suspended</option>
                <option value="pending">Pending</option>
                <option value="rejected">Rejected</option>
              </select>
              <select
                className="admin-input-search"
                value={doctorAvailFilter}
                onChange={(e) => setDoctorAvailFilter(e.target.value)}
              >
                <option value="">All Availability</option>
                <option value="true">Available</option>
                <option value="false">Unavailable</option>
              </select>
            </div>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Found {doctors.length} doctors
            </span>
          </div>

          {loadingDoctors ? (
            <Spinner />
          ) : doctors.length === 0 ? (
            <div className="doctor-empty-state">
              <Stethoscope size={48} />
              <h3>No doctors found</h3>
              <p>No doctor profiles match your current search and filters.</p>
            </div>
          ) : (
            <div className="admin-table-container">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Doctor ID</th>
                    <th>Practitioner</th>
                    <th>Specialty</th>
                    <th>Reg. Number</th>
                    <th>Status</th>
                    <th>Availability</th>
                    <th>Appointments</th>
                    <th>Verified</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {doctors.map((doc) => (
                    <tr key={doc.id}>
                      <td>
                        <strong>{doc.doctor_id || `ID #${doc.id}`}</strong>
                      </td>
                      <td>
                        <div>
                          <strong>{doc.full_name}</strong>
                          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>{doc.email}</div>
                          {doc.clinic_name && (
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{doc.clinic_name}</div>
                          )}
                        </div>
                      </td>
                      <td>
                        <span style={{ color: 'var(--red-primary)', fontWeight: 600 }}>{doc.specialty}</span>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                          {doc.years_experience} yrs exp
                        </div>
                      </td>
                      <td>
                        <code>{doc.registration_number}</code>
                      </td>
                      <td>
                        <span className={`status-pill status-${doc.status}`}>{doc.status}</span>
                      </td>
                      <td>
                        <span
                          style={{
                            fontSize: '0.8rem',
                            color: doc.is_available ? 'var(--emerald)' : 'var(--text-muted)',
                            fontWeight: 600,
                          }}
                        >
                          {doc.is_available ? 'Available' : 'Unavailable'}
                        </span>
                      </td>
                      <td>
                        <div style={{ fontSize: '0.8rem' }}>
                          <span>Total: <strong>{doc.appointments_total}</strong></span><br />
                          <span style={{ color: 'var(--emerald)' }}>Done: {doc.appointments_completed}</span> •{' '}
                          <span style={{ color: 'var(--warning)' }}>Req: {doc.appointments_pending}</span>
                        </div>
                      </td>
                      <td>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                          {doc.verified_at ? new Date(doc.verified_at).toLocaleDateString() : '—'}
                        </span>
                      </td>
                      <td>
                        {doc.status === 'approved' && (
                          <Button
                            variant="danger"
                            size="sm"
                            onClick={() => {
                              setSelectedDoctorForAction(doc);
                              setDoctorActionType('suspend');
                              setActionReason('');
                            }}
                          >
                            <Ban size={13} /> Suspend
                          </Button>
                        )}
                        {doc.status === 'suspended' && (
                          <Button
                            variant="primary"
                            size="sm"
                            onClick={() => {
                              setSelectedDoctorForAction(doc);
                              setDoctorActionType('reactivate');
                              setActionReason('');
                            }}
                          >
                            <CheckCircle2 size={13} /> Reactivate
                          </Button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* =======================================================================
       * TAB 4: APPOINTMENT MANAGEMENT
       * ======================================================================= */}
      {activeTab === 'appointments' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Privacy Notice */}
          <div
            style={{
              padding: '0.75rem 1rem',
              borderRadius: '8px',
              background: 'rgba(59, 130, 246, 0.1)',
              border: '1px solid rgba(59, 130, 246, 0.3)',
              color: 'var(--text-primary)',
              fontSize: '0.85rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.65rem',
            }}
          >
            <Info size={18} color="#3b82f6" />
            <span>
              <strong>Administrative Privacy Guard:</strong> Patient clinical narratives and consultation notes are
              confidential medical data and are redacted from administrative views per backend privacy architecture.
            </span>
          </div>

          {/* Filter Bar */}
          <div className="admin-filter-toolbar">
            <div className="admin-filter-group">
              <select
                className="admin-input-search"
                value={apptStatusFilter}
                onChange={(e) => setApptStatusFilter(e.target.value)}
              >
                <option value="">All Statuses</option>
                <option value="requested">Requested</option>
                <option value="accepted">Accepted</option>
                <option value="rejected">Rejected</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>

              <input
                type="text"
                className="admin-input-search"
                placeholder="Doctor ID..."
                style={{ width: '110px', minWidth: '110px' }}
                value={apptDoctorId}
                onChange={(e) => setApptDoctorId(e.target.value)}
              />

              <input
                type="text"
                className="admin-input-search"
                placeholder="Patient Account ID..."
                style={{ width: '140px', minWidth: '140px' }}
                value={apptPatientId}
                onChange={(e) => setApptPatientId(e.target.value)}
              />

              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>From:</span>
                <input
                  type="date"
                  className="admin-input-search"
                  value={apptDateFrom}
                  onChange={(e) => setApptDateFrom(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>To:</span>
                <input
                  type="date"
                  className="admin-input-search"
                  value={apptDateTo}
                  onChange={(e) => setApptDateTo(e.target.value)}
                />
              </div>
            </div>

            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Total: {appointments.length}
            </span>
          </div>

          {loadingAppointments ? (
            <Spinner />
          ) : appointments.length === 0 ? (
            <div className="doctor-empty-state">
              <Calendar size={48} />
              <h3>No appointments found</h3>
              <p>No appointments match the specified administrative query.</p>
            </div>
          ) : (
            <div className="admin-table-container">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Appt ID</th>
                    <th>Status</th>
                    <th>Patient Profile</th>
                    <th>Doctor</th>
                    <th>Timing</th>
                    <th>Response / Decision</th>
                    <th>Audit</th>
                    <th>History</th>
                  </tr>
                </thead>
                <tbody>
                  {appointments.map((appt) => (
                    <tr key={appt.id}>
                      <td>
                        <strong>#{appt.id}</strong>
                      </td>
                      <td>
                        <span className={`status-pill status-${appt.status}`}>{appt.status}</span>
                      </td>
                      <td>
                        <div>
                          <strong>{appt.member_name}</strong>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                            {appt.patient_email} (Acc #{appt.patient_account_id})
                          </div>
                        </div>
                      </td>
                      <td>
                        <div>
                          <strong>{appt.doctor_name}</strong>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                            {appt.doctor_email} (Doc #{appt.doctor_id})
                          </div>
                        </div>
                      </td>
                      <td>
                        <div style={{ fontSize: '0.8rem' }}>
                          <div>
                            <strong>Preferred:</strong> {new Date(appt.preferred_at).toLocaleString()}
                          </div>
                          {appt.scheduled_at && (
                            <div style={{ color: 'var(--emerald)' }}>
                              <strong>Scheduled:</strong> {new Date(appt.scheduled_at).toLocaleString()}
                            </div>
                          )}
                        </div>
                      </td>
                      <td>
                        {appt.doctor_response ? (
                          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                            {appt.doctor_response}
                          </span>
                        ) : (
                          <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>—</span>
                        )}
                      </td>
                      <td>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                          <div>Req: {appt.requested_by_email}</div>
                          {appt.booked_by_email && <div>Booked: {appt.booked_by_email}</div>}
                        </div>
                      </td>
                      <td>
                        <Button variant="secondary" size="sm" onClick={() => handleOpenHistory(appt.id)}>
                          <Clock size={13} /> History
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* =======================================================================
       * TAB 5: PATIENT ACCOUNTS
       * ======================================================================= */}
      {activeTab === 'patients' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="admin-filter-toolbar">
            <div className="admin-filter-group">
              <input
                type="text"
                className="admin-input-search"
                placeholder="Search patient email..."
                value={patientSearch}
                onChange={(e) => setPatientSearch(e.target.value)}
              />
            </div>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Showing {patients.length} patient accounts
            </span>
          </div>

          {loadingPatients ? (
            <Spinner />
          ) : patients.length === 0 ? (
            <div className="doctor-empty-state">
              <Users size={48} />
              <h3>No patient accounts found</h3>
              <p>No patient records found matching your query.</p>
            </div>
          ) : (
            <div className="admin-table-container">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Account ID</th>
                    <th>Email Address</th>
                    <th>Status</th>
                    <th>Family Profiles Registered</th>
                    <th>Account Created</th>
                  </tr>
                </thead>
                <tbody>
                  {patients.map((pat) => (
                    <tr key={pat.id}>
                      <td>
                        <strong>#{pat.id}</strong>
                      </td>
                      <td>
                        <strong>{pat.email}</strong>
                      </td>
                      <td>
                        <span className="status-pill status-approved">{pat.account_status}</span>
                      </td>
                      <td>
                        <span
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '4px',
                            fontWeight: 600,
                            color: 'var(--purple-500, #a855f7)',
                          }}
                        >
                          <Users size={14} /> {pat.family_profile_count} {pat.family_profile_count === 1 ? 'profile' : 'profiles'}
                        </span>
                      </td>
                      <td>
                        <span style={{ fontSize: '0.825rem', color: 'var(--text-muted)' }}>
                          {new Date(pat.created_at).toLocaleString()}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* =======================================================================
       * TAB 6: DOCTOR INVITATIONS
       * ======================================================================= */}
      {activeTab === 'invitations' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="admin-filter-toolbar">
            <span style={{ fontSize: '0.9rem', color: 'var(--text-primary)' }}>
              <strong>Sent Doctor Onboarding Invitations</strong>
            </span>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Total: {invitations.length}
            </span>
          </div>

          {loadingInvs ? (
            <Spinner />
          ) : invitations.length === 0 ? (
            <div className="doctor-empty-state">
              <Mail size={48} />
              <h3>No invitations found</h3>
              <p>Click "Send Doctor Invitation" to invite medical practitioners to join MedLife.</p>
            </div>
          ) : (
            <div className="admin-table-container">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Inv. ID</th>
                    <th>Invited Email</th>
                    <th>Status</th>
                    <th>Delivery</th>
                    <th>Account State</th>
                    <th>Expires At</th>
                    <th>Invited By</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {invitations.map((inv) => (
                    <tr key={inv.id}>
                      <td>
                        <strong>#{inv.id}</strong>
                      </td>
                      <td>
                        <strong>{inv.email}</strong>
                      </td>
                      <td>
                        <span className={`status-pill status-${inv.status}`}>{inv.status}</span>
                      </td>
                      <td>
                        <span style={{ fontSize: '0.8rem', color: 'var(--emerald)', fontWeight: 600 }}>
                          {inv.email_status}
                        </span>
                      </td>
                      <td>
                        {inv.account_created ? (
                          <span style={{ color: 'var(--emerald)', fontSize: '0.8rem', fontWeight: 600 }}>
                            <CheckCircle2 size={13} style={{ verticalAlign: 'middle' }} /> Account Active
                          </span>
                        ) : inv.activation_pending ? (
                          <span style={{ color: 'var(--warning)', fontSize: '0.8rem', fontWeight: 600 }}>
                            Activation Pending
                          </span>
                        ) : (
                          <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>Unclaimed</span>
                        )}
                      </td>
                      <td>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                          {new Date(inv.expires_at).toLocaleDateString()}
                        </span>
                      </td>
                      <td>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                          {inv.invited_by}
                        </span>
                      </td>
                      <td>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                          {new Date(inv.created_at).toLocaleDateString()}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* =======================================================================
       * TAB 7: ANALYTICS
       * ======================================================================= */}
      {activeTab === 'analytics' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {loadingAnalytics ? (
            <Spinner />
          ) : !analyticsData ? (
            <div className="doctor-empty-state">
              <AlertCircle size={48} />
              <p>Analytics metrics unavailable.</p>
            </div>
          ) : (
            <>
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '0.75rem 1rem',
                  background: 'var(--bg-card)',
                  borderRadius: '10px',
                  border: '1px solid var(--border-subtle)',
                  fontSize: '0.85rem',
                }}
              >
                <span>
                  <strong>Reporting Interval:</strong> Last 6 calendar months
                </span>
                <span style={{ color: 'var(--text-muted)' }}>
                  Generated: {new Date(analyticsData.generated_at).toLocaleString()}
                </span>
              </div>

              <div className="analytics-grid">
                {/* 1. Patient Registrations */}
                <div className="admin-section-card">
                  <h3>
                    <Users size={18} color="var(--purple-500, #a855f7)" /> Patient Registrations
                  </h3>
                  <div className="chart-bars-wrap">
                    {analyticsData.patient_registrations?.map((item) => {
                      const maxVal = Math.max(
                        ...analyticsData.patient_registrations.map((x) => x.count),
                        1
                      );
                      const heightPercent = Math.max((item.count / maxVal) * 100, 6);
                      return (
                        <div key={item.month} className="chart-bar-col">
                          <span className="chart-bar-val">{item.count}</span>
                          <div
                            className="chart-bar-fill"
                            style={{
                              height: `${heightPercent}%`,
                              background: 'linear-gradient(180deg, #a855f7 0%, rgba(168, 85, 247, 0.4) 100%)',
                            }}
                          />
                          <span className="chart-bar-label">{item.month.slice(5)}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* 2. Doctor Registrations */}
                <div className="admin-section-card">
                  <h3>
                    <UserCheck size={18} color="var(--emerald)" /> Doctor Account Registrations
                  </h3>
                  <div className="chart-bars-wrap">
                    {analyticsData.doctor_registrations?.map((item) => {
                      const maxVal = Math.max(
                        ...analyticsData.doctor_registrations.map((x) => x.count),
                        1
                      );
                      const heightPercent = Math.max((item.count / maxVal) * 100, 6);
                      return (
                        <div key={item.month} className="chart-bar-col">
                          <span className="chart-bar-val">{item.count}</span>
                          <div
                            className="chart-bar-fill"
                            style={{
                              height: `${heightPercent}%`,
                              background: 'linear-gradient(180deg, #10b981 0%, rgba(16, 185, 129, 0.4) 100%)',
                            }}
                          />
                          <span className="chart-bar-label">{item.month.slice(5)}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* 3. Doctor Applications */}
                <div className="admin-section-card">
                  <h3>
                    <ShieldAlert size={18} color="var(--red-primary)" /> Doctor Applications Submitted
                  </h3>
                  <div className="chart-bars-wrap">
                    {analyticsData.doctor_applications?.map((item) => {
                      const maxVal = Math.max(
                        ...analyticsData.doctor_applications.map((x) => x.count),
                        1
                      );
                      const heightPercent = Math.max((item.count / maxVal) * 100, 6);
                      return (
                        <div key={item.month} className="chart-bar-col">
                          <span className="chart-bar-val">{item.count}</span>
                          <div
                            className="chart-bar-fill"
                            style={{
                              height: `${heightPercent}%`,
                              background: 'linear-gradient(180deg, var(--red-primary) 0%, rgba(225, 29, 72, 0.4) 100%)',
                            }}
                          />
                          <span className="chart-bar-label">{item.month.slice(5)}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* 4. Appointment Bookings */}
                <div className="admin-section-card">
                  <h3>
                    <Calendar size={18} color="#3b82f6" /> Appointment Bookings
                  </h3>
                  <div className="chart-bars-wrap">
                    {analyticsData.appointment_bookings?.map((item) => {
                      const maxVal = Math.max(
                        ...analyticsData.appointment_bookings.map((x) => x.count),
                        1
                      );
                      const heightPercent = Math.max((item.count / maxVal) * 100, 6);
                      return (
                        <div key={item.month} className="chart-bar-col">
                          <span className="chart-bar-val">{item.count}</span>
                          <div
                            className="chart-bar-fill"
                            style={{
                              height: `${heightPercent}%`,
                              background: 'linear-gradient(180deg, #3b82f6 0%, rgba(59, 130, 246, 0.4) 100%)',
                            }}
                          />
                          <span className="chart-bar-label">{item.month.slice(5)}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* =======================================================================
       * TAB 8: AUDIT LOG
       * ======================================================================= */}
      {activeTab === 'audit_log' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="admin-filter-toolbar">
            <div className="admin-filter-group">
              <input
                type="text"
                className="admin-input-search"
                placeholder="Filter by action..."
                value={auditActionFilter}
                onChange={(e) => setAuditActionFilter(e.target.value)}
              />
              <input
                type="text"
                className="admin-input-search"
                placeholder="Filter by actor email..."
                value={auditActorFilter}
                onChange={(e) => setAuditActorFilter(e.target.value)}
              />
              <select
                className="admin-input-search"
                style={{ width: '120px', minWidth: '120px' }}
                value={auditLimit}
                onChange={(e) => setAuditLimit(e.target.value)}
              >
                <option value="50">Limit: 50</option>
                <option value="100">Limit: 100</option>
                <option value="200">Limit: 200</option>
              </select>
            </div>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Events shown: {auditEvents.length}
            </span>
          </div>

          {loadingAudit ? (
            <Spinner />
          ) : auditEvents.length === 0 ? (
            <div className="doctor-empty-state">
              <Activity size={48} />
              <h3>No audit events found</h3>
              <p>No audit log events match your query parameters.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
              {auditEvents.map((evt) => (
                <div key={evt.id} className="audit-event-item">
                  <span
                    className={`audit-source-pill ${
                      evt.source === 'admin_audit' ? 'source-admin-audit' : 'source-appointment-history'
                    }`}
                  >
                    {evt.source === 'admin_audit' ? 'Admin Audit' : 'Appointment'}
                  </span>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '4px' }}>
                      <strong style={{ color: 'var(--text-primary)' }}>{evt.action}</strong>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {new Date(evt.created_at).toLocaleString()}
                      </span>
                    </div>

                    <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                      Actor: <strong>{evt.actor || 'System'}</strong>
                      {evt.appointment_id && <span> • Appt ID: #{evt.appointment_id}</span>}
                      {evt.doctor_id && <span> • Doctor ID: #{evt.doctor_id}</span>}
                      {evt.member_id && <span> • Family Member ID: #{evt.member_id}</span>}
                      {evt.from_status && evt.to_status && (
                        <span>
                          {' '}
                          • Transition: <code>{evt.from_status}</code> → <code>{evt.to_status}</code>
                        </span>
                      )}
                      {evt.reason && <span> • Reason: {evt.reason}</span>}
                    </div>

                    {evt.metadata && Object.keys(evt.metadata).length > 0 && (
                      <div style={{ marginTop: '0.35rem' }}>
                        <Button variant="ghost" size="sm" onClick={() => setSelectedMetaEvent(evt)}>
                          <Eye size={13} /> View Metadata
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* =======================================================================
       * MODALS
       * ======================================================================= */}

      {/* 1. Review Doctor Application Modal */}
      {reviewingApp && (
        <Modal
          title={`Review Application: ${reviewingApp.full_name}`}
          subtitle={`Registration No: ${reviewingApp.registration_number} • Specialty: ${reviewingApp.specialty}`}
          onClose={() => setReviewingApp(null)}
        >
          <form onSubmit={handleReviewSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="form-group">
              <label>Decision</label>
              <div style={{ display: 'flex', gap: '1rem', marginTop: '0.25rem' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                  <input
                    type="radio"
                    name="decision"
                    value="approve"
                    checked={decision === 'approve'}
                    onChange={() => setDecision('approve')}
                  />
                  <span>
                    <strong>Approve Application</strong>
                  </span>
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                  <input
                    type="radio"
                    name="decision"
                    value="reject"
                    checked={decision === 'reject'}
                    onChange={() => setDecision('reject')}
                  />
                  <span>
                    <strong>Reject Application</strong>
                  </span>
                </label>
              </div>
            </div>

            {decision === 'approve' ? (
              <div
                style={{
                  background: 'rgba(16, 185, 129, 0.1)',
                  padding: '0.85rem',
                  borderRadius: '8px',
                  fontSize: '0.85rem',
                  color: 'var(--text-secondary)',
                }}
              >
                Approving this application will generate a secure, single-use 24-hour activation link emailed to{' '}
                <strong>{reviewingApp.email}</strong>. The practitioner will complete password setup and mandatory
                authenticator (TOTP) enrollment before an active doctor account is created.
              </div>
            ) : (
              <div
                style={{
                  background: 'rgba(239, 68, 68, 0.1)',
                  padding: '0.85rem',
                  borderRadius: '8px',
                  fontSize: '0.85rem',
                  color: 'var(--text-secondary)',
                }}
              >
                Rejecting this application requires an explicit explanation. This reason will be emailed directly to the
                applicant.
              </div>
            )}

            <div className="form-group">
              <label>
                {decision === 'reject' ? 'Rejection Reason (Required)' : 'Review Notes (Optional)'}
              </label>
              <textarea
                className="form-input"
                rows={3}
                placeholder={
                  decision === 'reject'
                    ? 'State the reason for rejection (e.g. invalid medical registration or insufficient verification documents)...'
                    : 'Internal review notes or remarks...'
                }
                value={reviewNote}
                onChange={(e) => setReviewNote(e.target.value)}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
              <Button type="button" variant="ghost" onClick={() => setReviewingApp(null)}>
                Cancel
              </Button>
              <Button
                type="submit"
                variant={decision === 'approve' ? 'primary' : 'danger'}
                disabled={submittingReview}
              >
                {submittingReview ? 'Submitting...' : decision === 'approve' ? 'Confirm Approval' : 'Confirm Rejection'}
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* 2. Doctor Suspend / Reactivate Modal */}
      {selectedDoctorForAction && (
        <Modal
          title={`${doctorActionType === 'suspend' ? 'Suspend' : 'Reactivate'} Doctor: ${selectedDoctorForAction.full_name}`}
          subtitle={`Doctor ID: ${selectedDoctorForAction.doctor_id || selectedDoctorForAction.id} • ${selectedDoctorForAction.email}`}
          onClose={() => setSelectedDoctorForAction(null)}
        >
          <form onSubmit={handleDoctorActionSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
              {doctorActionType === 'suspend'
                ? 'Suspending a doctor will set their status to suspended and immediately make them unavailable for consultations and bookings.'
                : 'Reactivating this doctor will restore their status to approved.'}
            </p>

            <div className="form-group">
              <label>Reason for Action (Optional)</label>
              <textarea
                className="form-input"
                rows={3}
                placeholder="State the administrative rationale..."
                value={actionReason}
                onChange={(e) => setActionReason(e.target.value)}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <Button type="button" variant="ghost" onClick={() => setSelectedDoctorForAction(null)}>
                Cancel
              </Button>
              <Button
                type="submit"
                variant={doctorActionType === 'suspend' ? 'danger' : 'primary'}
                disabled={submittingDoctorAction}
              >
                {submittingDoctorAction
                  ? 'Processing...'
                  : doctorActionType === 'suspend'
                  ? 'Confirm Suspension'
                  : 'Confirm Reactivation'}
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* 3. Appointment Lifecycle History Modal */}
      {historyAppointmentId && (
        <Modal
          title={`Appointment Lifecycle History: #${historyAppointmentId}`}
          subtitle="Chronological audit records of all state changes for this appointment"
          onClose={() => setHistoryAppointmentId(null)}
        >
          {loadingHistory ? (
            <Spinner />
          ) : appointmentHistory.length === 0 ? (
            <p style={{ color: 'var(--text-muted)' }}>No historical transitions recorded for this appointment.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '400px', overflowY: 'auto' }}>
              {appointmentHistory.map((item) => (
                <div
                  key={item.id}
                  style={{
                    padding: '0.85rem',
                    borderRadius: '8px',
                    background: 'var(--bg-secondary)',
                    border: '1px solid var(--border-subtle)',
                    fontSize: '0.85rem',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <strong>{item.action}</strong>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {new Date(item.created_at).toLocaleString()}
                    </span>
                  </div>
                  <div style={{ color: 'var(--text-secondary)', marginTop: '4px' }}>
                    Actor: <strong>{item.actor || 'System'}</strong>
                    {item.from_status && item.to_status && (
                      <span>
                        {' '}
                        • <code>{item.from_status}</code> → <code>{item.to_status}</code>
                      </span>
                    )}
                  </div>
                  {item.reason && (
                    <div style={{ marginTop: '4px', color: 'var(--text-secondary)' }}>
                      <strong>Reason / Remarks:</strong> {item.reason}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem' }}>
            <Button variant="secondary" onClick={() => setHistoryAppointmentId(null)}>
              Close
            </Button>
          </div>
        </Modal>
      )}

      {/* 4. Admin Book Appointment Modal */}
      {bookModalOpen && (
        <Modal
          title="Book Appointment (Administrative)"
          subtitle="Super Admin booking on behalf of patient family profile"
          onClose={() => {
            setBookModalOpen(false);
            setBookingModalError('');
          }}
        >
          {bookingModalError && <Banner variant="error">{bookingModalError}</Banner>}
          <form onSubmit={handleBookAppointmentSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div
              style={{
                fontSize: '0.825rem',
                color: 'var(--text-secondary)',
                background: 'rgba(59, 130, 246, 0.1)',
                padding: '0.75rem',
                borderRadius: '8px',
              }}
            >
              <strong>Security Rule:</strong> The patient profile must have active profile-sharing consent for the
              selected doctor before this booking can be submitted.
            </div>

            <div className="form-group">
              <label>Family Member ID (Patient Profile PK)</label>
              <input
                type="number"
                className="form-input"
                placeholder="e.g. 1"
                required
                value={bookMemberId}
                onChange={(e) => setBookMemberId(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>Doctor ID (Profile PK)</label>
              <input
                type="number"
                className="form-input"
                placeholder="e.g. 1"
                required
                value={bookDoctorId}
                onChange={(e) => setBookDoctorId(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>Preferred Date and Time</label>
              <input
                type="datetime-local"
                className="form-input"
                required
                value={bookPreferredAt}
                onChange={(e) => setBookPreferredAt(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>Reason for Appointment</label>
              <input
                type="text"
                className="form-input"
                placeholder="General consultation, follow-up..."
                value={bookReason}
                onChange={(e) => setBookReason(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>Administrative Notes</label>
              <textarea
                className="form-input"
                rows={2}
                placeholder="Administrative context..."
                value={bookPatientNote}
                onChange={(e) => setBookPatientNote(e.target.value)}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <Button type="button" variant="ghost" onClick={() => setBookModalOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" variant="primary" disabled={submittingBooking}>
                {submittingBooking ? 'Booking...' : 'Book Appointment'}
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* 5. Send Doctor Invitation Modal */}
      {inviteModalOpen && (
        <Modal
          title="Invite Medical Practitioner"
          subtitle="Generate a secure single-use invitation link delivered by email"
          onClose={() => {
            setInviteModalOpen(false);
            setInviteEmail('');
            setInviteModalError('');
          }}
        >
          {inviteModalError && <Banner variant="error">{inviteModalError}</Banner>}
          <form onSubmit={handleInviteSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
              An invitation email will be sent containing a secure 7-day token. The invited doctor will be able to
              accept the invitation and configure their account credentials.
            </p>

            <div className="form-group">
              <label>Practitioner Email Address</label>
              <input
                type="email"
                className="form-input"
                placeholder="doctor@example.com"
                required
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <Button type="button" variant="ghost" onClick={() => setInviteModalOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" variant="primary" disabled={submittingInvite}>
                {submittingInvite ? 'Sending...' : 'Send Invitation'}
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* 6. Metadata Viewer Modal */}
      {selectedMetaEvent && (
        <Modal
          title={`Event Metadata: ${selectedMetaEvent.action}`}
          subtitle={`Event ID: #${selectedMetaEvent.id} • Source: ${selectedMetaEvent.source}`}
          onClose={() => setSelectedMetaEvent(null)}
        >
          <pre
            style={{
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border-subtle)',
              padding: '1rem',
              borderRadius: '8px',
              fontSize: '0.8rem',
              overflowX: 'auto',
              maxHeight: '400px',
            }}
          >
            {JSON.stringify(selectedMetaEvent.metadata, null, 2)}
          </pre>
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem' }}>
            <Button variant="secondary" onClick={() => setSelectedMetaEvent(null)}>
              Close
            </Button>
          </div>
        </Modal>
      )}
    </div>
  );
}
