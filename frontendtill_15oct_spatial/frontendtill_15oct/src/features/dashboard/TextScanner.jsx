// import {useEffect,useRef,useState} from 'react';
// import {Camera,FileText,Upload,Trash2,RefreshCw} from 'lucide-react';
// import {scanDocument,listDocuments,deleteDocument} from '../../services/api.js';
// /** Member-specific document scanner. Camera capture uses the native mobile camera when available. */
// export default function TextScanner({memberName}){
//  const [type,setType]=useState('medical_record'),[file,setFile]=useState(null),[busy,setBusy]=useState(false),[error,setError]=useState(''),[notice,setNotice]=useState(''),[docs,setDocs]=useState([]);const input=useRef(null);
//  async function refresh(){try{const d=await listDocuments(memberName);setDocs(d.documents||[])}catch(e){setError(e.message||'Unable to load saved scans.')}}
//  useEffect(()=>{setDocs([]);setError('');refresh()},[memberName]);
//  async function submit(e){e.preventDefault();if(!file)return;setBusy(true);setError('');setNotice('');try{const d=await scanDocument(file,type,memberName);setNotice(d.notice||d.description||d.extracted_text||'Document scanned and saved.');setFile(null);if(input.current)input.current.value='';await refresh()}catch(e){setError(e.message||'Scanning failed.')}finally{setBusy(false)}}
//  async function remove(id){try{await deleteDocument(id);await refresh()}catch(e){setError(e.message||'Unable to delete scan.')}}
//  return <section className="scanner-panel">
//  <div className="scanner-heading"><div><span className="scanner-icon"><FileText size={20}/></span><div><h2>Text scanner</h2><p>Scan and securely save documents for this member</p></div></div><button type="button" className="scanner-refresh" onClick={refresh} aria-label="Refresh saved scans"><RefreshCw size={16}/></button></div>
//  <form onSubmit={submit}><label className="scanner-label">Document type</label><select value={type} onChange={e=>setType(e.target.value)}><option value="medicine_label">Medicine label</option><option value="prescription">Prescription</option><option value="other">Other</option></select>
//  <div className="scanner-drop"><FileText size={25}/><strong>{file?file.name:'Choose a document image'}</strong><span>JPG, PNG or supported image file</span><div className="scanner-actions"><label className="scanner-btn"><Upload size={16}/> Browse<input ref={input} type="file" accept="image/*" onChange={e=>setFile(e.target.files?.[0]||null)}/></label><label className="scanner-btn"><Camera size={16}/> Open camera<input type="file" accept="image/*" capture="environment" onChange={e=>setFile(e.target.files?.[0]||null)}/></label></div></div>
//  <button className="scanner-submit" disabled={!file||busy} type="submit">{busy?'Scanning…':'Scan and save document'}</button></form>
//  {error&&<p className="scanner-error" role="alert">{error}</p>}{notice&&<div className="scanner-result"><strong>Latest scan</strong><p>{notice}</p></div>}
//  <div className="scanner-saved"><h3>Saved scans</h3>{!docs.length?<p className="scanner-muted">No saved scans for this member yet.</p>:docs.map(d=><article className="scanner-document" key={d.id}><div><strong>{d.title||d.documentType||d.document_type||'Scanned document'}</strong><p>{d.createdAt?new Date(d.createdAt).toLocaleString():d.processingStatus||''}</p>{(d.description||d.extracted_text)&&<details><summary>View extracted details</summary><p>{d.description||d.extracted_text}</p></details>}</div><button type="button" onClick={()=>remove(d.id)} aria-label="Delete scan"><Trash2 size={16}/></button></article>)}</div>
//  </section>
// }

















