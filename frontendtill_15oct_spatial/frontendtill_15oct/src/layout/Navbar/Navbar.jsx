/** Navbar component.
 * Edit this file when changing this component behavior or markup.

import {useEffect,useState} from 'react';import {Menu,X,UserRound,Sun,Moon} from 'lucide-react';import Logo from '../../components/Logo/index.js';import Button from '../../components/Button/index.js';import {navLinks} from '../../data/navLinks.js';import './Navbar.css';
export default function Navbar({route,onSignIn}){const [scrolled,setScrolled]=useState(false),[open,setOpen]=useState(false);const [theme,setTheme]=useState(()=>document.documentElement.getAttribute('data-theme')||'dark');const toggleTheme=()=>{const next=theme==='dark'?'light':'dark';document.documentElement.setAttribute('data-theme',next);try{localStorage.setItem('medlife_theme',next)}catch{}setTheme(next)};useEffect(()=>{const f=()=>setScrolled(window.scrollY>12);f();window.addEventListener('scroll',f);return()=>window.removeEventListener('scroll',f)},[]);return <header className={`navbar ${scrolled?'navbar-scrolled':''}`}><div className="container nav-row"><Logo/><nav className={`nav-links ${open?'nav-open':''}`} aria-label="Main navigation">{navLinks.map(n=><a key={n.route} href={`#/${n.route}`} onClick={()=>setOpen(false)} className={route===n.route?'nav-active':''} aria-current={route===n.route?'page':undefined}>{n.label}</a>)}<div className="mobile-sign"><Button variant="ghost" size="sm" onClick={()=>{setOpen(false);onSignIn()}}><UserRound size={18}/> Sign in</Button></div></nav><div className="nav-actions"><Button variant="ghost" size="sm" onClick={onSignIn}><UserRound size={18}/> Sign in</Button><button className="theme-toggle" aria-label={theme==='dark'?'Switch to light mode':'Switch to dark mode'} title={theme==='dark'?'Switch to light mode':'Switch to dark mode'} onClick={toggleTheme}>{theme==='dark'?<Sun size={18}/>:<Moon size={18}/>}</button><button className="menu-toggle" aria-label={open?'Close navigation menu':'Open navigation menu'} aria-expanded={open} onClick={()=>setOpen(!open)}>{open?<X/>:<Menu/>}</button></div></div></header>}
*/ 






/** Navbar component.
 * Edit this file when changing this component behavior or markup.
 */
import {useEffect,useState} from 'react';
import {Menu,X,UserRound,Sun,Moon,Palette} from 'lucide-react';
import Logo from '../../components/Logo/index.js';
import Button from '../../components/Button/index.js';
import {navLinks} from '../../data/navLinks.js';
import './Navbar.css';

export default function Navbar({route,onSignIn}){
 const [scrolled,setScrolled]=useState(false),[open,setOpen]=useState(false);
 const [theme,setTheme]=useState(()=>document.documentElement.getAttribute('data-theme')||localStorage.getItem('medlife_theme')||'dark');
 const [palette,setPalette]=useState(()=>document.documentElement.getAttribute('data-palette')||localStorage.getItem('medlife_palette')||'red');
 const toggleTheme=()=>{const next=theme==='dark'?'light':'dark';document.documentElement.setAttribute('data-theme',next);try{localStorage.setItem('medlife_theme',next)}catch{}setTheme(next)};
 const changePalette=e=>{const next=e.target.value;document.documentElement.setAttribute('data-palette',next);try{localStorage.setItem('medlife_palette',next)}catch{}setPalette(next)};
 useEffect(()=>{document.documentElement.setAttribute('data-theme',theme);document.documentElement.setAttribute('data-palette',palette)},[]);
 useEffect(()=>{const f=()=>setScrolled(window.scrollY>12);f();window.addEventListener('scroll',f);return()=>window.removeEventListener('scroll',f)},[]);
 return <header className={`navbar ${scrolled?'navbar-scrolled':''}`}><div className="container nav-row"><Logo/><nav className={`nav-links ${open?'nav-open':''}`} aria-label="Main navigation">{navLinks.map(n=><a key={n.route} href={`#/${n.route}`} onClick={()=>setOpen(false)} className={route===n.route?'nav-active':''} aria-current={route===n.route?'page':undefined}>{n.label}</a>)}<div className="mobile-sign"><Button variant="ghost" size="sm" onClick={()=>{setOpen(false);onSignIn()}}><UserRound size={18}/> Sign in</Button></div></nav><div className="nav-actions"><Button variant="ghost" size="sm" onClick={onSignIn}><UserRound size={18}/> Sign in</Button><button className="theme-toggle" aria-label={theme==='dark'?'Switch to light mode':'Switch to dark mode'} title={theme==='dark'?'Switch to light mode':'Switch to dark mode'} onClick={toggleTheme}>{theme==='dark'?<Sun size={18}/>:<Moon size={18}/>}</button><label className="palette-control" title="Change website colour theme"><Palette size={16}/><select className="palette-select" aria-label="Choose website colour theme" value={palette} onChange={changePalette}><option value="red">Red</option><option value="green">Green</option></select></label><button className="menu-toggle" aria-label={open?'Close navigation menu':'Open navigation menu'} aria-expanded={open} onClick={()=>setOpen(!open)}>{open?<X/>:<Menu/>}</button></div></div></header>
}

