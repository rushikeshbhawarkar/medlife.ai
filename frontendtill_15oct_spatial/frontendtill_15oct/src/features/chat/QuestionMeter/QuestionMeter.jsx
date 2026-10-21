/** QuestionMeter component.
 * Edit this file when changing this component behavior or markup.
 */
import './QuestionMeter.css';export default function QuestionMeter({used}){const n=Number(used)||0;return <div className="question-meter" title={`${n} of 100 questions used`}><div><span>Questions</span><b>{n}/100</b></div><div className="meter-track"><span className={n>=90?'meter-danger':''} style={{width:`${Math.min(100,n)}%`}}/></div></div>}