// import {useEffect,useRef,useState} from 'react';
// import {Camera,FileText,Upload,Trash2,RefreshCw} from 'lucide-react';
// import {scanDocument,listDocuments,deleteDocument} from '../../services/api.js';
// /** Member-specific document scanner. Camera capture uses the native mobile camera when available. */
// export default function TextScanner({memberName}){
//  const [type,setType]=useState('medicine_label'),[file,setFile]=useState(null),[busy,setBusy]=useState(false),[error,setError]=useState(''),[notice,setNotice]=useState(''),[docs,setDocs]=useState([]);const input=useRef(null);
//  async function refresh(){try{const d=await listDocuments(memberName);setDocs(d.documents||[])}catch(e){setError(e.message||'Unable to load saved scans.')}}
//  useEffect(()=>{setDocs([]);setError('');refresh()},[memberName]);
//  async function submit(e){e.preventDefault();if(!file)return;setBusy(true);setError('');setNotice('');try{const d=await scanDocument(file,type,memberName);setNotice(d.notice||d.description||d.extracted_text||'Document scanned and saved.');setFile(null);if(input.current)input.current.value='';await refresh()}catch(e){setError(e.message||'Scanning failed.')}finally{setBusy(false)}}
//  async function remove(id){try{await deleteDocument(id);await refresh()}catch(e){setError(e.message||'Unable to delete scan.')}}
//  return <section className="scanner-panel">
//  <div className="scanner-heading"><div><span className="scanner-icon"><FileText size={20}/></span><div><h2>Text scanner</h2><p>Scan and securely save documents for this member</p></div></div><button type="button" className="scanner-refresh" onClick={refresh} aria-label="Refresh saved scans"><RefreshCw size={16}/></button></div>
//  <form onSubmit={submit}><label className="scanner-label">Document type</label><select value={type} onChange={e=>setType(e.target.value)}><option value="medicine_label">Medicine label</option><option value="prescription">Prescription</option><option value="other">Other</option></select>
//  <div className="scanner-drop"><FileText size={25}/><strong>{file?file.name:'Choose a document image'}</strong><span>JPG, PNG or supported image file</span><div className="scanner-actions"><label className="scanner-btn"><Upload size={16}/> Browse<input ref={input} type="file" accept="image/*" onChange={e=>setFile(e.target.files?.[0]||null)}/></label><label className="scanner-btn scanner-camera-btn"><Camera size={16}/> Open camera<input type="file" accept="image/*" capture="environment" aria-label="Take a photo with the device camera" onChange={e=>setFile(e.target.files?.[0]||null)}/></label></div></div>
//  <button className="scanner-submit" disabled={!file||busy} type="submit">{busy?'Scanning…':'Scan and save document'}</button></form>
//  {error&&<p className="scanner-error" role="alert">{error}</p>}{notice&&<div className="scanner-result"><strong>Latest scan</strong><p>{notice}</p></div>}
//  <div className="scanner-saved"><h3>Saved scans</h3>{!docs.length?<p className="scanner-muted">No saved scans for this member yet.</p>:docs.map(d=><article className="scanner-document" key={d.id}><div><strong>{d.title||d.documentType||d.document_type||'Scanned document'}</strong><p>{d.createdAt?new Date(d.createdAt).toLocaleString():d.processingStatus||''}</p>{(d.description||d.extracted_text)&&<details><summary>View extracted details</summary><p>{d.description||d.extracted_text}</p></details>}</div><button type="button" onClick={()=>remove(d.id)} aria-label="Delete scan"><Trash2 size={16}/></button></article>)}</div>
//  </section>
// }













import { useEffect, useRef, useState } from 'react';
import { Camera, FileText, Upload, Trash2, RefreshCw, X, CheckCircle2, AlertCircle } from 'lucide-react';
import { scanDocument, listDocuments, updateDocument, deleteDocument } from '../../services/api.js';

