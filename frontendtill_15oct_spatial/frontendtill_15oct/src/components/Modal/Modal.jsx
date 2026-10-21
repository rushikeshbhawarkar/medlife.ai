/** Modal component.
 * Edit this file when changing this component behavior or markup.
 */
import { useEffect, useRef } from 'react';
import { X } from 'lucide-react';
import './Modal.css';

export default function Modal({ title, subtitle, onClose, wide = false, children }) {
  const ref = useRef(null);
  const onCloseRef = useRef(onClose);
  onCloseRef.current = onClose;

  useEffect(() => {
    const old = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    const key = e => {
      if (e.key === 'Escape') onCloseRef.current?.();
    };
    window.addEventListener('keydown', key);

    // Focus the first input/select/textarea or primary content button, skipping the close button
    const target =
      ref.current?.querySelector('input:not([disabled]),select:not([disabled]),textarea:not([disabled])') ||
      ref.current?.querySelector('.modal-card button:not(.modal-close)');
    target?.focus();

    return () => {
      document.body.style.overflow = old;
      window.removeEventListener('keydown', key);
    };
  }, []);

  return (
    <div
      className="modal-backdrop"
      onMouseDown={e => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <section
        className={`modal-card ${wide ? 'modal-wide' : ''}`}
        role="dialog"
        aria-modal="true"
        aria-label={title}
        ref={ref}
      >
        <button className="modal-close" aria-label="Close dialog" onClick={onClose}>
          <X />
        </button>
        <h2>{title}</h2>
        {subtitle && <p className="muted modal-subtitle">{subtitle}</p>}
        {children}
      </section>
    </div>
  );
}