/** FaqItem component.
 * Edit this file when changing this component behavior or markup.
 */
import {ChevronDown} from 'lucide-react';import './FaqItem.css';export default function FaqItem({item,open,onClick}){return <section className={`faq-item ${open?'faq-open':''}`}><button className="faq-question" onClick={onClick} aria-expanded={open}><span>{item.q}</span><ChevronDown size={20}/></button><div className="faq-answer" aria-hidden={!open}><div><p>{item.a}</p></div></div></section>}