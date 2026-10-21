/** Button component.
 * Edit this file when changing this component behavior or markup.
 */
import './Button.css';
export default function Button({children,variant='primary',size='lg',block=false,className='',...props}){return <button className={`btn btn-${variant} btn-${size} ${block?'btn-block':''} ${className}`} {...props}>{children}</button>}