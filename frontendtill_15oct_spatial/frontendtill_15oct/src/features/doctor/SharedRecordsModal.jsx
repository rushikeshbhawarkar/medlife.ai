import { useEffect, useState, useCallback } from 'react';
import Modal from '../../components/Modal/index.js';
import Button from '../../components/Button/index.js';
import Spinner from '../../components/Spinner/index.js';
import Banner from '../../components/Banner/index.js';
import { getSharedRecords } from '../../services/api.js';
import { Activity, FileText, Pill, ShieldCheck } from 'lucide-react';

export default function SharedRecordsModal({ memberId, memberName, onClose }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadRecords = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      const res = await getSharedRecords(memberId);
      setData(res);
    } catch (e) {
      setError(e.message || 'Unable to access shared medical records.');
    } finally {
      setLoading(false);
    }
  }, [memberId]);

  useEffect(() => {
    loadRecords();
  }, [loadRecords]);

  return (
    <Modal
      title={`Shared Medical Records — ${memberName || data?.member_name || `Member #${memberId}`}`}
      subtitle="Authorized clinical view based on patient-granted consent scopes"
      onClose={onClose}
      wide={true}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {error && <Banner variant="error">{error}</Banner>}

        {loading ? (
          <Spinner />
        ) : data ? (
          <>
            {/* Active Consent Scopes */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                <ShieldCheck size={16} color="var(--emerald)" /> Active Scopes:
              </span>
              <div className="scope-chips">
                {(data.consent_scopes || []).map((scope) => (
                  <span key={scope} className="scope-chip">
                    {scope}
                  </span>
                ))}
              </div>
            </div>

            {/* Health Metrics Tiles */}
            <div>
              <h4 style={{ fontSize: '0.95rem', color: 'var(--text-primary)', marginBottom: '0.6rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Activity size={17} color="var(--red-primary)" /> Vital Health Metrics
              </h4>
              <div className="request-details-grid">
                <div className="request-detail-item">
                  <span className="request-detail-label">Height</span>
                  <span className="request-detail-val">{data.height || 'Not recorded'}</span>
                </div>
                <div className="request-detail-item">
                  <span className="request-detail-label">Weight</span>
                  <span className="request-detail-val">{data.weight || 'Not recorded'}</span>
                </div>
                <div className="request-detail-item">
                  <span className="request-detail-label">Blood Pressure</span>
                  <span className="request-detail-val">{data.blood_pressure || 'Not recorded'}</span>
                </div>
                <div className="request-detail-item">
                  <span className="request-detail-label">HbA1c</span>
                  <span className="request-detail-val">{data.a1c ? `${data.a1c}%` : 'Not recorded'}</span>
                </div>
              </div>
            </div>

            {/* Current Medicines */}
            <div>
              <h4 style={{ fontSize: '0.95rem', color: 'var(--text-primary)', marginBottom: '0.6rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Pill size={17} color="var(--warning)" /> Current Medications
              </h4>
              <div
                style={{
                  background: 'var(--bg-secondary)',
                  padding: '0.85rem 1rem',
                  borderRadius: '8px',
                  border: '1px solid var(--border-subtle)',
                  color: 'var(--text-primary)',
                  fontSize: '0.9rem',
                  whiteSpace: 'pre-wrap',
                }}
              >
                {data.medicine || 'No medications listed by patient.'}
              </div>
            </div>

            {/* Medical Summary / Description */}
            {data.medical_description && (
              <div>
                <h4 style={{ fontSize: '0.95rem', color: 'var(--text-primary)', marginBottom: '0.6rem' }}>
                  Medical History & Notes
                </h4>
                <div
                  style={{
                    background: 'var(--bg-secondary)',
                    padding: '0.85rem 1rem',
                    borderRadius: '8px',
                    border: '1px solid var(--border-subtle)',
                    color: 'var(--text-primary)',
                    fontSize: '0.875rem',
                    whiteSpace: 'pre-wrap',
                    lineHeight: '1.5',
                  }}
                >
                  {data.medical_description}
                </div>
              </div>
            )}

            {/* Documents (if permitted) */}
            {data.documents && (
              <div>
                <h4 style={{ fontSize: '0.95rem', color: 'var(--text-primary)', marginBottom: '0.6rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <FileText size={17} /> Scanned Medical Documents ({data.documents.length})
                </h4>
                {data.documents.length === 0 ? (
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No documents uploaded for this member.</p>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '200px', overflowY: 'auto' }}>
                    {data.documents.map((doc) => (
                      <div
                        key={doc.id}
                        style={{
                          background: 'var(--bg-secondary)',
                          border: '1px solid var(--border-subtle)',
                          borderRadius: '8px',
                          padding: '0.65rem 0.85rem',
                          fontSize: '0.85rem',
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 600, color: 'var(--text-primary)' }}>
                          <span style={{ textTransform: 'capitalize' }}>{doc.document_type || 'Document'}</span>
                          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                            {new Date(doc.created_at).toLocaleDateString()}
                          </span>
                        </div>
                        <div style={{ color: 'var(--text-secondary)', marginTop: '0.25rem', whiteSpace: 'pre-wrap' }}>
                          {doc.description}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Past Consultation Notes (if permitted) */}
            {data.consultation_notes && (
              <div>
                <h4 style={{ fontSize: '0.95rem', color: 'var(--text-primary)', marginBottom: '0.6rem' }}>
                  Past Consultation Notes ({data.consultation_notes.length})
                </h4>
                {data.consultation_notes.length === 0 ? (
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No past consultation notes.</p>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '200px', overflowY: 'auto' }}>
                    {data.consultation_notes.map((note, idx) => (
                      <div
                        key={idx}
                        style={{
                          background: 'var(--bg-secondary)',
                          border: '1px solid var(--border-subtle)',
                          borderRadius: '8px',
                          padding: '0.65rem 0.85rem',
                          fontSize: '0.85rem',
                        }}
                      >
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                          Appointment #{note.appointment_id} • {new Date(note.updated_at).toLocaleDateString()}
                        </div>
                        <div style={{ color: 'var(--text-primary)', whiteSpace: 'pre-wrap' }}>{note.content}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </>
        ) : null}

        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
          <Button type="button" variant="secondary" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </Modal>
  );
}
