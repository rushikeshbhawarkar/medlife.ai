/** SectionHeader component.
 * Edit this file when changing this component behavior or markup.
 */
import './SectionHeader.css';
export default function SectionHeader({eyebrow,title,text,center=true}){return <div className={`section-header ${center?'is-center':''}`}><div className="eyebrow">{eyebrow}</div><h2>{title}</h2>{text&&<p>{text}</p>}</div>}