/** RichText component.
 * Edit this file when changing this component behavior or markup.
 */
import './RichText.css';
function inline(s){return s.split(/(\*\*.*?\*\*)/g).map((x,i)=>x.startsWith('**')&&x.endsWith('**')?<strong key={i}>{x.slice(2,-2)}</strong>:x)}
export default function RichText({text=''}){const lines=String(text).split('\n');return <div className="rich-text">{lines.map((line,i)=>{const t=line.trim();if(!t)return <div key={i} className="rich-space"/>;if(/^[-*•]\s/.test(t))return <div key={i} className="rich-list">• {inline(t.replace(/^[-*•]\s/,''))}</div>;if(/^\d+[.)]\s/.test(t))return <div key={i} className="rich-list">{inline(t)}</div>;return <p key={i}>{inline(t.replace(/^#+\s*/,''))}</p>})}</div>}