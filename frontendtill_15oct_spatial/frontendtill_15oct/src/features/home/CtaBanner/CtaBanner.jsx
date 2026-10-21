/** CtaBanner component.
 * Edit this file when changing this component behavior or markup.
 */
import {ArrowRight} from 'lucide-react';import Button from '../../../components/Button/index.js';import './CtaBanner.css';export default function CtaBanner({onSignIn}){return <section className="cta-section"><div className="container"><div className="cta-banner"><h2>Take the first step towards better health today</h2><p>Start your free trial and get answers in seconds.</p><Button variant="light" size="lg" onClick={onSignIn}>Start Now <ArrowRight size={18}/></Button></div></div></section>}