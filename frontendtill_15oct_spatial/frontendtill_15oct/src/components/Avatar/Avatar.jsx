/** Avatar component.
 * Edit this file when changing this component behavior or markup.
 */
import {initials,avatarColors} from '../../utils/person.js';import './Avatar.css';export default function Avatar({member,index=0,size=42}){const c=avatarColors(index);return <span className="avatar" style={{width:size,height:size,background:`linear-gradient(135deg,${c[0]},${c[1]})`,fontSize:size*.31}} aria-label={member?.firstName?`${member.firstName} avatar`:'Profile avatar'}>{initials(member)}</span>}