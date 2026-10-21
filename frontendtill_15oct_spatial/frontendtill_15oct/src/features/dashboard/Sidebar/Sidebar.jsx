import { useState } from 'react';
import {
  Users,
  Plus,
  LogOut,
  X,
  KeyRound,
  Stethoscope,
  BriefcaseMedical,
  ShieldAlert,
  Mail,
  Calendar,
  MessageSquare,
  Clock,
} from 'lucide-react';
import Logo from '../../../components/Logo/index.js';
import Button from '../../../components/Button/index.js';
import Avatar from '../../../components/Avatar/index.js';
import { fullName } from '../../../utils/person.js';
import { MAX_MEMBERS } from '../../../data/siteConfig.js';
import ChangePasswordModal from '../../auth/ChangePasswordModal/index.js';
import './Sidebar.css';

export default function Sidebar({
  email,
  userRole = 'patient',
  members = {},
  selected,
  onSelect,
  onAdd,
  onSignOut,
  open,
  onClose,
  currentView = 'health',
  onSelectView,
  adminTab = 'applications',
  onSelectAdminTab,
  doctorTab = 'requests',
  onSelectDoctorTab,
  hasDoctorProfile = false,
  isStaff = false,
  applicationStatus = null,
  onOpenDoctorApp,
}) {
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const entries = Object.entries(members || {});

  return (
    <>
      <div className={`sidebar-scrim ${open ? 'scrim-visible' : ''}`} onClick={onClose} />
      <aside className={`dashboard-sidebar ${open ? 'sidebar-open' : ''}`}>
        <div className="sidebar-top">
          <Logo light toHome={false} />
          <button className="sidebar-close" aria-label="Close sidebar" onClick={onClose}>
            <X />
          </button>
        </div>

        <div className="sidebar-role-indicator">
          <span className={`role-pill role-pill-${userRole}`}>
            {userRole === 'super_admin' ? 'Super Admin' : userRole === 'doctor' ? 'Doctor' : 'Patient'}
          </span>
        </div>

        {/* 1. SUPER ADMIN WORKSPACE */}
        {userRole === 'super_admin' ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '16px', flex: '1 1 auto' }}>
            <button
              type="button"
              className={`member-choice ${currentView === 'admin_portal' && adminTab === 'applications' ? 'member-selected' : ''}`}
              onClick={() => {
                if (onSelectAdminTab) onSelectAdminTab('applications');
                else if (onSelectView) onSelectView('admin_portal');
                if (open) onClose();
              }}
            >
              <ShieldAlert size={18} color="var(--warning)" />
              <span>
                <strong>Doctor Applications</strong>
                <small>Review & verification</small>
              </span>
            </button>

            <button
              type="button"
              className={`member-choice ${currentView === 'admin_portal' && adminTab === 'invitations' ? 'member-selected' : ''}`}
              onClick={() => {
                if (onSelectAdminTab) onSelectAdminTab('invitations');
                else if (onSelectView) onSelectView('admin_portal');
                if (open) onClose();
              }}
            >
              <Mail size={18} color="var(--red-primary)" />
              <span>
                <strong>Doctor Invitations</strong>
                <small>Onboarding invitations</small>
              </span>
            </button>
          </div>
        ) : userRole === 'doctor' ? (
          /* 2. DOCTOR WORKSPACE */
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '16px', flex: '1 1 auto' }}>
            <button
              type="button"
              className={`member-choice ${currentView === 'doctor_workspace' && doctorTab === 'requests' ? 'member-selected' : ''}`}
              onClick={() => {
                if (onSelectDoctorTab) onSelectDoctorTab('requests');
                else if (onSelectView) onSelectView('doctor_workspace');
                if (open) onClose();
              }}
            >
              <Clock size={18} color="var(--warning)" />
              <span>
                <strong>Appointment Requests</strong>
                <small>Patient bookings</small>
              </span>
            </button>

            <button
              type="button"
              className={`member-choice ${currentView === 'doctor_workspace' && doctorTab === 'upcoming' ? 'member-selected' : ''}`}
              onClick={() => {
                if (onSelectDoctorTab) onSelectDoctorTab('upcoming');
                else if (onSelectView) onSelectView('doctor_workspace');
                if (open) onClose();
              }}
            >
              <Calendar size={18} color="var(--emerald)" />
              <span>
                <strong>Upcoming Appointments</strong>
                <small>Sessions & clinical notes</small>
              </span>
            </button>

            <button
              type="button"
              className={`member-choice ${currentView === 'doctor_workspace' && doctorTab === 'chats' ? 'member-selected' : ''}`}
              onClick={() => {
                if (onSelectDoctorTab) onSelectDoctorTab('chats');
                else if (onSelectView) onSelectView('doctor_workspace');
                if (open) onClose();
              }}
            >
              <MessageSquare size={18} color="var(--red-primary)" />
              <span>
                <strong>Online Consultations</strong>
                <small>Live patient messaging</small>
              </span>
            </button>

            <button
              type="button"
              className={`member-choice ${currentView === 'doctor_workspace' && doctorTab === 'profile' ? 'member-selected' : ''}`}
              onClick={() => {
                if (onSelectDoctorTab) onSelectDoctorTab('profile');
                else if (onSelectView) onSelectView('doctor_workspace');
                if (open) onClose();
              }}
            >
              <BriefcaseMedical size={18} />
              <span>
                <strong>Doctor Profile</strong>
                <small>Schedule & fees</small>
              </span>
            </button>
          </div>
        ) : (
          /* 3. PATIENT WORKSPACE */
          <>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '16px' }}>
              <button
                type="button"
                className={`member-choice ${currentView === 'health' ? 'member-selected' : ''}`}
                onClick={() => {
                  if (onSelectView) onSelectView('health');
                  if (open) onClose();
                }}
              >
                <Users size={18} />
                <span>
                  <strong>Family Health</strong>
                  <small>Profiles & AI assistant</small>
                </span>
              </button>

              <button
                type="button"
                className={`member-choice ${currentView === 'consultation' ? 'member-selected' : ''}`}
                onClick={() => {
                  if (onSelectView) onSelectView('consultation');
                  if (open) onClose();
                }}
              >
                <Stethoscope size={18} color="var(--red-primary)" />
                <span>
                  <strong>Consult a Doctor</strong>
                  <small>Appointments & online chat</small>
                </span>
              </button>
            </div>

            {/* Family profiles section (strictly for patients) */}
            <div className="sidebar-label">
              <span><Users size={17} /> Family profiles</span>
              <b>{entries.length}/{MAX_MEMBERS}</b>
            </div>

            <div className="member-menu" style={{ flex: '1 1 auto', overflowY: 'auto', minHeight: '120px' }}>
              {entries.map(([key, m], i) => (
                <button
                  key={key}
                  className={`member-choice ${currentView === 'health' && selected === key ? 'member-selected' : ''}`}
                  onClick={() => {
                    onSelect(key);
                    if (onSelectView) onSelectView('health');
                    onClose();
                  }}
                >
                  <Avatar member={m} index={i} size={38} />
                  <span>
                    <strong>{fullName(m)}</strong>
                    <small>{m.tokens || 0} questions asked</small>
                  </span>
                </button>
              ))}
            </div>

            <Button variant="sidebar-add" block disabled={entries.length >= MAX_MEMBERS} onClick={onAdd}>
              <Plus size={18} />
              {entries.length >= MAX_MEMBERS ? 'Profile limit reached' : 'Add family member'}
            </Button>
          </>
        )}

        <div className="sidebar-account">
          <span className="account-initial">{email?.[0]?.toUpperCase() || '?'}</span>
          <span className="account-email" title={email}>{email}</span>
        </div>

        <button
          type="button"
          className="signout-btn security-btn"
          onClick={()=>{setShowPasswordModal(true);if(open)onClose();}}
        >
          <KeyRound size={17}/> Password & Security
        </button>

        <button className="signout-btn" onClick={onSignOut}>
          <LogOut size={17}/> Sign out
        </button>
      </aside>

      {showPasswordModal&&(
        <ChangePasswordModal
          email={email}
          onClose={()=>setShowPasswordModal(false)}
        />
      )}
    </>
  );
}