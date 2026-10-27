import { useEffect, useState, useCallback } from 'react';
import Modal from '../../components/Modal/index.js';
import Button from '../../components/Button/index.js';
import Spinner from '../../components/Spinner/index.js';
import Banner from '../../components/Banner/index.js';
import {
  getConsultationNote,
  saveConsultationNote,
  getConsultationNoteRevisions,
  downloadConsultationSummary,
} from '../../services/api.js';
import {
  FileText,
  Download,
  History,
  Lock,
  Edit3,
  CheckCircle,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

export default function ConsultationNotesModal({ appointment, isDoctor = false, onClose }) {
  const [content, setContent] = useState('');
  const [sections, setSections] = useState({
    symptoms: '',
    observations: '',
    assessment: '',
    recommendations: '',
    follow_up: '',
  });
  const [noteMeta, setNoteMeta] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Mode for editing: null | 'edit' | 'amend'
  const [isAmending, setIsAmending] = useState(false);
  const [showStructured, setShowStructured] = useState(false);

  // Revision history
  const [showRevisions, setShowRevisions] = useState(false);
  const [revisions, setRevisions] = useState([]);
  const [loadingRevisions, setLoadingRevisions] = useState(false);

  const loadNote = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      const data = await getConsultationNote(appointment.id);
      setContent(data?.content || '');
      setSections({
        symptoms: data?.sections?.symptoms || '',
        observations: data?.sections?.observations || '',
        assessment: data?.sections?.assessment || '',
        recommendations: data?.sections?.recommendations || '',
        follow_up: data?.sections?.follow_up || '',
      });
      setNoteMeta(data);
      if (data?.sections && Object.values(data.sections).some((v) => Boolean(v))) {
        setShowStructured(true);
      }
    } catch (e) {
      if (e.status === 404) {
        setContent('');
        setSections({ symptoms: '', observations: '', assessment: '', recommendations: '', follow_up: '' });
        setNoteMeta(null);
      } else {
        setError(e.message || 'Unable to load consultation note.');
      }
    } finally {
      setLoading(false);
    }
  }, [appointment.id]);

  useEffect(() => {
    loadNote();
  }, [loadNote]);

  const loadRevisions = async () => {
    try {
      setLoadingRevisions(true);
      const data = await getConsultationNoteRevisions(appointment.id);
      setRevisions(data?.revisions || []);
    } catch (e) {
      setError(e.message || 'Unable to load revision history.');
    } finally {
      setLoadingRevisions(false);
    }
  };

  const handleToggleRevisions = () => {
    const next = !showRevisions;
    setShowRevisions(next);
    if (next && revisions.length === 0) {
      loadRevisions();
    }
  };

  const handleDownload = async () => {
    try {
      setDownloading(true);
      setError('');
      await downloadConsultationSummary(appointment.id);
      setSuccess('Consultation summary downloaded successfully.');
    } catch (e) {
      setError(e.message || 'Unable to download consultation summary.');
    } finally {
      setDownloading(false);
    }
  };

  const handleSaveAction = async (actionType) => {
    if (saving) return;
    setError('');
    setSuccess('');

    const cleanSections = {};
    ['symptoms', 'observations', 'assessment', 'recommendations', 'follow_up'].forEach((key) => {
      if (sections[key]?.trim()) {
        cleanSections[key] = sections[key].trim().slice(0, 5000);
      }
    });

    const cleanContent = content.trim();
    if (!cleanContent && Object.keys(cleanSections).length === 0) {
      setError('Please provide consultation note content or at least one structured section.');
      return;
    }

    setSaving(true);
    try {
      const payload = {
        action: actionType,
        content: cleanContent,
        sections: cleanSections,
      };
      const saved = await saveConsultationNote(appointment.id, payload);
      setNoteMeta(saved);
      setIsAmending(false);
      setSuccess(
        actionType === 'finalize'
          ? 'Consultation note finalized successfully. It is now a permanent medical record.'
          : actionType === 'amend'
          ? 'Consultation note amended successfully. Audit revision preserved.'
          : 'Consultation note draft saved successfully.'
      );
      if (showRevisions) {
        loadRevisions();
      }
    } catch (e) {
      setError(e.message || 'Unable to save consultation note.');
    } finally {
      setSaving(false);
    }
  };

  const isFinalized = Boolean(noteMeta?.finalized_at);
  const canEdit = isDoctor && (appointment.status === 'accepted' || appointment.status === 'completed');

  return (
    <Modal
      title={`Consultation Notes — Appointment #${appointment.id}`}
      subtitle={`Patient: ${appointment.member_name || 'Member'} | Status: ${appointment.status}`}
      onClose={onClose}
      wide={true}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {error && <Banner variant="error">{error}</Banner>}
        {success && <Banner variant="info">{success}</Banner>}

        {loading ? (
          <Spinner />
        ) : (
          <>
            {/* Meta & Status bar */}
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: '0.5rem',
                background: 'var(--bg-secondary)',
                padding: '0.65rem 0.85rem',
                borderRadius: '8px',
                border: '1px solid var(--border-subtle)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', flexWrap: 'wrap' }}>
                {isFinalized ? (
                  <span
                    className="status-pill status-accepted"
                    style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', fontWeight: 600 }}
                  >
                    <Lock size={13} /> Finalized
                  </span>
                ) : noteMeta ? (
                  <span
                    className="status-pill status-requested"
                    style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}
                  >
                    Draft
                  </span>
                ) : (
                  <span className="status-pill status-requested">Not Started</span>
                )}

                {noteMeta?.finalized_at && (
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Finalized: {new Date(noteMeta.finalized_at).toLocaleString()}
                  </span>
                )}
                {noteMeta?.updated_at && !noteMeta?.finalized_at && (
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Updated: {new Date(noteMeta.updated_at).toLocaleString()}
                  </span>
                )}
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                {noteMeta && (
                  <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    onClick={handleDownload}
                    disabled={downloading}
                    title="Download Official Consultation Summary"
                  >
                    <Download size={14} /> {downloading ? 'Downloading...' : 'Summary'}
                  </Button>
                )}

                {noteMeta && (
                  <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    onClick={handleToggleRevisions}
                    title="View Revision History"
                  >
                    <History size={14} />
                    Revisions {noteMeta?.revision_count !== undefined ? `(${noteMeta.revision_count})` : ''}
                  </Button>
                )}
              </div>
            </div>

            {/* Revision History Panel */}
            {showRevisions && (
              <div
                style={{
                  background: 'var(--bg-secondary)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '8px',
                  padding: '1rem',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.75rem',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <h4 style={{ margin: 0, fontSize: '0.95rem', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                    <History size={16} /> Audit Revision History
                  </h4>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    {revisions.length} revision{revisions.length === 1 ? '' : 's'} recorded
                  </span>
                </div>

                {loadingRevisions ? (
                  <Spinner />
                ) : revisions.length === 0 ? (
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>
                    No previous revisions. Revisions are recorded whenever a finalized note is amended.
                  </p>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '220px', overflowY: 'auto' }}>
                    {revisions.map((rev, idx) => (
                      <div
                        key={rev.id || idx}
                        style={{
                          background: 'var(--bg-card)',
                          border: '1px solid var(--border-subtle)',
                          borderRadius: '6px',
                          padding: '0.75rem',
                          fontSize: '0.85rem',
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>
                          <span>Revised by: <strong>{rev.revised_by}</strong></span>
                          <span>{new Date(rev.created_at).toLocaleString()}</span>
                        </div>
                        {rev.content && (
                          <div style={{ color: 'var(--text-primary)', whiteSpace: 'pre-wrap', lineHeight: '1.4' }}>
                            {rev.content}
                          </div>
                        )}
                        {rev.sections && Object.keys(rev.sections).length > 0 && (
                          <div style={{ marginTop: '0.35rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                            {Object.entries(rev.sections).map(([k, v]) => v ? (
                              <div key={k}>
                                <strong style={{ textTransform: 'capitalize' }}>{k}:</strong> {v}
                              </div>
                            ) : null)}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Note Body */}
            {canEdit ? (
              isFinalized && !isAmending ? (
                /* Finalized view for Doctor */
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <div
                    style={{
                      background: 'rgba(16, 185, 129, 0.08)',
                      border: '1px solid var(--emerald)',
                      borderRadius: '8px',
                      padding: '0.85rem 1rem',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      gap: '0.75rem',
                      flexWrap: 'wrap',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--emerald)', fontSize: '0.9rem' }}>
                      <Lock size={18} />
                      <span>This consultation note has been finalized. Changes require creating an auditable amendment.</span>
                    </div>
                    <Button
                      type="button"
                      variant="secondary"
                      size="sm"
                      onClick={() => setIsAmending(true)}
                    >
                      <Edit3 size={14} /> Amend Note
                    </Button>
                  </div>

                  {/* Render note sections and content */}
                  <div
                    style={{
                      background: 'var(--bg-secondary)',
                      padding: '1.25rem',
                      borderRadius: '8px',
                      border: '1px solid var(--border-subtle)',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '0.85rem',
                    }}
                  >
                    {sections.symptoms && (
                      <div>
                        <strong style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Symptoms:</strong>
                        <p style={{ margin: '0.2rem 0 0 0', color: 'var(--text-primary)', whiteSpace: 'pre-wrap' }}>{sections.symptoms}</p>
                      </div>
                    )}
                    {sections.observations && (
                      <div>
                        <strong style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Observations:</strong>
                        <p style={{ margin: '0.2rem 0 0 0', color: 'var(--text-primary)', whiteSpace: 'pre-wrap' }}>{sections.observations}</p>
                      </div>
                    )}
                    {sections.assessment && (
                      <div>
                        <strong style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Clinical Assessment:</strong>
                        <p style={{ margin: '0.2rem 0 0 0', color: 'var(--text-primary)', whiteSpace: 'pre-wrap' }}>{sections.assessment}</p>
                      </div>
                    )}
                    {sections.recommendations && (
                      <div>
                        <strong style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Recommendations & Plan:</strong>
                        <p style={{ margin: '0.2rem 0 0 0', color: 'var(--text-primary)', whiteSpace: 'pre-wrap' }}>{sections.recommendations}</p>
                      </div>
                    )}
                    {sections.follow_up && (
                      <div>
                        <strong style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Follow-up:</strong>
                        <p style={{ margin: '0.2rem 0 0 0', color: 'var(--text-primary)', whiteSpace: 'pre-wrap' }}>{sections.follow_up}</p>
                      </div>
                    )}
                    {content && (
                      <div>
                        <strong style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>General Notes:</strong>
                        <p style={{ margin: '0.2rem 0 0 0', color: 'var(--text-primary)', whiteSpace: 'pre-wrap' }}>{content}</p>
                      </div>
                    )}
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                    <Button type="button" variant="secondary" onClick={onClose}>
                      Close
                    </Button>
                  </div>
                </div>
              ) : (
                /* Editable form: Draft or Amending */
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    handleSaveAction(isAmending ? 'amend' : 'save');
                  }}
                  style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}
                >
                  {isAmending && (
                    <div
                      style={{
                        background: 'rgba(234, 179, 8, 0.1)',
                        border: '1px solid var(--warning)',
                        borderRadius: '8px',
                        padding: '0.75rem 1rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        color: 'var(--warning)',
                        fontSize: '0.875rem',
                      }}
                    >
                      <AlertTriangle size={18} />
                      <span>
                        <strong>Amendment Mode:</strong> Submitting will record the current note as a snapshot in the revision history and update the finalized record.
                      </span>
                    </div>
                  )}

                  {/* Toggle structured clinical sections */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <label htmlFor="consultation-notes-area" style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                      Clinical Assessment & Notes
                    </label>
                    <button
                      type="button"
                      onClick={() => setShowStructured((prev) => !prev)}
                      style={{
                        background: 'transparent',
                        border: 'none',
                        color: 'var(--red-primary)',
                        fontSize: '0.825rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.3rem',
                      }}
                    >
                      {showStructured ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                      {showStructured ? 'Hide Structured Sections' : 'Show Structured Sections (Symptoms, Assessment, etc.)'}
                    </button>
                  </div>

                  {/* Structured Sections */}
                  {showStructured && (
                    <div
                      style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                        gap: '0.75rem',
                        background: 'var(--bg-secondary)',
                        padding: '1rem',
                        borderRadius: '8px',
                        border: '1px solid var(--border-subtle)',
                      }}
                    >
                      <div className="doctor-form-group">
                        <label htmlFor="sec-symptoms">Symptoms Reported</label>
                        <input
                          id="sec-symptoms"
                          type="text"
                          className="doctor-form-input"
                          placeholder="e.g. Headache, fever for 3 days"
                          value={sections.symptoms}
                          onChange={(e) => setSections({ ...sections, symptoms: e.target.value })}
                          disabled={saving}
                          maxLength={5000}
                        />
                      </div>

                      <div className="doctor-form-group">
                        <label htmlFor="sec-observations">Clinical Observations</label>
                        <input
                          id="sec-observations"
                          type="text"
                          className="doctor-form-input"
                          placeholder="e.g. BP 120/80, normal chest sounds"
                          value={sections.observations}
                          onChange={(e) => setSections({ ...sections, observations: e.target.value })}
                          disabled={saving}
                          maxLength={5000}
                        />
                      </div>

                      <div className="doctor-form-group">
                        <label htmlFor="sec-assessment">Assessment / Diagnosis</label>
                        <input
                          id="sec-assessment"
                          type="text"
                          className="doctor-form-input"
                          placeholder="e.g. Acute viral rhinitis"
                          value={sections.assessment}
                          onChange={(e) => setSections({ ...sections, assessment: e.target.value })}
                          disabled={saving}
                          maxLength={5000}
                        />
                      </div>

                      <div className="doctor-form-group">
                        <label htmlFor="sec-recommendations">Recommendations & Prescriptions</label>
                        <input
                          id="sec-recommendations"
                          type="text"
                          className="doctor-form-input"
                          placeholder="e.g. Rest, hydration, paracetamol 500mg SOS"
                          value={sections.recommendations}
                          onChange={(e) => setSections({ ...sections, recommendations: e.target.value })}
                          disabled={saving}
                          maxLength={5000}
                        />
                      </div>

                      <div className="doctor-form-group" style={{ gridColumn: '1 / -1' }}>
                        <label htmlFor="sec-followup">Follow-up Instructions</label>
                        <input
                          id="sec-followup"
                          type="text"
                          className="doctor-form-input"
                          placeholder="e.g. Return in 5 days if fever persists"
                          value={sections.follow_up}
                          onChange={(e) => setSections({ ...sections, follow_up: e.target.value })}
                          disabled={saving}
                          maxLength={5000}
                        />
                      </div>
                    </div>
                  )}

                  {/* General / Main Content Area */}
                  <div className="doctor-form-group">
                    <label htmlFor="consultation-notes-area">
                      General Clinical Narrative & Notes
                    </label>
                    <textarea
                      id="consultation-notes-area"
                      className="doctor-form-textarea"
                      rows={6}
                      placeholder="Enter detailed clinical narrative, diagnostic rationale, treatment discussions, and patient advice..."
                      value={content}
                      onChange={(e) => setContent(e.target.value)}
                      disabled={saving}
                      maxLength={20000}
                    />
                    <small style={{ color: 'var(--text-muted)' }}>
                      Note: The patient must have granted &ldquo;consultation_notes&rdquo; consent scope to save notes.
                    </small>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', flexWrap: 'wrap' }}>
                    {isAmending && (
                      <Button
                        type="button"
                        variant="secondary"
                        onClick={() => setIsAmending(false)}
                        disabled={saving}
                      >
                        Cancel Amendment
                      </Button>
                    )}

                    <Button type="button" variant="secondary" onClick={onClose} disabled={saving}>
                      Close
                    </Button>

                    {!isFinalized && !isAmending && (
                      <>
                        <Button
                          type="button"
                          variant="secondary"
                          onClick={() => handleSaveAction('save')}
                          disabled={saving}
                        >
                          {saving ? 'Saving...' : 'Save Draft'}
                        </Button>
                        <Button
                          type="button"
                          variant="primary"
                          onClick={() => {
                            if (window.confirm('Finalize this consultation note? Finalized notes cannot be directly edited without creating an audit amendment.')) {
                              handleSaveAction('finalize');
                            }
                          }}
                          disabled={saving}
                        >
                          <Lock size={14} /> Finalize Note
                        </Button>
                      </>
                    )}

                    {isAmending && (
                      <Button
                        type="button"
                        variant="primary"
                        onClick={() => handleSaveAction('amend')}
                        disabled={saving}
                      >
                        <Edit3 size={14} /> {saving ? 'Submitting...' : 'Save Auditable Amendment'}
                      </Button>
                    )}
                  </div>
                </form>
              )
            ) : (
              /* Patient Read-Only View */
              <div>
                {content || Object.values(sections).some((v) => Boolean(v)) ? (
                  <div
                    style={{
                      background: 'var(--bg-secondary)',
                      padding: '1.25rem',
                      borderRadius: '8px',
                      border: '1px solid var(--border-subtle)',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '0.85rem',
                    }}
                  >
                    {sections.symptoms && (
                      <div>
                        <strong style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Symptoms:</strong>
                        <p style={{ margin: '0.2rem 0 0 0', color: 'var(--text-primary)', whiteSpace: 'pre-wrap' }}>{sections.symptoms}</p>
                      </div>
                    )}
                    {sections.observations && (
                      <div>
                        <strong style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Observations:</strong>
                        <p style={{ margin: '0.2rem 0 0 0', color: 'var(--text-primary)', whiteSpace: 'pre-wrap' }}>{sections.observations}</p>
                      </div>
                    )}
                    {sections.assessment && (
                      <div>
                        <strong style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Clinical Assessment:</strong>
                        <p style={{ margin: '0.2rem 0 0 0', color: 'var(--text-primary)', whiteSpace: 'pre-wrap' }}>{sections.assessment}</p>
                      </div>
                    )}
                    {sections.recommendations && (
                      <div>
                        <strong style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Recommendations & Plan:</strong>
                        <p style={{ margin: '0.2rem 0 0 0', color: 'var(--text-primary)', whiteSpace: 'pre-wrap' }}>{sections.recommendations}</p>
                      </div>
                    )}
                    {sections.follow_up && (
                      <div>
                        <strong style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Follow-up:</strong>
                        <p style={{ margin: '0.2rem 0 0 0', color: 'var(--text-primary)', whiteSpace: 'pre-wrap' }}>{sections.follow_up}</p>
                      </div>
                    )}
                    {content && (
                      <div>
                        <strong style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Doctor Notes:</strong>
                        <p style={{ margin: '0.2rem 0 0 0', color: 'var(--text-primary)', whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>{content}</p>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="doctor-empty-state">
                    <p>No consultation notes have been recorded for this appointment yet.</p>
                  </div>
                )}
                <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem' }}>
                  <Button type="button" variant="secondary" onClick={onClose}>
                    Close
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </Modal>
  );
}
