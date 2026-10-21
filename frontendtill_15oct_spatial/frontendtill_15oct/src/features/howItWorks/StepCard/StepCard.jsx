/** StepCard component.
 * Edit this file when changing this component behavior or markup.
 */
import './StepCard.css';export default function StepCard({item,index}){return <article className="step-card"><span className="step-number">{index+1}</span><h3>{item.title}</h3><p>{item.text}</p></article>}