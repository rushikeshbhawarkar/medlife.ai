import { useState, useEffect } from 'react';
import Button from '../../components/Button/index.js';
import Banner from '../../components/Banner/index.js';
import Spinner from '../../components/Spinner/index.js';
import Logo from '../../components/Logo/index.js';
import { acceptDoctorInvitation, getAccessToken } from '../../services/api.js';
import { CheckCircle2, Stethoscope, AlertTriangle } from 'lucide-react';
import './doctor.css';

export default function DoctorInvitationPage({ email, onReturnToSignIn }) {
  const [token, setToken] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const [form, setForm] = useState({
    full_name: '',
    specialty: '',
    qualifications: '',
    registration_number: '',
    clinic_name: '',
    bio: '',
    years_experience: 0,
  });

  useEffect(() => {
    // Read token from URL hash (e.g. #token=... or #/doctor-invitation#token=...)
    const hash = window.location.hash || '';
    const tokenMatch = hash.match(/token=([^&]+)/);
    if (tokenMatch) {
      setToken(decodeURIComponent(tokenMatch[1]));
    }
  }, []);

  const tokenPresent = Boolean(token);
  const isAuthenticated = Boolean(getAccessToken() && email);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!tokenPresent) {
      setError('Invitation token is missing from the URL.');
      return;
    }
    setSubmitting(true);
    setError('');
    try {
      await acceptDoctorInvitation({
        token,
        ...form,
        years_experience: Number(form.years_experience) || 0,
      });
      setSuccess(true);
    } catch (err) {
      setError(err.message || 'Unable to accept doctor invitation.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleReturn = () => {
    window.location.hash = '#/';
    window.location.reload();
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
          maxWidth: '560px',
          background: 'var(--bg-card)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '16px',
          padding: '2rem',
          boxShadow: 'var(--shadow-lg)',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.25rem',
        }}
      >
        <div style={{ textAlign: 'center' }}>
          <Logo toHome={false} />
          <h2 style={{ marginTop: '1rem', color: 'var(--text-primary)', fontSize: '1.4rem' }}>
            Doctor Onboarding Invitation
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: '0.25rem 0 0 0' }}>
            Complete your practitioner credentials to verify your profile
          </p>
        </div>

        {error && <Banner variant="error">{error}</Banner>}

        {!tokenPresent && (
          <Banner variant="error">
            No invitation token found in the URL. Please verify the link from your invitation email.
          </Banner>
        )}

        {!isAuthenticated && tokenPresent && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', textAlign: 'center' }}>
            <Banner variant="info">
              You must sign in or register with the email address that received this invitation before submitting your credentials.
            </Banner>
            <Button
              type="button"
              variant="primary"
              size="lg"
              block
              onClick={() => {
                if (onReturnToSignIn) {
                  onReturnToSignIn();
                } else {
                  window.location.hash = '#/signin';
                }
              }}
            >
              Sign In to Continue
            </Button>
          </div>
        )}

        {isAuthenticated && tokenPresent && !success && (
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Authenticated as <strong>{email}</strong>
            </p>

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

            <Button type="submit" variant="primary" size="lg" block disabled={submitting}>
              {submitting ? 'Submitting Credentials...' : 'Accept Invitation & Apply'}
            </Button>
          </form>
        )}

        {success && (
          <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', gap: '1rem', alignItems: 'center' }}>
            <CheckCircle2 size={54} color="var(--emerald)" />
            <h3 style={{ margin: 0, color: 'var(--text-primary)' }}>Invitation Accepted!</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', margin: 0 }}>
              Your doctor application has been submitted and is currently awaiting verification by medical administration.
            </p>
            <Button type="button" variant="primary" size="lg" block onClick={handleReturn}>
              Return to MedLife Dashboard
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
