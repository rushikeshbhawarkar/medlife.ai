import { useState, useEffect, useCallback } from 'react';
import Modal from '../../components/Modal/index.js';
import Button from '../../components/Button/index.js';
import Spinner from '../../components/Spinner/index.js';
import Banner from '../../components/Banner/index.js';
import { getMyDoctorApplication, submitDoctorApplication } from '../../services/api.js';

export default function DoctorApplicationModal({ onClose, onApplied }) {
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [existingApp, setExistingApp] = useState(null);
  const [doctorProfile, setDoctorProfile] = useState(null);

  const [form, setForm] = useState({
    full_name: '',
    specialty: '',
    qualifications: '',
    registration_number: '',
    clinic_name: '',
    bio: '',
    years_experience: 0,
  });

  const loadMyApplication = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      const data = await getMyDoctorApplication();
      setExistingApp(data?.application || null);
      setDoctorProfile(data?.doctor_profile || null);
    } catch (e) {
      setError(e.message || 'Unable to check application status.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadMyApplication();
  }, [loadMyApplication]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      await submitDoctorApplication({
        ...form,
        years_experience: Number(form.years_experience) || 0,
      });
      await loadMyApplication();
      if (onApplied) onApplied();
    } catch (e) {
      setError(e.message || 'Unable to submit doctor application.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      title="Doctor Verification & Application"
      subtitle="Join the MedLife Medical Network as a Verified Healthcare Practitioner"
      onClose={onClose}
      wide={true}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {error && <Banner variant="error">{error}</Banner>}

        {loading ? (
          <Spinner />
        ) : existingApp ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div
              style={{
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '12px',
                padding: '1.25rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.75rem',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ margin: 0, color: 'var(--text-primary)', fontSize: '1.1rem' }}>
                  Application #{existingApp.id}
                </h3>
                <span className={`status-pill status-${existingApp.status}`}>
                  {existingApp.status}
                </span>
              </div>

              <div className="request-details-grid">
                <div className="request-detail-item">
                  <span className="request-detail-label">Applicant Name</span>
                  <span className="request-detail-val">{existingApp.full_name}</span>
                </div>
                <div className="request-detail-item">
                  <span className="request-detail-label">Specialty</span>
                  <span className="request-detail-val">{existingApp.specialty}</span>
                </div>
                <div className="request-detail-item">
                  <span className="request-detail-label">Registration No.</span>
                  <span className="request-detail-val">{existingApp.registration_number}</span>
                </div>
                <div className="request-detail-item">
                  <span className="request-detail-label">Experience</span>
                  <span className="request-detail-val">{existingApp.years_experience} years</span>
                </div>
              </div>

              {existingApp.review_note && (
                <div className="request-note-box">
                  <strong>Reviewer Feedback: </strong> {existingApp.review_note}
                </div>
              )}

              {existingApp.status === 'pending' && (
                <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', margin: 0 }}>
                  Your application is currently under review by MedLife Medical Administration. You will be notified once reviewed.
                </p>
              )}

              {existingApp.status === 'approved' && (
                <p style={{ color: 'var(--emerald)', fontSize: '0.875rem', margin: 0 }}>
                  Congratulations! Your doctor profile has been verified and approved. You now have access to the Doctor Workspace.
                </p>
              )}
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button type="button" variant="secondary" onClick={onClose}>
                Close
              </Button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="doctor-form-grid">
              <div className="doctor-form-group">
                <label htmlFor="doc-full-name">Full Name (with title) *</label>
                <input
                  id="doc-full-name"
                  type="text"
                  className="doctor-form-input"
                  placeholder="e.g. Dr. Jane Smith"
                  required
                  maxLength={150}
                  value={form.full_name}
                  onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                  disabled={submitting}
                />
              </div>

              <div className="doctor-form-group">
                <label htmlFor="doc-specialty">Primary Specialty *</label>
                <input
                  id="doc-specialty"
                  type="text"
                  className="doctor-form-input"
                  placeholder="e.g. Cardiology, General Medicine"
                  required
                  maxLength={120}
                  value={form.specialty}
                  onChange={(e) => setForm({ ...form, specialty: e.target.value })}
                  disabled={submitting}
                />
              </div>

              <div className="doctor-form-group">
                <label htmlFor="doc-qualifications">Qualifications *</label>
                <input
                  id="doc-qualifications"
                  type="text"
                  className="doctor-form-input"
                  placeholder="e.g. MBBS, MD, FRCP"
                  required
                  maxLength={255}
                  value={form.qualifications}
                  onChange={(e) => setForm({ ...form, qualifications: e.target.value })}
                  disabled={submitting}
                />
              </div>

              <div className="doctor-form-group">
                <label htmlFor="doc-reg-number">Medical Registration Number *</label>
                <input
                  id="doc-reg-number"
                  type="text"
                  className="doctor-form-input"
                  placeholder="Official medical council ID"
                  required
                  maxLength={120}
                  value={form.registration_number}
                  onChange={(e) => setForm({ ...form, registration_number: e.target.value })}
                  disabled={submitting}
                />
              </div>

              <div className="doctor-form-group">
                <label htmlFor="doc-clinic-name">Clinic / Hospital Affiliation</label>
                <input
                  id="doc-clinic-name"
                  type="text"
                  className="doctor-form-input"
                  placeholder="e.g. Apollo Hospital or Private Clinic"
                  maxLength={200}
                  value={form.clinic_name}
                  onChange={(e) => setForm({ ...form, clinic_name: e.target.value })}
                  disabled={submitting}
                />
              </div>

              <div className="doctor-form-group">
                <label htmlFor="doc-years-exp">Years of Experience</label>
                <input
                  id="doc-years-exp"
                  type="number"
                  min="0"
                  max="80"
                  className="doctor-form-input"
                  placeholder="0"
                  value={form.years_experience}
                  onChange={(e) => setForm({ ...form, years_experience: e.target.value })}
                  disabled={submitting}
                />
              </div>

              <div className="doctor-form-group doctor-form-full">
                <label htmlFor="doc-bio">Professional Bio & Clinical Focus</label>
                <textarea
                  id="doc-bio"
                  rows={4}
                  className="doctor-form-textarea"
                  placeholder="Summary of experience, clinical interests, consultation methodology..."
                  maxLength={5000}
                  value={form.bio}
                  onChange={(e) => setForm({ ...form, bio: e.target.value })}
                  disabled={submitting}
                />
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
              <Button type="button" variant="secondary" onClick={onClose} disabled={submitting}>
                Cancel
              </Button>
              <Button type="submit" variant="primary" disabled={submitting}>
                {submitting ? 'Submitting Application...' : 'Submit Application'}
              </Button>
            </div>
          </form>
        )}
      </div>
    </Modal>
  );
}
