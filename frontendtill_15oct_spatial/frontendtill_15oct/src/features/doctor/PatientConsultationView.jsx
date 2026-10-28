import { useState, useEffect, useCallback } from 'react';
import Button from '../../components/Button/index.js';
import Spinner from '../../components/Spinner/index.js';
import Banner from '../../components/Banner/index.js';
import Modal from '../../components/Modal/index.js';
import DoctorChatModal from './DoctorChatModal.jsx';
import ConsultationNotesModal from './ConsultationNotesModal.jsx';
import {
  getPublicDoctors,
  getPublicDoctorAvailability,
  getAppointments,
  requestAppointment,
  cancelAppointment,
  requestAppointmentReschedule,
  getRescheduleRequests,
  decideRescheduleRequest,
  getChatRequests,
  requestChat,
  cancelChatRequest,
  getAccessGrants,
  createAccessGrant,
  revokeAccessGrant,
} from '../../services/api.js';
import {
  Stethoscope,
  Calendar,
  MessageSquare,
  ShieldCheck,
  Search,
  UserCheck,
  Clock,
  Ban,
  FileText,
  AlertCircle,
  Plus,
} from 'lucide-react';
import './doctor.css';

const WEEKDAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

const getNextDateForWeekdayTime = (weekday, timeStr) => {
  const now = new Date();
  const [hours, minutes] = (timeStr || '09:00').split(':').map(Number);
  const currentPyDay = (now.getDay() + 6) % 7; // Monday=0..Sunday=6
  let daysAhead = (weekday - currentPyDay + 7) % 7;
  const target = new Date(now);
  target.setDate(now.getDate() + daysAhead);
  target.setHours(hours, minutes, 0, 0);
  if (target <= now) {
    target.setDate(target.getDate() + 7);
  }
  const pad = (n) => String(n).padStart(2, '0');
  return `${target.getFullYear()}-${pad(target.getMonth() + 1)}-${pad(target.getDate())}T${pad(target.getHours())}:${pad(target.getMinutes())}`;
};

const checkSlotMatch = (dateTimeStr, slots) => {
  if (!dateTimeStr || !slots || slots.length === 0) return true;
  const dt = new Date(dateTimeStr);
  if (isNaN(dt.getTime())) return false;
  const pyWeekday = (dt.getDay() + 6) % 7;
  const timeStr = `${String(dt.getHours()).padStart(2, '0')}:${String(dt.getMinutes()).padStart(2, '0')}`;
  return slots.some(
    (slot) => slot.weekday === pyWeekday && slot.start_time <= timeStr && timeStr < slot.end_time
  );
};

