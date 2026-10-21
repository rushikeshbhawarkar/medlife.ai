import { useState, useRef } from 'react';
import Logo from '../../components/Logo/index.js';
import Button from '../../components/Button/index.js';
import Banner from '../../components/Banner/index.js';
import Spinner from '../../components/Spinner/index.js';
import { submitDoctorApplication } from '../../services/api.js';
import {
  Stethoscope,
  User,
  Phone,
  MapPin,
  GraduationCap,
  Award,
  Building2,
  FileText,
  Upload,
  Trash2,
  CheckCircle2,
  ShieldAlert,
  ArrowLeft,
  AlertTriangle,
} from 'lucide-react';
import './doctor.css';

const MAX_DOCUMENTS = 10;
const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024; // 10 MB
const ALLOWED_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png'];

export default function DoctorApplicationPage({ onReturnToSignIn }) {
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [submittedData, setSubmittedData] = useState(null);

  // Form Fields
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    phone: '',
    address: '',
    qualifications: '',
    specialty: '',
    years_experience: '',
    registration_number: '',
    registration_authority: '',
    clinic_name: '',
    bio: '',
  });

  // Supporting Documents: array of { id, file, document_type, error }
  const [documents, setDocuments] = useState([]);
  const [declarationChecked, setDeclarationChecked] = useState(false);
  const fileInputRef = useRef(null);

  const handleFieldChange = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleAddFiles = (e) => {
    const files = Array.from(e.target.files || []);
    if (!files.length) return;

    if (documents.length + files.length > MAX_DOCUMENTS) {
      setError(`You can upload at most ${MAX_DOCUMENTS} supporting documents.`);
      if (fileInputRef.current) fileInputRef.current.value = '';
      return;
    }

    setError('');
    const newDocs = [];
    for (const f of files) {
      const ext = f.name.includes('.') ? f.name.split('.').pop().toLowerCase() : '';
      let fileErr = '';
      if (!ALLOWED_EXTENSIONS.includes(ext)) {
        fileErr = 'Only PDF, JPG, JPEG, and PNG files are accepted.';
      } else if (f.size > MAX_FILE_SIZE_BYTES) {
        fileErr = 'Document must be 10 MB or smaller.';
      }
      newDocs.push({
        id: Math.random().toString(36).substring(2, 9),
        file: f,
        document_type: 'medical_registration',
        error: fileErr,
      });
    }

    setDocuments((prev) => [...prev, ...newDocs]);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleDocTypeChange = (id, type) => {
    setDocuments((prev) =>
      prev.map((doc) => (doc.id === id ? { ...doc, document_type: type } : doc))
    );
  };

  const handleRemoveDoc = (id) => {
    setDocuments((prev) => prev.filter((doc) => doc.id !== id));
  };

  const validateForm = () => {
    if (!form.full_name.trim()) return 'Full name is required.';
    if (form.full_name.trim().length > 150) return 'Full name must not exceed 150 characters.';

    if (!form.email.trim() || !form.email.includes('@')) {
      return 'A valid email address is required.';
    }
    if (form.email.trim().length > 254) return 'Email must not exceed 254 characters.';

    if (form.phone.trim().length > 32) return 'Phone must not exceed 32 characters.';
    if (form.address.trim().length > 3000) return 'Address must not exceed 3000 characters.';

    if (!form.qualifications.trim()) return 'Qualifications and degrees are required.';
    if (form.qualifications.trim().length > 255) return 'Qualifications must not exceed 255 characters.';

    if (!form.specialty.trim()) return 'Medical specialty is required.';
    if (form.specialty.trim().length > 120) return 'Specialty must not exceed 120 characters.';

    const years = Number(form.years_experience);
    if (isNaN(years) || years < 0 || years > 80) {
      return 'Years of clinical experience must be a number between 0 and 80.';
    }

    if (!form.registration_number.trim()) return 'Medical council registration number is required.';
    if (form.registration_number.trim().length > 120) {
      return 'Registration number must not exceed 120 characters.';
    }

    if (form.registration_authority.trim().length > 200) {
      return 'Registration authority must not exceed 200 characters.';
    }
    if (form.clinic_name.trim().length > 200) {
      return 'Clinic or hospital name must not exceed 200 characters.';
    }
    if (form.bio.trim().length > 5000) {
      return 'Bio must not exceed 5000 characters.';
    }

    for (const doc of documents) {
      if (doc.error) {
        return `Please resolve invalid document: ${doc.file.name} (${doc.error})`;
      }
    }

    if (!declarationChecked) {
      return 'Please confirm the declaration of accuracy before submitting.';
    }

    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }

    setError('');
    setSubmitting(true);

    try {
      const formData = new FormData();
      formData.append('full_name', form.full_name.trim());
      formData.append('email', form.email.trim().toLowerCase());
      formData.append('phone', form.phone.trim());
      formData.append('address', form.address.trim());
      formData.append('qualifications', form.qualifications.trim());
      formData.append('specialty', form.specialty.trim());
      formData.append('years_experience', String(Number(form.years_experience) || 0));
      formData.append('registration_number', form.registration_number.trim());
      formData.append('registration_authority', form.registration_authority.trim());
      formData.append('clinic_name', form.clinic_name.trim());
      formData.append('bio', form.bio.trim());

      documents.forEach((doc) => {
        formData.append('documents', doc.file);
        formData.append('document_types', doc.document_type);
      });

      const response = await submitDoctorApplication(formData);
      setSubmittedData(response?.application || {
        id: 'PENDING',
        full_name: form.full_name,
        email: form.email,
        specialty: form.specialty,
        status: 'pending',
      });
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      setError(err.message || 'Unable to submit doctor application. Please check all fields.');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } finally {
      setSubmitting(false);
    }
  };

  const navigateToHome = () => {
    window.location.hash = '#/';
  };

  const navigateToSignIn = () => {
    if (onReturnToSignIn) {
      onReturnToSignIn();
    } else {
      window.location.hash = '#/signin';
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'var(--bg-primary)',
        color: 'var(--text-primary)',
        padding: '2.5rem 1rem 4rem 1rem',
      }}
    >
      <div style={{ maxWidth: '820px', margin: '0 auto' }}>
        {/* Header Bar */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '2rem',
            flexWrap: 'wrap',
            gap: '1rem',
          }}
        >
          <Logo toHome={false} />
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            <Button variant="ghost" size="sm" onClick={navigateToHome}>
              <ArrowLeft size={16} /> MedLife Home
            </Button>
            <Button variant="secondary" size="sm" onClick={navigateToSignIn}>
              Sign In
            </Button>
          </div>
        </div>

        {/* Post-Submission Confirmation Screen */}
        {submittedData ? (
          <div
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '16px',
              padding: '2.5rem',
              boxShadow: 'var(--shadow-lg)',
              display: 'flex',
              flexDirection: 'column',
              gap: '1.5rem',
              textAlign: 'center',
              alignItems: 'center',
            }}
          >
            <div
              style={{
                width: '64px',
                height: '64px',
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

            <div>
              <h2 style={{ fontSize: '1.6rem', color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
                Doctor Application Submitted Successfully
              </h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', maxWidth: '560px', margin: '0 auto' }}>
                Your application has been logged and is currently awaiting verification and review by our Super Admin medical board.
              </p>
            </div>

            <div
              style={{
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '12px',
                padding: '1.25rem 1.75rem',
                width: '100%',
                maxWidth: '560px',
                textAlign: 'left',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.75rem',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                  Application Reference
                </span>
                <span className="status-pill status-pending">Pending Review</span>
              </div>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                Application #{submittedData.id}
              </div>
              <div style={{ height: '1px', background: 'var(--border-subtle)', margin: '0.25rem 0' }} />
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.9rem' }}>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Applicant:</span>{' '}
                  <strong>{submittedData.full_name}</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Specialty:</span>{' '}
                  <strong>{submittedData.specialty}</strong>
                </div>
                <div style={{ gridColumn: '1 / -1' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Contact Email:</span>{' '}
                  <strong>{submittedData.email}</strong>
                </div>
              </div>
            </div>

            <div
              style={{
                background: 'rgba(255, 26, 60, 0.05)',
                borderLeft: '4px solid var(--red-primary)',
                padding: '1rem 1.25rem',
                borderRadius: '0 8px 8px 0',
                fontSize: '0.875rem',
                color: 'var(--text-secondary)',
                maxWidth: '560px',
                textAlign: 'left',
              }}
            >
              <strong>Important Notice:</strong> Submitting this application creates an application record only.
              No doctor or patient account has been created. Upon review and approval by a Super Admin, an official
              Doctor ID and single-use secure password activation link will be delivered directly to{' '}
              <strong>{submittedData.email}</strong>.
            </div>

            <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem', flexWrap: 'wrap' }}>
              <Button variant="primary" size="lg" onClick={navigateToSignIn}>
                Return to Sign In
              </Button>
              <Button variant="secondary" size="lg" onClick={navigateToHome}>
                Back to MedLife Home
              </Button>
            </div>
          </div>
        ) : (
          /* Application Form */
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Title Card */}
            <div
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '16px',
                padding: '2rem',
                boxShadow: 'var(--shadow-sm)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                <div
                  style={{
                    background: 'rgba(255, 26, 60, 0.1)',
                    color: 'var(--red-primary)',
                    padding: '8px',
                    borderRadius: '10px',
                    display: 'flex',
                  }}
                >
                  <Stethoscope size={24} />
                </div>
                <div>
                  <h1 style={{ fontSize: '1.5rem', fontWeight: 700, margin: 0, color: 'var(--text-primary)' }}>
                    Apply to Become a Verified MedLife Doctor
                  </h1>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: '0.2rem 0 0 0' }}>
                    Accredited practitioner intake form. Evaluated independently by MedLife Medical Administration.
                  </p>
                </div>
              </div>

              <div
                style={{
                  background: 'var(--bg-secondary)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '8px',
                  padding: '0.75rem 1rem',
                  fontSize: '0.85rem',
                  color: 'var(--text-secondary)',
                  marginTop: '1rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                }}
              >
                <ShieldAlert size={18} color="var(--red-primary)" style={{ flexShrink: 0 }} />
                <span>
                  No sign-in is required to apply. An approved doctor account will only be created after review by our Super Admin.
                </span>
              </div>
            </div>

            {error && <Banner variant="error">{error}</Banner>}

            {/* SECTION 1: Personal & Contact Information */}
            <div
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '16px',
                padding: '1.75rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '1.25rem',
              }}
            >
              <h3 style={{ fontSize: '1.1rem', margin: 0, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <User size={18} color="var(--red-primary)" /> 1. Personal & Contact Details
              </h3>

              <div className="doctor-form-grid">
                <div className="doctor-form-group">
                  <label htmlFor="app-full-name">Full Legal & Professional Name *</label>
                  <input
                    id="app-full-name"
                    type="text"
                    className="doctor-form-input"
                    placeholder="e.g. Dr. Arthur Conan Doyle, MD"
                    required
                    maxLength={150}
                    value={form.full_name}
                    onChange={(e) => handleFieldChange('full_name', e.target.value)}
                    disabled={submitting}
                  />
                  <small style={{ color: 'var(--text-muted)' }}>As registered with your medical council</small>
                </div>

                <div className="doctor-form-group">
                  <label htmlFor="app-email">Official Email Address *</label>
                  <input
                    id="app-email"
                    type="email"
                    className="doctor-form-input"
                    placeholder="doctor@hospital.org"
                    required
                    maxLength={254}
                    value={form.email}
                    onChange={(e) => handleFieldChange('email', e.target.value)}
                    disabled={submitting}
                  />
                  <small style={{ color: 'var(--text-muted)' }}>Decision and activation link will be sent here</small>
                </div>

                <div className="doctor-form-group">
                  <label htmlFor="app-phone">Contact Phone Number</label>
                  <input
                    id="app-phone"
                    type="tel"
                    className="doctor-form-input"
                    placeholder="e.g. +1 555-0199"
                    maxLength={32}
                    value={form.phone}
                    onChange={(e) => handleFieldChange('phone', e.target.value)}
                    disabled={submitting}
                  />
                </div>

                <div className="doctor-form-group">
                  <label htmlFor="app-clinic">Clinic / Hospital Affiliation</label>
                  <input
                    id="app-clinic"
                    type="text"
                    className="doctor-form-input"
                    placeholder="e.g. St. Jude Memorial Hospital"
                    maxLength={200}
                    value={form.clinic_name}
                    onChange={(e) => handleFieldChange('clinic_name', e.target.value)}
                    disabled={submitting}
                  />
                </div>

                <div className="doctor-form-group doctor-form-full">
                  <label htmlFor="app-address">Clinic or Practice Address</label>
                  <input
                    id="app-address"
                    type="text"
                    className="doctor-form-input"
                    placeholder="Suite 400, 100 Healthcare Blvd, Metro City"
                    maxLength={3000}
                    value={form.address}
                    onChange={(e) => handleFieldChange('address', e.target.value)}
                    disabled={submitting}
                  />
                </div>
              </div>
            </div>

            {/* SECTION 2: Qualifications & Medical Council Registration */}
            <div
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '16px',
                padding: '1.75rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '1.25rem',
              }}
            >
              <h3 style={{ fontSize: '1.1rem', margin: 0, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Award size={18} color="var(--red-primary)" /> 2. Medical Credentials & Registration
              </h3>

              <div className="doctor-form-grid">
                <div className="doctor-form-group">
                  <label htmlFor="app-specialty">Primary Medical Specialty *</label>
                  <input
                    id="app-specialty"
                    type="text"
                    className="doctor-form-input"
                    placeholder="e.g. Cardiology, Pediatrics, General Practice"
                    required
                    maxLength={120}
                    value={form.specialty}
                    onChange={(e) => handleFieldChange('specialty', e.target.value)}
                    disabled={submitting}
                  />
                </div>

                <div className="doctor-form-group">
                  <label htmlFor="app-experience">Years of Clinical Experience *</label>
                  <input
                    id="app-experience"
                    type="number"
                    min={0}
                    max={80}
                    className="doctor-form-input"
                    placeholder="e.g. 12"
                    required
                    value={form.years_experience}
                    onChange={(e) => handleFieldChange('years_experience', e.target.value)}
                    disabled={submitting}
                  />
                </div>

                <div className="doctor-form-group doctor-form-full">
                  <label htmlFor="app-qualifications">Degrees & Medical Qualifications *</label>
                  <input
                    id="app-qualifications"
                    type="text"
                    className="doctor-form-input"
                    placeholder="e.g. MBBS, MD (Cardiology), FACS, Board Certified Internal Medicine"
                    required
                    maxLength={255}
                    value={form.qualifications}
                    onChange={(e) => handleFieldChange('qualifications', e.target.value)}
                    disabled={submitting}
                  />
                </div>

                <div className="doctor-form-group">
                  <label htmlFor="app-reg-number">Medical Council Registration / License No. *</label>
                  <input
                    id="app-reg-number"
                    type="text"
                    className="doctor-form-input"
                    placeholder="e.g. MED-89420-NY"
                    required
                    maxLength={120}
                    value={form.registration_number}
                    onChange={(e) => handleFieldChange('registration_number', e.target.value)}
                    disabled={submitting}
                  />
                </div>

                <div className="doctor-form-group">
                  <label htmlFor="app-reg-auth">Issuing Authority / State Council</label>
                  <input
                    id="app-reg-auth"
                    type="text"
                    className="doctor-form-input"
                    placeholder="e.g. State Medical Board, GMC, NMC"
                    maxLength={200}
                    value={form.registration_authority}
                    onChange={(e) => handleFieldChange('registration_authority', e.target.value)}
                    disabled={submitting}
                  />
                </div>

                <div className="doctor-form-group doctor-form-full">
                  <label htmlFor="app-bio">Clinical Biography & Practitioner Statement</label>
                  <textarea
                    id="app-bio"
                    rows={4}
                    className="doctor-form-textarea"
                    placeholder="Summary of clinical training, practice philosophy, areas of special interest, or hospital appointments..."
                    maxLength={5000}
                    value={form.bio}
                    onChange={(e) => handleFieldChange('bio', e.target.value)}
                    disabled={submitting}
                  />
                </div>
              </div>
            </div>

            {/* SECTION 3: Supporting Document Uploads */}
            <div
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '16px',
                padding: '1.75rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '1.25rem',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
                <h3 style={{ fontSize: '1.1rem', margin: 0, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <FileText size={18} color="var(--red-primary)" /> 3. Supporting Verification Documents
                </h3>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                  {documents.length} / {MAX_DOCUMENTS} documents attached
                </span>
              </div>

              <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', margin: 0 }}>
                Upload clear scans or photos of your medical registration certificate, degrees, or government-issued identity proof.
                Accepted formats: PDF, JPG, JPEG, PNG (max 10 MB each).
              </p>

              {/* Uploaded Documents List */}
              {documents.length > 0 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {documents.map((doc, idx) => (
                    <div
                      key={doc.id}
                      style={{
                        background: 'var(--bg-secondary)',
                        border: `1px solid ${doc.error ? 'var(--red-primary)' : 'var(--border-subtle)'}`,
                        borderRadius: '10px',
                        padding: '0.85rem 1rem',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        gap: '1rem',
                        flexWrap: 'wrap',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flex: '1 1 240px' }}>
                        <FileText size={20} color={doc.error ? 'var(--red-primary)' : 'var(--text-muted)'} />
                        <div style={{ overflow: 'hidden' }}>
                          <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)', textOverflow: 'ellipsis', whiteSpace: 'nowrap', overflow: 'hidden' }}>
                            {doc.file.name}
                          </div>
                          <div style={{ fontSize: '0.75rem', color: doc.error ? 'var(--red-primary)' : 'var(--text-muted)' }}>
                            {doc.error ? doc.error : `${(doc.file.size / 1024 / 1024).toFixed(2)} MB`}
                          </div>
                        </div>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <select
                          className="doctor-form-select"
                          style={{ padding: '0.4rem 0.6rem', fontSize: '0.85rem', width: 'auto' }}
                          value={doc.document_type}
                          onChange={(e) => handleDocTypeChange(doc.id, e.target.value)}
                          disabled={submitting}
                        >
                          <option value="medical_registration">Medical Registration</option>
                          <option value="qualification">Medical Degree / Qualification</option>
                          <option value="identity">Government ID / Passport</option>
                          <option value="other">Other Supporting Credential</option>
                        </select>

                        <button
                          type="button"
                          onClick={() => handleRemoveDoc(doc.id)}
                          style={{
                            background: 'transparent',
                            border: 'none',
                            color: 'var(--red-primary)',
                            cursor: 'pointer',
                            padding: '4px',
                            display: 'flex',
                            alignItems: 'center',
                          }}
                          title="Remove document"
                          disabled={submitting}
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Add Document Picker */}
              {documents.length < MAX_DOCUMENTS && (
                <div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept=".pdf,.jpg,.jpeg,.png"
                    onChange={handleAddFiles}
                    style={{ display: 'none' }}
                    id="doc-upload-input"
                    disabled={submitting}
                  />
                  <label
                    htmlFor="doc-upload-input"
                    style={{
                      border: '2px dashed var(--border-subtle)',
                      borderRadius: '12px',
                      padding: '1.25rem',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '0.5rem',
                      cursor: submitting ? 'not-allowed' : 'pointer',
                      background: 'var(--bg-tertiary)',
                      transition: 'border-color 0.2s',
                    }}
                  >
                    <Upload size={22} color="var(--red-primary)" />
                    <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                      Click to choose documents to upload
                    </span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      PDF, JPG, JPEG, or PNG up to 10 MB each (Max {MAX_DOCUMENTS - documents.length} more)
                    </span>
                  </label>
                </div>
              )}
            </div>

            {/* SECTION 4: Declaration & Submission */}
            <div
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '16px',
                padding: '1.75rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '1.25rem',
              }}
            >
              <h3 style={{ fontSize: '1.1rem', margin: 0, color: 'var(--text-primary)' }}>
                4. Applicant Declaration & Submission
              </h3>

              <label
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '0.75rem',
                  fontSize: '0.875rem',
                  color: 'var(--text-secondary)',
                  cursor: 'pointer',
                  lineHeight: '1.4',
                }}
              >
                <input
                  type="checkbox"
                  checked={declarationChecked}
                  onChange={(e) => setDeclarationChecked(e.target.checked)}
                  style={{ marginTop: '3px', cursor: 'pointer' }}
                  disabled={submitting}
                />
                <span>
                  I hereby solemnly affirm that the credentials, medical registration, and qualifications provided are true,
                  authentic, and up to date. I understand that submitting this application creates an intake record only,
                  does not grant immediate dashboard access, and that account creation is strictly contingent on Super Admin verification.
                </span>
              </label>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '0.5rem' }}>
                <Button type="button" variant="secondary" size="lg" onClick={navigateToHome} disabled={submitting}>
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  size="lg"
                  disabled={submitting || !declarationChecked}
                >
                  {submitting ? 'Submitting Application...' : 'Submit Doctor Application'}
                </Button>
              </div>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
