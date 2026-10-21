/**
 * Footer component.
 * Edit the markup or link behavior in this file if the footer layout changes.
 */
import * as Icons from 'lucide-react';
import Logo from '../../components/Logo/index.js';
import { footer } from '../../data/footer.js';
import './Footer.css';

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="container">
        <div className="footer-main">
          <div>
            <Logo light />
            <p className="footer-tagline">{footer.tagline}</p>
            <div className="socials">
              {footer.social.map((s) => {
                const I = Icons[s.icon];
                return (
                  <a href={s.href} aria-label={s.label} key={s.label}>
                    {I && <I size={20} />}
                  </a>
                );
              })}
            </div>
          </div>

          <nav className="footer-links" aria-label="Footer links">
            {footer.links.map((link) => (
              // EDIT FOOTER LINK DESTINATIONS in src/data/footer.js.
              <a href={link.href} key={link.label}>{link.label}</a>
            ))}
          </nav>
        </div>

        <div className="footer-bottom">
          <span>© {new Date().getFullYear()} medlife.ai. All rights reserved.</span>
          <small>{footer.disclaimer}</small>
        </div>
      </div>
    </footer>
  );
}
