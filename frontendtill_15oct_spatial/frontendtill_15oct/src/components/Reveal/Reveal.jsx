/** Reveal component.
 * Edit this file when changing this component behavior or markup.
 */
import {useEffect,useRef,useState} from 'react';import './Reveal.css';
export default function Reveal({children,delay=0}){const ref=useRef(null);const [visible,setVisible]=useState(false);useEffect(()=>{if(!('IntersectionObserver'in window)){setVisible(true);return}const node=ref.current;const ob=new IntersectionObserver(entries=>{if(entries[0].isIntersecting){setVisible(true);ob.disconnect()}},{threshold:.15});if(node)ob.observe(node);return()=>ob.disconnect()},[]);return <div ref={ref} className={`reveal ${visible?'reveal-visible':''}`} style={{transitionDelay:`${delay}ms`}}>{children}</div>}