/** Member-specific document scanner with live camera and image upload. */
export default function TextScanner({ memberName }) {
  const [type, setType] = useState('medicine_label');
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [docs, setDocs] = useState([]);
  const [cameraOpen, setCameraOpen] = useState(false);
  const [cameraBusy, setCameraBusy] = useState(false);
  
  const input = useRef(null);
  const cameraInput = useRef(null);
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const canvasRef = useRef(null);

  async function refresh() {
    try {
      const d = await listDocuments(memberName);
      setDocs(d.documents || []);
    } catch (e) {
      setError(e.message || 'Unable to load saved scans.');
    }
  }

  function stopCamera() {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setCameraOpen(false);
    setCameraBusy(false);
  }

  useEffect(() => {
    setDocs([]);
    setFile(null);
    setError('');
    setNotice('');
    refresh();
    return () => {
      streamRef.current?.getTracks().forEach((track) => track.stop());
    };
  }, [memberName]);

  async function openCamera() {
    setError('');
    setNotice('');
    if (!navigator.mediaDevices?.getUserMedia) {
      // Fallback: native camera picker, particularly useful on mobile.
      cameraInput.current?.click();
      setError(
        'Live camera is unavailable in this browser context. ' +
        'Try localhost or HTTPS, or use the device camera picker.'
      );
      return;
    }

    try {
      setCameraBusy(true);

      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: 'environment' } },
        audio: false,
      });

      streamRef.current = stream;
      setCameraOpen(true);
    } catch (e) {
      setCameraBusy(false);

      const messages = {
        NotAllowedError:
          'Camera permission was denied. Allow camera access in your browser settings.',
        NotFoundError: 'No camera was found on this device.',
        NotReadableError: 'The camera is busy or cannot be accessed by the browser.',
      };

      setError(
        messages[e.name] ||
        `Unable to open camera: ${e.message || 'Unknown camera error.'}`
      );
    }
  }

  useEffect(() => {
    if (!cameraOpen || !videoRef.current || !streamRef.current) return;
    const video = videoRef.current;
    video.srcObject = streamRef.current;

    video.play().catch(() => {
      setError('Camera opened, but video playback failed. Try reopening it.');
    });
  }, [cameraOpen]);

  function capturePhoto() {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || !video.videoWidth) {
      setError('Camera is not ready yet. Please wait a moment.');
      return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(
      (blob) => {
        if (!blob) {
          setError('Could not capture the photo. Please try again.');
          return;
        }

        setFile(
          new File([blob], `medlife-scan-${Date.now()}.jpg`, {
            type: 'image/jpeg',
          })
        );

        if (input.current) input.current.value = '';
        setError('');
        setNotice('Photo captured. Select Scan and save document to continue.');
        stopCamera();
      },
      'image/jpeg',
      0.92
    );
  }

  async function submit(e) {
    e.preventDefault();
    if (!file || busy) return;
    setBusy(true);
    setError('');
    setNotice('');

    try {
      const d = await scanDocument(file, type, memberName);

      setNotice(
        d.notice ||
        d.description ||
        d.extracted_text ||
        'Document scanned and saved.'
      );

      setFile(null);
      if (input.current) input.current.value = '';
      await refresh();
    } catch (e) {
      setError(e.message || 'Scanning failed.');
    } finally {
      setBusy(false);
    }
  }

  async function remove(id) {
    try {
      await deleteDocument(id);
      await refresh();
    } catch (e) {
      setError(e.message || 'Unable to delete scan.');
    }
  }

  async function confirmScan(id, description) {
    try {
      await updateDocument(id, { description, isConfirmed: true });
      await refresh();
    } catch (e) {
      setError(e.message || 'Unable to confirm scan.');
    }
  }

  return (
    <section className="scanner-panel">
      <div className="scanner-heading">
        <div>
          <span className="scanner-icon">
            <FileText size={20} />
          </span>
          <div>
            <h2>Text scanner</h2>
            <p>Scan and securely save documents for this member</p>
          </div>
        </div>
        <button
          type="button"
          className="scanner-refresh"
          onClick={refresh}
          aria-label="Refresh saved scans"
        >
          <RefreshCw size={16} />
        </button>
      </div>

      <form onSubmit={submit}>
        <label className="scanner-label">Document type</label>
        <select value={type} onChange={(e) => setType(e.target.value)}>
          <option value="medicine_label">Medicine label</option>
          <option value="prescription">Prescription</option>
          <option value="other">Other</option>
        </select>

        <div className="scanner-drop">
          <FileText size={25} />
          <strong>{file ? file.name : 'Choose a document image'}</strong>
          <span>JPG, PNG or supported image file</span>

          {cameraOpen && (
            <div className="scanner-live-camera">
              <video
                ref={videoRef}
                autoPlay
                muted
                playsInline
                aria-label="Live camera preview"
              />

              <div className="scanner-actions">
                <button
                  type="button"
                  className="scanner-btn scanner-camera-btn"
                  onClick={capturePhoto}
                >
                  <Camera size={16} /> Capture photo
                </button>

                <button
                  type="button"
                  className="scanner-btn"
                  onClick={stopCamera}
                >
                  <X size={16} /> Close camera
                </button>
              </div>
            </div>
          )}

          <canvas ref={canvasRef} hidden />

          <div className="scanner-actions">
            <label className="scanner-btn">
              <Upload size={16} /> Browse
              <input
                ref={input}
                type="file"
                accept="image/*"
                onChange={(e) => {
                  setFile(e.target.files?.[0] || null);
                  setError('');
                  setNotice('');
                }}
              />
            </label>

            <button
              type="button"
              className="scanner-btn scanner-camera-btn"
              onClick={openCamera}
              disabled={cameraBusy || cameraOpen}
            >
              <Camera size={16} />
              {cameraBusy ? 'Opening camera…' : 'Open camera'}
            </button>

            <input
              ref={cameraInput}
              type="file"
              accept="image/*"
              capture="environment"
              hidden
              onChange={(e) => {
                setFile(e.target.files?.[0] || null);
                setError('');
                setNotice('');
              }}
            />
          </div>

          {file && (
            <button
              type="button"
              className="scanner-btn"
              onClick={() => {
                setFile(null);
                if (input.current) input.current.value = '';
                if (cameraInput.current) cameraInput.current.value = '';
                setNotice('');
              }}
            >
              <X size={16} /> Remove selected image
            </button>
          )}
        </div>

        <button
          className="scanner-submit"
          disabled={!file || busy}
          type="submit"
        >
          {busy ? 'Scanning…' : 'Scan and save document'}
        </button>
      </form>

      {error && (
        <p className="scanner-error" role="alert">
          {error}
        </p>
      )}

      {notice && (
        <div className="scanner-result">
          <strong>Latest scan</strong>
          <p>{notice}</p>
        </div>
      )}

      <div className="scanner-saved">
        <h3>Saved scans</h3>

        {!docs.length ? (
          <p className="scanner-muted">No saved scans for this member yet.</p>
        ) : (
          docs.map((d) => (
            <article className="scanner-document" key={d.id}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                  <strong>
                    {d.title || (d.documentType === 'medicine_label' ? 'Medicine label' : d.documentType === 'prescription' ? 'Prescription' : 'Scanned document')}
                  </strong>
                  {d.isConfirmed ? (
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '0.75rem', color: 'var(--sp-ok-text, #10b981)', fontWeight: 600 }}>
                      <CheckCircle2 size={13} /> Verified
                    </span>
                  ) : (
                    <button
                      type="button"
                      className="scanner-btn"
                      style={{ padding: '2px 8px', fontSize: '0.75rem', height: 'auto', minHeight: '26px' }}
                      onClick={() => confirmScan(d.id, d.description)}
                    >
                      <CheckCircle2 size={13} /> Confirm
                    </button>
                  )}
                  {d.processingStatus === 'low_confidence' && (
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '0.75rem', color: 'var(--sp-danger-text, #f59e0b)', fontWeight: 600 }}>
                      <AlertCircle size={13} /> Review needed
                    </span>
                  )}
                </div>

                <p>
                  {d.createdAt
                    ? new Date(d.createdAt).toLocaleString()
                    : d.processingStatus || ''}
                  {d.ocrConfidence ? ` · ${Math.round(d.ocrConfidence)}% confidence` : ''}
                </p>

                {d.structuredData?.medications?.length > 0 && (
                  <div style={{ margin: '8px 0', padding: '8px 10px', background: 'color-mix(in srgb, var(--text-primary) 5%, transparent)', borderRadius: '8px', fontSize: '0.82rem' }}>
                    <span style={{ fontWeight: 600, display: 'block', marginBottom: '4px' }}>Extracted Medications:</span>
                    <ul style={{ margin: 0, paddingLeft: '18px' }}>
                      {d.structuredData.medications.map((m, idx) => (
                        <li key={idx}>
                          <strong>{m.name || 'Medication'}</strong>
                          {m.dosage ? ` — ${m.dosage}` : ''}
                          {m.frequency ? ` (${m.frequency})` : ''}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {(d.description || d.extracted_text) && (
                  <details>
                    <summary>View extracted text</summary>
                    <p style={{ whiteSpace: 'pre-wrap' }}>{d.description || d.extracted_text}</p>
                  </details>
                )}
              </div>

              <button
                type="button"
                onClick={() => remove(d.id)}
                aria-label="Delete scan"
              >
                <Trash2 size={16} />
              </button>
            </article>
          ))
        )}
      </div>
    </section>
  );
}