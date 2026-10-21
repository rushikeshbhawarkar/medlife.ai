/** Logo component.
 * Edit this file when changing this component behavior or markup.
 */
import {HeartPulse} from 'lucide-react';import './Logo.css';
export default function Logo({light=false,toHome=true}){const body=<><span className="logo-mark"><HeartPulse size={20} strokeWidth={2.4}/></span><span className={light?'logo-word logo-light':'logo-word'}>medlife<span>.ai</span></span></>;return toHome?<a className="brand-logo" href="#/" aria-label="medlife.ai home">{body}</a>:<div className="brand-logo">{body}</div>}