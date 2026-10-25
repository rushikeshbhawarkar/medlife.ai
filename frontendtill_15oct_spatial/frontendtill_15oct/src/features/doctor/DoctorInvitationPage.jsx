import { useState, useEffect } from 'react';
import Button from '../../components/Button/index.js';
import Banner from '../../components/Banner/index.js';
import Spinner from '../../components/Spinner/index.js';
import Logo from '../../components/Logo/index.js';
import { acceptDoctorInvitation } from '../../services/api.js';
import { CheckCircle2, Stethoscope, AlertTriangle, ArrowRight, XCircle } from 'lucide-react';
import './doctor.css';

function readInvitationToken() {
  const hash = window.location.hash || '';
  const search = new URLSearchParams(window.location.search);

  const queryToken = search.get('token');
  if (queryToken) return queryToken;

  const hashToken = hash.match(/(?:^#|&|\?|#\/doctor-invitation#)token=([^&]*)/);
  if (hashToken) {
    try {
      return decodeURIComponent(hashToken[1]);
    } catch {
      return hashToken[1];
    }
  }

  try {
    const decoded = decodeURIComponent(hash);
    const marker = '#token=';
    const idx = decoded.lastIndexOf(marker);
    if (idx !== -1) {
      return decoded.slice(idx + marker.length).split('&')[0];
    }
    const paramMarker = 'token=';
    const paramIdx = decoded.indexOf(paramMarker);
    if (paramIdx !== -1) {
      return decoded.slice(paramIdx + paramMarker.length).split('&')[0];
    }
  } catch {}

  return '';
}

export default function DoctorInvitationPage({ onReturnToSignIn }) {
  const [token, setToken] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [resultState, setResultState] = useState(null); // { type: 'accepted' | 'rejected', message: '', activationToken: '' }

  const [form, setForm] = useState({
    full_name: '',
    specialty: '',
    qualifications: '',
    registration_number: '',
    registration_authority: '',
    phone: '',
    address: '',
    clinic_name: '',
    bio: '',
    years_experience: 0,
  });

  useEffect(() => {
    const parsed = readInvitationToken();
    if (parsed) {
      setToken(parsed);
    } else {
      setError('Invitation token is missing from the link. Please verify the link in your invitation email.');
    }
  }, []);

  const tokenPresent = Boolean(token);

  // Handle Accept Invitation
  const handleAccept = async (e) => {
    e.preventDefault();
    if (!tokenPresent) {
      setError('Invitation token is missing from the URL.');
      return;
    }
    if (!form.full_name.trim() || !form.specialty.trim() || !form.qualifications.trim() || !form.registration_number.trim()) {
      setError('Full name, specialty, qualifications, and registration number are required.');
      return;
    }

    setSubmitting(true);
    setError('');
    try {
      const res = await acceptDoctorInvitation({
        token,
        decision: 'accept',
        full_name: form.full_name.trim(),
        specialty: form.specialty.trim(),
        qualifications: form.qualifications.trim(),
        registration_number: form.registration_number.trim(),
        registration_authority: form.registration_authority.trim(),
        phone: form.phone.trim(),
        address: form.address.trim(),
        clinic_name: form.clinic_name.trim(),
        bio: form.bio.trim(),
        years_experience: Number(form.years_experience) || 0,
      });

      setResultState({
        type: 'accepted',
        message: res?.message || 'Invitation accepted! Continue to set up your password and two-factor authenticator.',
        activationToken: res?.activation_token || '',
      });
    } catch (err) {
      setError(err.message || 'Unable to accept doctor invitation. The invitation may be expired or already used.');
    } finally {
      setSubmitting(false);
    }
  };

  // Handle Reject Invitation
  const handleReject = async () => {
    if (!window.confirm('Are you sure you want to decline this doctor invitation? This cannot be undone.')) {
      return;
    }
    setSubmitting(true);
    setError('');
    try {
      const res = await acceptDoctorInvitation({
        token,
        decision: 'reject',
      });
      setResultState({
        type: 'rejected',
        message: res?.message || 'Invitation rejected. No doctor account was created.',
      });
    } catch (err) {
      setError(err.message || 'Unable to reject invitation.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleProceedToActivation = () => {
    if (resultState?.activationToken) {
      window.location.hash = `#/doctor-activate#token=${resultState.activationToken}`;
      window.location.reload();
    } else {
      window.location.hash = '#/doctor-activate';
      window.location.reload();
    }
  };

  const handleReturnHome = () => {
    window.location.hash = '#/';
    if (onReturnToSignIn) onReturnToSignIn();
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'var(--bg-primary)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem 1rem',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '580px',
          background: 'var(--bg-card)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '16px',
          padding: '2.25rem 2rem',
          boxShadow: 'var(--shadow-lg)',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.25rem',
        }}
      >
        <div style={{ textAlign: 'center' }}>
          <Logo toHome={false} />
          <h2 style={{ marginTop: '1rem', color: 'var(--text-primary)', fontSize: '1.4rem', fontWeight: 700 }}>
            Doctor Onboarding Invitation
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: '0.25rem 0 0 0' }}>
            Complete your clinical practitioner credentials to accept your invitation
          </p>
        </div>

        {error && <Banner variant="error">{error}</Banner>}

        {!tokenPresent && (
          <Banner variant="error">
            No invitation token found in the URL. Please verify the link from your invitation email.
          </Banner>
        )}

        {/* ACCEPTED SUCCESS VIEW */}
        {resultState?.type === 'accepted' && (
          <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', gap: '1.25rem', alignItems: 'center', padding: '1rem 0' }}>
            <div
              style={{
                width: '56px',
                height: '56px',
                borderRadius: '50%',
                background: 'rgba(16, 185, 129, 0.12)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--emerald, #10b981)',
              }}
            >
              <CheckCircle2 size={36} />
            </div>
            <h3 style={{ margin: 0, color: 'var(--text-primary)', fontSize: '1.2rem' }}>
              Invitation Accepted!
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.925rem', margin: 0, lineHeight: 1.5 }}>
              {resultState.message}
            </p>
            <Button
              type="button"
              variant="primary"
              size="lg"
              block
              onClick={handleProceedToActivation}
            >
              Set Password & Activate Account <ArrowRight size={18} style={{ marginLeft: '6px' }} />
            </Button>
          </div>
        )}

        {/* REJECTED VIEW */}
        {resultState?.type === 'rejected' && (
          <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', gap: '1.25rem', alignItems: 'center', padding: '1rem 0' }}>
            <XCircle size={48} color="var(--text-muted)" />
            <h3 style={{ margin: 0, color: 'var(--text-primary)', fontSize: '1.2rem' }}>
              Invitation Declined
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.925rem', margin: 0 }}>
              {resultState.message}
            </p>
            <Button type="button" variant="secondary" size="lg" block onClick={handleReturnHome}>
              Return to MedLife Home
            </Button>
          </div>
        )}

        {/* ONBOARDING FORM */}
        {tokenPresent && !resultState && (
          <form onSubmit={handleAccept} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="doctor-form-grid">
              <div className="doctor-form-group">
                <label htmlFor="inv-full-name">Full Name (with Dr. title) *</label>
                <input
                  id="inv-full-name"
                  type="text"
                  className="doctor-form-input"
                  required
                  maxLength={150}
                  placeholder="Dr. Full Name"
                  value={form.full_name}
                  onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                  disabled={submitting}
                />
              </div>

              <div className="doctor-form-group">
                <label htmlFor="inv-specialty">Specialty *</label>
                <input
                  id="inv-specialty"
                  type="text"
                  className="doctor-form-input"
                  required
                  maxLength={120}
                  placeholder="e.g. Cardiology"
                  value={form.specialty}
                  onChange={(e) => setForm({ ...form, specialty: e.target.value })}
                  disabled={submitting}
                />
              </div>

              <div className="doctor-form-group">
                <label htmlFor="inv-qualifications">Qualifications *</label>
                <input
                  id="inv-qualifications"
                  type="text"
                  className="doctor-form-input"
                  required
                  maxLength={255}
                  placeholder="e.g. MBBS, MD"
                  value={form.qualifications}
                  onChange={(e) => setForm({ ...form, qualifications: e.target.value })}
                  disabled={submitting}
                />
              </div>

              <div className="doctor-form-group">
                <label htmlFor="inv-reg-number">Medical Registration No. *</label>
                <input
                  id="inv-reg-number"
                  type="text"
                  className="doctor-form-input"
                  required
                  maxLength={120}
                  placeholder="Medical Council Registration"
                  value={form.registration_number}
                  onChange={(e) => setForm({ ...form, registration_number: e.target.value })}
                  disabled={submitting}
                />
              </div>

              <div className="doctor-form-group">
                <label htmlFor="inv-reg-auth">Registration Authority</label>
                <input
                  id="inv-reg-auth"
                  type="text"
                  className="doctor-form-input"
                  maxLength={200}
                  placeholder="Medical Council / State Board"
                  value={form.registration_authority}
                  onChange={(e) => setForm({ ...form, registration_authority: e.target.value })}
                  disabled={submitting}
                />
              </div>

              <div className="doctor-form-group">
                <label htmlFor="inv-clinic">Clinic / Hospital Name</label>
                <input
                  id="inv-clinic"
                  type="text"
                  className="doctor-form-input"
                  maxLength={200}
                  placeholder="Affiliated Hospital or Clinic"
                  value={form.clinic_name}
                  onChange={(e) => setForm({ ...form, clinic_name: e.target.value })}
                  disabled={submitting}
                />
              </div>

              <div className="doctor-form-group">
                <label htmlFor="inv-phone">Contact Phone</label>
                <input
                  id="inv-phone"
                  type="tel"
                  className="doctor-form-input"
                  maxLength={32}
                  placeholder="Phone number"
                  value={form.phone}
                  onChange={(e) => setForm({ ...form, phone: e.target.value })}
                  disabled={submitting}
                />
              </div>

              <div className="doctor-form-group">
                <label htmlFor="inv-years">Years of Experience</label>
                <input
                  id="inv-years"
                  type="number"
                  min="0"
                  max="80"
                  className="doctor-form-input"
                  value={form.years_experience}
                  onChange={(e) => setForm({ ...form, years_experience: e.target.value })}
                  disabled={submitting}
                />
              </div>

              <div className="doctor-form-group doctor-form-full">
                <label htmlFor="inv-bio">Clinical Bio</label>
                <textarea
                  id="inv-bio"
                  rows={3}
                  className="doctor-form-textarea"
                  maxLength={5000}
                  placeholder="Summary of experience and background..."
                  value={form.bio}
                  onChange={(e) => setForm({ ...form, bio: e.target.value })}
                  disabled={submitting}
                />
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem' }}>
              <Button
                type="button"
                variant="danger"
                size="lg"
                onClick={handleReject}
                disabled={submitting}
                style={{ flex: 1 }}
              >
                Decline
              </Button>
              <Button
                type="submit"
                variant="primary"
                size="lg"
                disabled={submitting}
                style={{ flex: 2 }}
              >
                {submitting ? 'Submitting Credentials...' : 'Accept Invitation & Continue'}
              </Button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
