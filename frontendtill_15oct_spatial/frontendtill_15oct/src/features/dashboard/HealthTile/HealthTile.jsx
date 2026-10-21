/** HealthTile component.
 * Edit this file when changing this component behavior or markup.
 */
import './HealthTile.css';export default function HealthTile({icon:Icon,label,value,status}){return <article className="health-tile"><div className="tile-label"><Icon size={18}/><span>{label}</span></div><strong>{value||'-'}</strong>{status&&<span className={`status-badge status-${status.tone}`}>{status.label}</span>}</article>}