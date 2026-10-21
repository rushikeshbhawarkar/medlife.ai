/** EmptyChat component.
 * Edit this file when changing this component behavior or markup.
 */
import {Sparkles} from 'lucide-react';import {chatSuggestions} from '../../../data/chatSuggestions.js';import './EmptyChat.css';export default function EmptyChat({onSuggestion}){return <div className="empty-chat"><span><Sparkles size={25}/></span><h3>How can I help today?</h3><p>Ask about symptoms, medicines, diet or your health readings.</p><div className="suggestion-chips">{chatSuggestions.map(s=><button key={s} onClick={()=>onSuggestion(s)}>{s}</button>)}</div></div>}