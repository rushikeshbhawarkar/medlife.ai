/** TypingIndicator component.
 * Edit this file when changing this component behavior or markup.
 */
import {HeartPulse} from 'lucide-react';import './TypingIndicator.css';export default function TypingIndicator(){return <div className="typing-row"><span><HeartPulse size={17}/></span><div className="typing-bubble" aria-label="medlife.ai is typing"><i/><i/><i/></div></div>}