export default function PatientConsultationView({
  email,
  members = {},
  selectedMemberKey = '',
  initialTab = 'directory',
  targetAppointmentId = null,
  targetChatId = null,
}) {
  const [activeTab, setActiveTab] = useState(initialTab); // 'directory', 'appointments', 'chats', 'consent'
  const [doctors, setDoctors] = useState([]);
  const [specialtyFilter, setSpecialtyFilter] = useState('');
  const [loadingDoctors, setLoadingDoctors] = useState(false);

  const [appointments, setAppointments] = useState([]);
  const [loadingAppointments, setLoadingAppointments] = useState(false);

  const [chatRequests, setChatRequests] = useState([]);
  const [loadingChats, setLoadingChats] = useState(false);

  const [grants, setGrants] = useState([]);
  const [loadingGrants, setLoadingGrants] = useState(false);

  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Doctor availability state
  const [doctorAvailability, setDoctorAvailability] = useState(null);
  const [loadingAvailability, setLoadingAvailability] = useState(false);
  const [availabilityError, setAvailabilityError] = useState('');

  // Rescheduling state
  const [rescheduleRequests, setRescheduleRequests] = useState([]);
  const [loadingReschedules, setLoadingReschedules] = useState(false);
  const [rescheduleModalApt, setRescheduleModalApt] = useState(null);
  const [rescheduleDoctorAvailability, setRescheduleDoctorAvailability] = useState(null);
  const [loadingRescheduleAvailability, setLoadingRescheduleAvailability] = useState(false);
  const [rescheduleForm, setRescheduleForm] = useState({
    proposed_at: '',
    reason: '',
  });
  const [rescheduleModalError, setRescheduleModalError] = useState('');
  const [submittingReschedule, setSubmittingReschedule] = useState(false);
  const [decidingRescheduleId, setDecidingRescheduleId] = useState(null);

  // Modal-specific error & submission states
  const [bookingModalError, setBookingModalError] = useState('');
  const [submittingBooking, setSubmittingBooking] = useState(false);
  const [chatModalError, setChatModalError] = useState('');
  const [submittingChat, setSubmittingChat] = useState(false);

  // Modals
  const [bookingDoctor, setBookingDoctor] = useState(null); // doctor obj
  const [chatTargetDoctor, setChatTargetDoctor] = useState(null);
  const [activeChatRequest, setActiveChatRequest] = useState(null);
  const [activeNoteAppointment, setActiveNoteAppointment] = useState(null);
  const [grantModalOpen, setGrantModalOpen] = useState(false);

  // Form states for booking appointment
  const [bookingForm, setBookingForm] = useState({
    member_id: '',
    member_key: selectedMemberKey || Object.keys(members)[0] || '',
    preferred_at: '',
    reason: '',
    patient_note: '',
    consent_scopes: ['profile', 'documents', 'consultation_notes'],
  });

  // Form states for requesting chat
  const [chatForm, setChatForm] = useState({
    member_id: '',
    member_key: selectedMemberKey || Object.keys(members)[0] || '',
    message: '',
    consent_scopes: ['profile'],
  });

  // Form states for granting consent
  const [consentForm, setConsentForm] = useState({
    member_id: '',
    member_key: selectedMemberKey || Object.keys(members)[0] || '',
    doctor_id: '',
    scopes: ['profile', 'documents', 'consultation_notes'],
  });

  // Load doctor availability
  const loadDoctorAvailability = useCallback(async (doctorId) => {
    if (!doctorId) return;
    try {
      setLoadingAvailability(true);
      setAvailabilityError('');
      const data = await getPublicDoctorAvailability(doctorId);
      setDoctorAvailability(data);
    } catch (e) {
      setAvailabilityError(e.message || 'Unable to retrieve doctor availability.');
    } finally {
      setLoadingAvailability(false);
    }
  }, []);

  // Fetch availability when selected booking doctor changes
  useEffect(() => {
    if (bookingDoctor?.id) {
      loadDoctorAvailability(bookingDoctor.id);
    } else {
      setDoctorAvailability(null);
      setAvailabilityError('');
    }
  }, [bookingDoctor, loadDoctorAvailability]);

  // Load doctors
  const loadDoctors = useCallback(async () => {
    try {
      setLoadingDoctors(true);
      setError('');
      const data = await getPublicDoctors(specialtyFilter);
      setDoctors(data?.doctors || []);
    } catch (e) {
      setError(e.message || 'Unable to load doctors.');
    } finally {
      setLoadingDoctors(false);
    }
  }, [specialtyFilter]);

  // Load patient appointments
  const loadAppointments = useCallback(async () => {
    try {
      setLoadingAppointments(true);
      const data = await getAppointments('patient');
      setAppointments(data?.appointments || []);
    } catch (e) {
      // Non-blocking
    } finally {
      setLoadingAppointments(false);
    }
  }, []);

  // Load patient reschedule requests
  const loadReschedules = useCallback(async () => {
    try {
      setLoadingReschedules(true);
      const data = await getRescheduleRequests('patient');
      setRescheduleRequests(data?.reschedule_requests || []);
    } catch {
      // Non-blocking
    } finally {
      setLoadingReschedules(false);
    }
  }, []);

  // Load patient chat requests
  const loadChats = useCallback(async () => {
    try {
      setLoadingChats(true);
      const data = await getChatRequests('patient');
      setChatRequests(data?.chat_requests || []);
    } catch (e) {
      // Non-blocking
    } finally {
      setLoadingChats(false);
    }
  }, []);

  // Load access grants
  const loadGrants = useCallback(async () => {
    try {
      setLoadingGrants(true);
      const data = await getAccessGrants();
      setGrants(data?.grants || []);
    } catch (e) {
      // Non-blocking
    } finally {
      setLoadingGrants(false);
    }
  }, []);

  useEffect(() => {
    loadDoctors();
  }, [loadDoctors]);

  useEffect(() => {
    if (activeTab === 'appointments') {
      loadAppointments();
      loadReschedules();
    }
    if (activeTab === 'chats') loadChats();
    if (activeTab === 'consent') loadGrants();
  }, [activeTab, loadAppointments, loadReschedules, loadChats, loadGrants]);

  // Direct navigation from notification
  useEffect(() => {
    if (targetAppointmentId) {
      setActiveTab('appointments');
      loadAppointments();
      loadReschedules();
    }
    if (targetChatId) {
      setActiveTab('chats');
      loadChats();
    }
  }, [targetAppointmentId, targetChatId, loadAppointments, loadReschedules, loadChats]);

  // Map known member names to database member_id from appointments/grants
  const memberIdMap = {};
  grants.forEach((g) => {
    if (g.member_name && g.member_id) {
      memberIdMap[g.member_name] = g.member_id;
    }
  });
  appointments.forEach((a) => {
    if (a.member_name && a.member_id) {
      memberIdMap[a.member_name] = a.member_id;
    }
  });
  chatRequests.forEach((c) => {
    if (c.member_name && c.member_id) {
      memberIdMap[c.member_name] = c.member_id;
    }
  });

  // Helper to resolve effective member ID
  const getResolvedMemberId = (selectedKey, manualId) => {
    if (manualId && !isNaN(Number(manualId))) {
      return Number(manualId);
    }
    const mem = members[selectedKey];
    if (mem?.id) return Number(mem.id);
    const fullName = `${mem?.firstName || ''} ${mem?.lastName || ''}`.trim();
    if (fullName && memberIdMap[fullName]) {
      return memberIdMap[fullName];
    }
    // Check if existing grants have the real database member_id
    const matchedGrant = grants.find(
      (g) => g.member_name && fullName && g.member_name.toLowerCase() === fullName.toLowerCase()
    );
    if (matchedGrant?.member_id) {
      return matchedGrant.member_id;
    }
    // Fallback slot number if database pk happens to be 1-indexed slot
    const slotMatch = selectedKey.match(/\d+/);
    if (slotMatch) return Number(slotMatch[0]);
    return 1;
  };

  // Handle appointment booking submit
  const handleBookAppointment = async (e) => {
    e.preventDefault();
    if (!bookingDoctor) return;
    setBookingModalError('');
    setError('');
    setSuccess('');

    // Ensure timezone offset is included in ISO string
    let isoPreferredAt = '';
    try {
      const dateObj = new Date(bookingForm.preferred_at);
      if (isNaN(dateObj.getTime())) throw new Error();
      if (dateObj <= new Date()) {
        setBookingModalError('Please select a future appointment date and time.');
        return;
      }
      isoPreferredAt = dateObj.toISOString();
    } catch {
      setBookingModalError('Please provide a valid appointment date and time.');
      return;
    }

    // Availability validation if doctor has configured slots
    if (doctorAvailability?.has_configured_slots) {
      if (!doctorAvailability.slots || doctorAvailability.slots.length === 0) {
        setBookingModalError('This doctor has no active weekly availability slots configured. Booking is unavailable.');
        return;
      }
      if (!checkSlotMatch(bookingForm.preferred_at, doctorAvailability.slots)) {
        setBookingModalError("The selected time is outside the doctor's active configured availability. Please choose a slot from the weekly schedule.");
        return;
      }
    }

    const memberId = getResolvedMemberId(bookingForm.member_key, bookingForm.member_id);
    setSubmittingBooking(true);

    try {
      await requestAppointment({
        member_id: memberId,
        doctor_id: bookingDoctor.id,
        preferred_at: isoPreferredAt,
        reason: bookingForm.reason.trim(),
        patient_note: bookingForm.patient_note.trim(),
        consent_scopes: bookingForm.consent_scopes,
      });
      setSuccess(`Appointment request sent to ${bookingDoctor.name}. Awaiting doctor confirmation.`);
      const savedDocId = bookingDoctor.id;
      setBookingDoctor(null);
      setBookingModalError('');
      setActiveTab('appointments');
      loadAppointments();
      loadReschedules();
      if (savedDocId) {
        loadDoctorAvailability(savedDocId);
      }
    } catch (err) {
      const msg = err.message || 'Unable to request appointment.';
      setBookingModalError(msg);
      setError(msg);
    } finally {
      setSubmittingBooking(false);
    }
  };

  // Open reschedule modal for an appointment
  const handleOpenReschedule = async (apt) => {
    setRescheduleModalApt(apt);
    setRescheduleModalError('');
    setRescheduleForm({
      proposed_at: '',
      reason: '',
    });
    setRescheduleDoctorAvailability(null);
    if (apt.doctor_id) {
      try {
        setLoadingRescheduleAvailability(true);
        const data = await getPublicDoctorAvailability(apt.doctor_id);
        setRescheduleDoctorAvailability(data);
      } catch {
        // Non-blocking
      } finally {
        setLoadingRescheduleAvailability(false);
      }
    }
  };

  // Submit rescheduling request
  const handleRequestReschedule = async (e) => {
    e.preventDefault();
    if (!rescheduleModalApt) return;
    setRescheduleModalError('');
    setError('');
    setSuccess('');

    let isoProposed = '';
    try {
      const dt = new Date(rescheduleForm.proposed_at);
      if (isNaN(dt.getTime())) throw new Error();
      if (dt <= new Date()) {
        setRescheduleModalError('Proposed appointment date and time must be in the future.');
        return;
      }
      isoProposed = dt.toISOString();
    } catch {
      setRescheduleModalError('Please provide a valid date and time for proposed rescheduling.');
      return;
    }

    if (rescheduleDoctorAvailability?.has_configured_slots) {
      if (!rescheduleDoctorAvailability.slots || rescheduleDoctorAvailability.slots.length === 0) {
        setRescheduleModalError('This doctor has no active availability slots configured.');
        return;
      }
      if (!checkSlotMatch(rescheduleForm.proposed_at, rescheduleDoctorAvailability.slots)) {
        setRescheduleModalError("The proposed time is outside the doctor's active configured availability. Please choose a slot from the weekly schedule.");
        return;
      }
    }

    setSubmittingReschedule(true);
    try {
      await requestAppointmentReschedule(
        rescheduleModalApt.id,
        isoProposed,
        rescheduleForm.reason.trim()
      );
      setSuccess(`Reschedule request submitted for Appointment #${rescheduleModalApt.id}.`);
      setRescheduleModalApt(null);
      loadAppointments();
      loadReschedules();
    } catch (err) {
      setRescheduleModalError(err.message || 'Unable to submit rescheduling request.');
    } finally {
      setSubmittingReschedule(false);
    }
  };

  // Decide reschedule request (accept or reject doctor-proposed new time)
  const handleRescheduleDecision = async (requestId, decision) => {
    if (!window.confirm(`Are you sure you want to ${decision} this rescheduling proposal?`)) return;
    setError('');
    setSuccess('');
    setDecidingRescheduleId(requestId);
    try {
      await decideRescheduleRequest(requestId, decision);
      setSuccess(`Rescheduling proposal was ${decision}ed.`);
      loadAppointments();
      loadReschedules();
    } catch (err) {
      setError(err.message || 'Unable to update rescheduling request.');
    } finally {
      setDecidingRescheduleId(null);
    }
  };

  // Handle online chat request submit
  const handleRequestChat = async (e) => {
    e.preventDefault();
    if (!chatTargetDoctor) return;
    setChatModalError('');
    setError('');
    setSuccess('');

    const memberId = getResolvedMemberId(chatForm.member_key, chatForm.member_id);
    setSubmittingChat(true);

    try {
      await requestChat({
        member_id: memberId,
        doctor_id: chatTargetDoctor.id,
        message: chatForm.message.trim(),
        consent_scopes: chatForm.consent_scopes,
      });
      setSuccess(`Consultation chat request sent to ${chatTargetDoctor.name}. Awaiting doctor acceptance.`);
      setChatTargetDoctor(null);
      setChatModalError('');
      setActiveTab('chats');
      loadChats();
    } catch (err) {
      const msg = err.message || 'Unable to request online consultation.';
      setChatModalError(msg);
      setError(msg);
    } finally {
      setSubmittingChat(false);
    }
  };

  // Handle cancel appointment
  const handleCancelAppointment = async (appointmentId) => {
    if (!window.confirm('Are you sure you want to cancel this appointment request?')) return;
    setError('');
    try {
      await cancelAppointment(appointmentId);
      loadAppointments();
      loadReschedules();
      setSuccess('Appointment cancelled successfully.');
    } catch (err) {
      setError(err.message || 'Unable to cancel appointment.');
    }
  };

  // Handle cancel chat request
  const handleCancelChat = async (chatId) => {
    if (!window.confirm('Are you sure you want to cancel this online consultation request?')) return;
    setError('');
    try {
      await cancelChatRequest(chatId);
      loadChats();
      setSuccess('Online consultation request cancelled.');
    } catch (err) {
      setError(err.message || 'Unable to cancel chat request.');
    }
  };

  // Handle grant consent
  const handleGrantConsent = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    const memberId = getResolvedMemberId(consentForm.member_key, consentForm.member_id);
    if (!consentForm.doctor_id) {
      setError('Please select an approved doctor.');
      return;
    }
    try {
      await createAccessGrant(memberId, Number(consentForm.doctor_id), consentForm.scopes);
      setSuccess('Medical record sharing consent granted successfully.');
      setGrantModalOpen(false);
      loadGrants();
    } catch (err) {
      setError(err.message || 'Unable to grant record sharing consent.');
    }
  };

  // Handle revoke consent
  const handleRevokeConsent = async (grantId) => {
    if (!window.confirm('Revoke doctor access to this family member medical record?')) return;
    setError('');
    try {
      await revokeAccessGrant(grantId);
      loadGrants();
      setSuccess('Record access consent revoked.');
    } catch (err) {
      setError(err.message || 'Unable to revoke consent.');
    }
  };

  return (
    <div className="doctor-system-container">
      {/* Header */}
      <div className="doctor-header-card">
        <div>
          <h2>Doctor Consultations & Appointments</h2>
          <p>Connect with verified healthcare practitioners, schedule consultations, and manage medical data sharing</p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <Button
            variant="secondary"
            size="md"
            onClick={() => {
              setGrantModalOpen(true);
            }}
          >
            <ShieldCheck size={16} /> Manage Record Consent
          </Button>
        </div>
      </div>

      {error && <Banner variant="error">{error}</Banner>}
      {success && <Banner variant="info">{success}</Banner>}

      {/* Navigation Tabs */}
      <div className="doctor-nav-tabs">
        <button
          className={`doctor-tab-btn ${activeTab === 'directory' ? 'active' : ''}`}
          onClick={() => setActiveTab('directory')}
        >
          <Stethoscope size={17} /> Find Doctors
          {doctors.length > 0 && <span className="doctor-badge-count">{doctors.length}</span>}
        </button>
        <button
          className={`doctor-tab-btn ${activeTab === 'appointments' ? 'active' : ''}`}
          onClick={() => setActiveTab('appointments')}
        >
          <Calendar size={17} /> My Appointments
          {appointments.length > 0 && <span className="doctor-badge-count">{appointments.length}</span>}
        </button>
        <button
          className={`doctor-tab-btn ${activeTab === 'chats' ? 'active' : ''}`}
          onClick={() => setActiveTab('chats')}
        >
          <MessageSquare size={17} /> Online Consultations
          {chatRequests.length > 0 && <span className="doctor-badge-count">{chatRequests.length}</span>}
        </button>
        <button
          className={`doctor-tab-btn ${activeTab === 'consent' ? 'active' : ''}`}
          onClick={() => setActiveTab('consent')}
        >
          <ShieldCheck size={17} /> Record Sharing Consent
          {grants.filter((g) => g.active).length > 0 && (
            <span className="doctor-badge-count">{grants.filter((g) => g.active).length}</span>
          )}
        </button>
      </div>

      {/* TAB 1: DOCTORS DIRECTORY */}
      {activeTab === 'directory' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Search bar */}
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            <div style={{ position: 'relative', flex: 1 }}>
              <input
                type="text"
                className="doctor-form-input"
                placeholder="Search by medical specialty (e.g. Cardiology, Pediatrics)..."
                value={specialtyFilter}
                onChange={(e) => setSpecialtyFilter(e.target.value)}
              />
            </div>
            <Button variant="secondary" size="md" onClick={loadDoctors}>
              <Search size={16} /> Filter
            </Button>
          </div>

          {loadingDoctors ? (
            <Spinner />
          ) : doctors.length === 0 ? (
            <div className="doctor-empty-state">
              <Stethoscope size={48} />
              <h3>No approved doctors found</h3>
              <p>There are currently no verified doctors matching your search criteria.</p>
            </div>
          ) : (
            <div className="doctors-grid">
              {doctors.map((doc) => (
                <div key={doc.id} className="doctor-card">
                  <div className="doctor-card-top">
                    <div className="doctor-avatar-circle">
                      {doc.name ? doc.name.replace(/^Dr\.?\s*/i, '')[0]?.toUpperCase() : 'D'}
                    </div>
                    <div className="doctor-info" style={{ flex: 1 }}>
                      <h3>{doc.name}</h3>
                      <div className="doctor-specialty">{doc.specialty}</div>
                    </div>
                  </div>

                  <div className="doctor-card-meta">
                    <span>
                      <UserCheck size={14} /> {doc.qualifications}
                    </span>
                    {doc.years_experience > 0 && <span>• {doc.years_experience} yrs exp</span>}
                    {doc.clinic_name && <span>• {doc.clinic_name}</span>}
                  </div>

                  {doc.bio && <p className="doctor-bio">{doc.bio}</p>}

                  <div className="doctor-card-actions">
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => setBookingDoctor(doc)}
                      title="Schedule in-person or video consultation"
                    >
                      <Calendar size={15} /> Book Appointment
                    </Button>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => setChatTargetDoctor(doc)}
                      title="Request direct online consultation chat"
                    >
                      <MessageSquare size={15} /> Request Chat
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 2: APPOINTMENTS */}
      {activeTab === 'appointments' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {loadingAppointments ? (
            <Spinner />
          ) : appointments.length === 0 ? (
            <div className="doctor-empty-state">
              <Calendar size={48} />
              <h3>No appointment requests</h3>
              <p>You have not booked any consultations yet. Explore the doctor directory to request one.</p>
              <Button variant="primary" size="md" onClick={() => setActiveTab('directory')}>
                Find a Doctor
              </Button>
            </div>
          ) : (
            <div className="requests-list">
              {appointments.map((apt) => {
                const pendingReschedule = rescheduleRequests.find(
                  (r) => r.appointment_id === apt.id && r.status === 'pending'
                );
                const canCancel = apt.status === 'requested' || apt.status === 'accepted';
                const canReschedule = apt.status === 'accepted' && !pendingReschedule;
                const isMyRescheduleProposal =
                  pendingReschedule?.requested_by &&
                  email &&
                  pendingReschedule.requested_by.toLowerCase() === email.toLowerCase();

                return (
                  <div key={apt.id} className="request-item-card">
                    <div className="request-item-header">
                      <div className="request-item-title">
                        <Calendar size={18} color="var(--red-primary)" />
                        <span>Appointment #{apt.id}</span>
                        <span className={`status-pill status-${apt.status}`}>{apt.status}</span>
                      </div>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        Requested {new Date(apt.created_at).toLocaleDateString()}
                      </span>
                    </div>

                    <div className="request-details-grid">
                      {apt.doctor_name && (
                        <div className="request-detail-item">
                          <span className="request-detail-label">Doctor</span>
                          <span className="request-detail-val" style={{ fontWeight: 600 }}>{apt.doctor_name}</span>
                        </div>
                      )}
                      <div className="request-detail-item">
                        <span className="request-detail-label">Family Member</span>
                        <span className="request-detail-val">{apt.member_name || `Member #${apt.member_id}`}</span>
                      </div>
                      <div className="request-detail-item">
                        <span className="request-detail-label">Preferred Date & Time</span>
                        <span className="request-detail-val">
                          {new Date(apt.preferred_at).toLocaleString([], {
                            dateStyle: 'medium',
                            timeStyle: 'short',
                          })}
                        </span>
                      </div>
                      {apt.scheduled_at && (
                        <div className="request-detail-item">
                          <span className="request-detail-label">Scheduled Date & Time</span>
                          <span className="request-detail-val" style={{ color: 'var(--emerald)', fontWeight: 600 }}>
                            {new Date(apt.scheduled_at).toLocaleString([], {
                              dateStyle: 'medium',
                              timeStyle: 'short',
                            })}
                          </span>
                        </div>
                      )}
                      {apt.reason && (
                        <div className="request-detail-item">
                          <span className="request-detail-label">Reason</span>
                          <span className="request-detail-val">{apt.reason}</span>
                        </div>
                      )}
                    </div>

                    {apt.patient_note && (
                      <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                        <strong>Patient Note: </strong> {apt.patient_note}
                      </div>
                    )}

                    {/* Display doctor response or reason for rejection/cancellation if API provides it */}
                    {apt.doctor_response && (
                      <div className="request-note-box">
                        <strong>Doctor Response / Decision Note: </strong> {apt.doctor_response}
                      </div>
                    )}

                    {/* Pending Reschedule Banner */}
                    {pendingReschedule && (
                      <div className="reschedule-banner-box">
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                          <Clock size={16} color="var(--warning)" />
                          <span>
                            {isMyRescheduleProposal
                              ? 'Rescheduling Request Pending Doctor Decision'
                              : 'Doctor Proposed a New Appointment Time'}
                          </span>
                        </div>
                        <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.35rem' }}>
                          <strong>Proposed Time: </strong>
                          {new Date(pendingReschedule.proposed_at).toLocaleString([], {
                            dateStyle: 'medium',
                            timeStyle: 'short',
                          })}
                          {pendingReschedule.reason && (
                            <span> • <em>Reason: {pendingReschedule.reason}</em></span>
                          )}
                        </div>
                        {!isMyRescheduleProposal && (
                          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.65rem' }}>
                            <Button
                              type="button"
                              variant="primary"
                              size="sm"
                              disabled={decidingRescheduleId === pendingReschedule.id}
                              onClick={() => handleRescheduleDecision(pendingReschedule.id, 'accept')}
                            >
                              {decidingRescheduleId === pendingReschedule.id ? 'Accepting...' : 'Accept New Time'}
                            </Button>
                            <Button
                              type="button"
                              variant="danger"
                              size="sm"
                              disabled={decidingRescheduleId === pendingReschedule.id}
                              onClick={() => handleRescheduleDecision(pendingReschedule.id, 'reject')}
                            >
                              {decidingRescheduleId === pendingReschedule.id ? 'Declining...' : 'Decline'}
                            </Button>
                          </div>
                        )}
                      </div>
                    )}

                    <div className="request-item-actions">
                      <Button
                        type="button"
                        variant="secondary"
                        size="sm"
                        onClick={() => setActiveNoteAppointment(apt)}
                      >
                        <FileText size={15} /> View Consultation Notes
                      </Button>

                      {canReschedule && (
                        <Button
                          type="button"
                          variant="secondary"
                          size="sm"
                          onClick={() => handleOpenReschedule(apt)}
                          title="Propose a new appointment time"
                        >
                          <Clock size={15} /> Reschedule
                        </Button>
                      )}

                      {canCancel && (
                        <Button
                          type="button"
                          variant="danger"
                          size="sm"
                          onClick={() => handleCancelAppointment(apt.id)}
                        >
                          <Ban size={15} /> Cancel Appointment
                        </Button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* TAB 3: ONLINE CONSULTATIONS */}
      {activeTab === 'chats' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {loadingChats ? (
            <Spinner />
          ) : chatRequests.length === 0 ? (
            <div className="doctor-empty-state">
              <MessageSquare size={48} />
              <h3>No online chat consultations</h3>
              <p>Request an online consultation from the doctor directory to begin text messaging.</p>
              <Button variant="primary" size="md" onClick={() => setActiveTab('directory')}>
                Find a Doctor
              </Button>
            </div>
          ) : (
            <div className="requests-list">
              {chatRequests.map((chat) => {
                const canCancel = chat.status === 'requested' || chat.status === 'accepted';
                return (
                  <div key={chat.id} className="request-item-card">
                    <div className="request-item-header">
                      <div className="request-item-title">
                        <MessageSquare size={18} color="var(--red-primary)" />
                        <span>Consultation #{chat.id}</span>
                        <span className={`status-pill status-${chat.status}`}>{chat.status}</span>
                      </div>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        Created {new Date(chat.created_at).toLocaleDateString()}
                      </span>
                    </div>

                    <div className="request-details-grid">
                      <div className="request-detail-item">
                        <span className="request-detail-label">Family Member</span>
                        <span className="request-detail-val">{chat.member_name || `Member #${chat.member_id}`}</span>
                      </div>
                      <div className="request-detail-item">
                        <span className="request-detail-label">Initial Query</span>
                        <span className="request-detail-val">{chat.message || 'General Consultation'}</span>
                      </div>
                    </div>

                    <div className="request-item-actions">
                      <Button
                        type="button"
                        variant={chat.status === 'accepted' ? 'primary' : 'secondary'}
                        size="sm"
                        onClick={() => setActiveChatRequest(chat)}
                      >
                        <MessageSquare size={15} /> {chat.status === 'accepted' ? 'Open Chat Messages' : 'View Consultation'}
                      </Button>

                      {canCancel && (
                        <Button
                          type="button"
                          variant="danger"
                          size="sm"
                          onClick={() => handleCancelChat(chat.id)}
                        >
                          <Ban size={15} /> Cancel Request
                        </Button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* TAB 4: RECORD SHARING CONSENT */}
      {activeTab === 'consent' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              Control medical data permissions granted to consulting practitioners. Doctors can only view health metrics and documents when active consent is maintained.
            </p>
            <Button variant="primary" size="sm" onClick={() => setGrantModalOpen(true)}>
              <Plus size={15} /> Grant New Consent
            </Button>
          </div>

          {loadingGrants ? (
            <Spinner />
          ) : grants.length === 0 ? (
            <div className="doctor-empty-state">
              <ShieldCheck size={48} />
              <h3>No record sharing grants</h3>
              <p>You have not shared any family member records with doctors yet.</p>
            </div>
          ) : (
            <div className="consent-table-container">
              <table className="consent-table">
                <thead>
                  <tr>
                    <th>Family Member</th>
                    <th>Doctor Contact</th>
                    <th>Permissions Granted</th>
                    <th>Status</th>
                    <th>Granted Date</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {grants.map((grant) => (
                    <tr key={grant.id}>
                      <td>
                        <strong>{grant.member_name || `Member #${grant.member_id}`}</strong>
                      </td>
                      <td>{grant.doctor_email || `Doctor #${grant.doctor_id}`}</td>
                      <td>
                        <div className="scope-chips">
                          {(grant.scopes || []).map((s) => (
                            <span key={s} className="scope-chip">
                              {s}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td>
                        <span className={`status-pill ${grant.active ? 'status-active' : 'status-revoked'}`}>
                          {grant.active ? 'Active' : 'Revoked'}
                        </span>
                      </td>
                      <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        {new Date(grant.granted_at).toLocaleDateString()}
                      </td>
                      <td>
                        {grant.active && (
                          <Button
                            type="button"
                            variant="danger"
                            size="sm"
                            onClick={() => handleRevokeConsent(grant.id)}
                          >
                            Revoke Access
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

      {/* BOOK APPOINTMENT MODAL */}
      {bookingDoctor && (
        <Modal
          title={`Book Appointment with ${bookingDoctor.name}`}
          subtitle={`${bookingDoctor.specialty} • ${bookingDoctor.qualifications}`}
          onClose={() => {
            setBookingDoctor(null);
            setBookingModalError('');
          }}
          wide={true}
        >
          {bookingModalError && <Banner variant="error">{bookingModalError}</Banner>}
          <form onSubmit={handleBookAppointment} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="doctor-form-grid">
              <div className="doctor-form-group">
                <label htmlFor="booking-member">Consulting Family Member *</label>
                <select
                  id="booking-member"
                  className="doctor-form-select"
                  value={bookingForm.member_key}
                  onChange={(e) => setBookingForm({ ...bookingForm, member_key: e.target.value })}
                  required
                >
                  {Object.entries(members).map(([key, m]) => (
                    <option key={key} value={key}>
                      {m.firstName} {m.lastName} ({key})
                    </option>
                  ))}
                </select>
              </div>

              <div className="doctor-form-group">
                <label htmlFor="booking-date">Preferred Date & Time *</label>
                <input
                  id="booking-date"
                  type="datetime-local"
                  className="doctor-form-input"
                  required
                  value={bookingForm.preferred_at}
                  onChange={(e) => {
                    setBookingForm({ ...bookingForm, preferred_at: e.target.value });
                    setBookingModalError('');
                  }}
                />
              </div>

              {/* Doctor Availability Slots */}
              <div className="doctor-form-group doctor-form-full">
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 600 }}>
                  <Clock size={15} color="var(--red-primary)" />
                  Doctor Weekly Availability
                </label>
                {loadingAvailability ? (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 0', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                    <Spinner size={16} /> Checking doctor bookable availability...
                  </div>
                ) : availabilityError ? (
                  <div style={{ fontSize: '0.85rem', color: 'var(--danger)', padding: '0.4rem 0' }}>
                    {availabilityError}
                  </div>
                ) : doctorAvailability?.has_configured_slots === false ? (
                  <div className="availability-notice info">
                    <Clock size={15} />
                    <span>Open Scheduling: Doctor accepts appointments across standard hours. Select any future date and time.</span>
                  </div>
                ) : doctorAvailability?.slots?.length === 0 ? (
                  <div className="availability-notice warning">
                    <AlertCircle size={16} />
                    <span>This doctor currently has no active weekly availability slots configured. Booking is unavailable.</span>
                  </div>
                ) : (
                  <div>
                    <p style={{ margin: '0 0 0.45rem 0', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      Click an active weekly slot to set the next available date & time:
                    </p>
                    <div className="availability-chips-list">
                      {(doctorAvailability?.slots || []).map((slot) => {
                        const dayName = WEEKDAY_NAMES[slot.weekday] || `Day ${slot.weekday}`;
                        return (
                          <button
                            key={slot.id}
                            type="button"
                            className="availability-slot-btn"
                            title={`Select next ${dayName} at ${slot.start_time}`}
                            onClick={() => {
                              const nextDt = getNextDateForWeekdayTime(slot.weekday, slot.start_time);
                              setBookingForm((prev) => ({ ...prev, preferred_at: nextDt }));
                              setBookingModalError('');
                            }}
                          >
                            <Calendar size={13} />
                            <strong>{dayName}</strong>
                            <span>{slot.start_time} – {slot.end_time}</span>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>

              <div className="doctor-form-group doctor-form-full">
                <label htmlFor="booking-reason">Reason for Consultation *</label>
                <input
                  id="booking-reason"
                  type="text"
                  className="doctor-form-input"
                  placeholder="e.g. Routine consultation, Blood pressure checkup, Prescription renewal"
                  required
                  maxLength={1000}
                  value={bookingForm.reason}
                  onChange={(e) => setBookingForm({ ...bookingForm, reason: e.target.value })}
                />
              </div>

              <div className="doctor-form-group doctor-form-full">
                <label htmlFor="booking-note">Additional Details / Symptoms</label>
                <textarea
                  id="booking-note"
                  rows={3}
                  className="doctor-form-textarea"
                  placeholder="Describe your current symptoms or relevant medical questions..."
                  maxLength={2000}
                  value={bookingForm.patient_note}
                  onChange={(e) => setBookingForm({ ...bookingForm, patient_note: e.target.value })}
                />
              </div>

              <div className="doctor-form-group doctor-form-full">
                <label>Medical Record Sharing Permissions *</label>
                <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  The doctor requires profile access to review vitals. Select additional permissions to share:
                </p>
                <div className="checkbox-group">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={bookingForm.consent_scopes.includes('profile')}
                      disabled={true}
                    />
                    <span>Profile & Vital Metrics (Required for consultation)</span>
                  </label>
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={bookingForm.consent_scopes.includes('documents')}
                      onChange={(e) => {
                        const next = e.target.checked
                          ? [...bookingForm.consent_scopes, 'documents']
                          : bookingForm.consent_scopes.filter((s) => s !== 'documents');
                        setBookingForm({ ...bookingForm, consent_scopes: next });
                      }}
                    />
                    <span>Scanned Lab Results & Prescriptions</span>
                  </label>
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={bookingForm.consent_scopes.includes('consultation_notes')}
                      onChange={(e) => {
                        const next = e.target.checked
                          ? [...bookingForm.consent_scopes, 'consultation_notes']
                          : bookingForm.consent_scopes.filter((s) => s !== 'consultation_notes');
                        setBookingForm({ ...bookingForm, consent_scopes: next });
                      }}
                    />
                    <span>Allow Doctor to Record & Share Consultation Notes</span>
                  </label>
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
              <Button
                type="button"
                variant="secondary"
                disabled={submittingBooking}
                onClick={() => {
                  setBookingDoctor(null);
                  setBookingModalError('');
                }}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                disabled={
                  submittingBooking ||
                  (doctorAvailability?.has_configured_slots &&
                    doctorAvailability?.slots?.length === 0)
                }
              >
                {submittingBooking
                  ? 'Sending Request...'
                  : doctorAvailability?.has_configured_slots &&
                    doctorAvailability?.slots?.length === 0
                  ? 'No Slots Available'
                  : 'Send Appointment Request'}
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* RESCHEDULE APPOINTMENT MODAL */}
      {rescheduleModalApt && (
        <Modal
          title={`Reschedule Appointment #${rescheduleModalApt.id}`}
          subtitle={`Doctor: ${rescheduleModalApt.doctor_name || 'Assigned Doctor'} | Current: ${new Date(rescheduleModalApt.scheduled_at || rescheduleModalApt.preferred_at).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })}`}
          onClose={() => {
            setRescheduleModalApt(null);
            setRescheduleModalError('');
          }}
          wide={true}
        >
          {rescheduleModalError && <Banner variant="error">{rescheduleModalError}</Banner>}
          <form onSubmit={handleRequestReschedule} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="doctor-form-grid">
              <div className="doctor-form-group doctor-form-full">
                <label htmlFor="reschedule-date">Proposed New Date & Time *</label>
                <input
                  id="reschedule-date"
                  type="datetime-local"
                  className="doctor-form-input"
                  required
                  value={rescheduleForm.proposed_at}
                  onChange={(e) => {
                    setRescheduleForm({ ...rescheduleForm, proposed_at: e.target.value });
                    setRescheduleModalError('');
                  }}
                />
              </div>

              {/* Doctor Availability for Rescheduling */}
              <div className="doctor-form-group doctor-form-full">
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 600 }}>
                  <Clock size={15} color="var(--red-primary)" />
                  Doctor Weekly Availability
                </label>
                {loadingRescheduleAvailability ? (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 0', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                    <Spinner size={16} /> Checking doctor schedule...
                  </div>
                ) : rescheduleDoctorAvailability?.has_configured_slots === false ? (
                  <div className="availability-notice info">
                    <Clock size={15} />
                    <span>Open Scheduling: Select any future time during standard operating hours.</span>
                  </div>
                ) : rescheduleDoctorAvailability?.slots?.length === 0 ? (
                  <div className="availability-notice warning">
                    <AlertCircle size={16} />
                    <span>This doctor currently has no active weekly availability slots configured.</span>
                  </div>
                ) : (
                  <div>
                    <p style={{ margin: '0 0 0.45rem 0', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      Select a time within the doctor's active weekly slots:
                    </p>
                    <div className="availability-chips-list">
                      {(rescheduleDoctorAvailability?.slots || []).map((slot) => {
                        const dayName = WEEKDAY_NAMES[slot.weekday] || `Day ${slot.weekday}`;
                        return (
                          <button
                            key={slot.id}
                            type="button"
                            className="availability-slot-btn"
                            title={`Select next ${dayName} at ${slot.start_time}`}
                            onClick={() => {
                              const nextDt = getNextDateForWeekdayTime(slot.weekday, slot.start_time);
                              setRescheduleForm((prev) => ({ ...prev, proposed_at: nextDt }));
                              setRescheduleModalError('');
                            }}
                          >
                            <Calendar size={13} />
                            <strong>{dayName}</strong>
                            <span>{slot.start_time} – {slot.end_time}</span>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>

              <div className="doctor-form-group doctor-form-full">
                <label htmlFor="reschedule-reason">Reason for Rescheduling</label>
                <input
                  id="reschedule-reason"
                  type="text"
                  className="doctor-form-input"
                  placeholder="e.g. Schedule conflict, family commitment, unwell"
                  maxLength={1000}
                  value={rescheduleForm.reason}
                  onChange={(e) => setRescheduleForm({ ...rescheduleForm, reason: e.target.value })}
                />
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
              <Button
                type="button"
                variant="secondary"
                disabled={submittingReschedule}
                onClick={() => {
                  setRescheduleModalApt(null);
                  setRescheduleModalError('');
                }}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                disabled={
                  submittingReschedule ||
                  (rescheduleDoctorAvailability?.has_configured_slots &&
                    rescheduleDoctorAvailability?.slots?.length === 0)
                }
              >
                {submittingReschedule ? 'Submitting...' : 'Submit Reschedule Request'}
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* REQUEST CHAT MODAL */}
      {chatTargetDoctor && (
        <Modal
          title={`Request Online Consultation with ${chatTargetDoctor.name}`}
          subtitle={`${chatTargetDoctor.specialty} • Direct messaging once accepted`}
          onClose={() => {
            setChatTargetDoctor(null);
            setChatModalError('');
          }}
          wide={true}
        >
          {chatModalError && <Banner variant="error">{chatModalError}</Banner>}
          <form onSubmit={handleRequestChat} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="doctor-form-group">
              <label htmlFor="chat-member">Consulting Family Member *</label>
              <select
                id="chat-member"
                className="doctor-form-select"
                value={chatForm.member_key}
                onChange={(e) => setChatForm({ ...chatForm, member_key: e.target.value })}
                required
              >
                {Object.entries(members).map(([key, m]) => (
                  <option key={key} value={key}>
                    {m.firstName} {m.lastName} ({key})
                  </option>
                ))}
              </select>
            </div>

            <div className="doctor-form-group">
              <label htmlFor="chat-message">Initial Consultation Inquiry *</label>
              <textarea
                id="chat-message"
                rows={4}
                className="doctor-form-textarea"
                placeholder="State your medical question or reason for requesting this online consultation..."
                required
                maxLength={1000}
                value={chatForm.message}
                onChange={(e) => setChatForm({ ...chatForm, message: e.target.value })}
              />
            </div>

            <div className="doctor-form-group">
              <label>Record Sharing Permissions</label>
              <div className="checkbox-group">
                <label className="checkbox-label">
                  <input type="checkbox" checked={chatForm.consent_scopes.includes('profile')} disabled={true} />
                  <span>Profile & Health Vitals (Required)</span>
                </label>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={chatForm.consent_scopes.includes('documents')}
                    onChange={(e) => {
                      const next = e.target.checked
                        ? [...chatForm.consent_scopes, 'documents']
                        : chatForm.consent_scopes.filter((s) => s !== 'documents');
                      setChatForm({ ...chatForm, consent_scopes: next });
                    }}
                  />
                  <span>Allow doctor to view scanned medical documents</span>
                </label>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
              <Button
                type="button"
                variant="secondary"
                disabled={submittingChat}
                onClick={() => {
                  setChatTargetDoctor(null);
                  setChatModalError('');
                }}
              >
                Cancel
              </Button>
              <Button type="submit" variant="primary" disabled={submittingChat}>
                {submittingChat ? 'Sending Request...' : 'Send Consultation Request'}
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* GRANT CONSENT MODAL */}
      {grantModalOpen && (
        <Modal
          title="Grant Medical Record Access Consent"
          subtitle="Authorize a doctor to view specific medical records for a family member"
          onClose={() => setGrantModalOpen(false)}
          wide={true}
        >
          <form onSubmit={handleGrantConsent} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="doctor-form-grid">
              <div className="doctor-form-group">
                <label htmlFor="grant-member">Family Member *</label>
                <select
                  id="grant-member"
                  className="doctor-form-select"
                  value={consentForm.member_key}
                  onChange={(e) => setConsentForm({ ...consentForm, member_key: e.target.value })}
                  required
                >
                  {Object.entries(members).map(([key, m]) => (
                    <option key={key} value={key}>
                      {m.firstName} {m.lastName} ({key})
                    </option>
                  ))}
                </select>
              </div>

              <div className="doctor-form-group">
                <label htmlFor="grant-doctor">Select Approved Doctor *</label>
                <select
                  id="grant-doctor"
                  className="doctor-form-select"
                  value={consentForm.doctor_id}
                  onChange={(e) => setConsentForm({ ...consentForm, doctor_id: e.target.value })}
                  required
                >
                  <option value="">-- Choose verified doctor --</option>
                  {doctors.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.name} ({d.specialty})
                    </option>
                  ))}
                </select>
              </div>

              <div className="doctor-form-group doctor-form-full">
                <label>Permissions (Scopes) *</label>
                <div className="checkbox-group">
                  <label className="checkbox-label">
                    <input type="checkbox" checked={consentForm.scopes.includes('profile')} disabled={true} />
                    <span>profile — Vitals, height, weight, BP, HbA1c, medications (Mandatory)</span>
                  </label>
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={consentForm.scopes.includes('documents')}
                      onChange={(e) => {
                        const next = e.target.checked
                          ? [...consentForm.scopes, 'documents']
                          : consentForm.scopes.filter((s) => s !== 'documents');
                        setConsentForm({ ...consentForm, scopes: next });
                      }}
                    />
                    <span>documents — Scanned prescriptions, lab reports, discharge summaries</span>
                  </label>
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={consentForm.scopes.includes('consultation_notes')}
                      onChange={(e) => {
                        const next = e.target.checked
                          ? [...consentForm.scopes, 'consultation_notes']
                          : consentForm.scopes.filter((s) => s !== 'consultation_notes');
                        setConsentForm({ ...consentForm, scopes: next });
                      }}
                    />
                    <span>consultation_notes — Clinical notes from consultations</span>
                  </label>
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
              <Button type="button" variant="secondary" onClick={() => setGrantModalOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" variant="primary">
                Grant Consent
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* ACTIVE CHAT MODAL */}
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
          isDoctor={false}
          onClose={() => setActiveNoteAppointment(null)}
        />
      )}
    </div>
  );
}
