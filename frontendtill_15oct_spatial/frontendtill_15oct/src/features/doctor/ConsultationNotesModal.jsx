import { useEffect, useState, useCallback } from 'react';
import Modal from '../../components/Modal/index.js';
import Button from '../../components/Button/index.js';
import Spinner from '../../components/Spinner/index.js';
import Banner from '../../components/Banner/index.js';
import { getConsultationNote, saveConsultationNote } from '../../services/api.js';

export default function ConsultationNotesModal({ appointment, isDoctor = false, onClose }) {
  const [content, setContent] = useState('');
  const [noteMeta, setNoteMeta] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const loadNote = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      const data = await getConsultationNote(appointment.id);
      setContent(data?.content || '');
      setNoteMeta(data);
    } catch (e) {
      if (e.status === 404) {
        setContent('');
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

  const handleSave = async (e) => {
    e.preventDefault();
    if (!content.trim() || saving) return;
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const saved = await saveConsultationNote(appointment.id, content.trim());
      setNoteMeta(saved);
      setSuccess('Consultation note saved successfully.');
    } catch (e) {
      setError(e.message || 'Unable to save consultation note.');
    } finally {
      setSaving(false);
    }
  };

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
            {noteMeta?.updated_at && (
              <p style={{ fontSize: '0.825rem', color: 'var(--text-muted)', margin: 0 }}>
                Last updated: {new Date(noteMeta.updated_at).toLocaleString()}
              </p>
            )}

            {canEdit ? (
              <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div className="doctor-form-group">
                  <label htmlFor="consultation-notes-area">Consultation Assessment & Prescription Notes</label>
                  <textarea
                    id="consultation-notes-area"
                    className="doctor-form-textarea"
                    rows={8}
                    placeholder="Enter clinical assessment, diagnostic notes, treatment plan, and prescription recommendations..."
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    disabled={saving}
                    maxLength={20000}
                    required
                  />
                  <small style={{ color: 'var(--text-muted)' }}>
                    Note: The patient must have granted &ldquo;consultation_notes&rdquo; consent scope to save notes.
                  </small>
                </div>
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                  <Button type="button" variant="secondary" onClick={onClose} disabled={saving}>
                    Close
                  </Button>
                  <Button type="submit" variant="primary" disabled={saving || !content.trim()}>
                    {saving ? 'Saving...' : 'Save Consultation Note'}
                  </Button>
                </div>
              </form>
            ) : (
              <div>
                {content ? (
                  <div
                    style={{
                      background: 'var(--bg-secondary)',
                      padding: '1.25rem',
                      borderRadius: '8px',
                      border: '1px solid var(--border-subtle)',
                      color: 'var(--text-primary)',
                      whiteSpace: 'pre-wrap',
                      lineHeight: '1.6',
                      fontSize: '0.925rem',
                    }}
                  >
                    {content}
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
