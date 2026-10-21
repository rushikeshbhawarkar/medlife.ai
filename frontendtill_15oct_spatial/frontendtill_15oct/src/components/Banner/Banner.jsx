/** Banner component.
 * Edit this file when changing this component behavior or markup.
 */
import {Info,TriangleAlert} from 'lucide-react';import './Banner.css';export default function Banner({variant='info',children}){const Icon=variant==='error'?TriangleAlert:Info;return <div className={`banner banner-${variant}`} role={variant==='error'?'alert':'status'}><Icon size={19}/><div>{children}</div></div>}