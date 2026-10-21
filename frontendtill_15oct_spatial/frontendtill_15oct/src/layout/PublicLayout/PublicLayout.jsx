/** PublicLayout component.
 * Edit this file when changing this component behavior or markup.
 */
import Navbar from '../Navbar/index.js';import Footer from '../Footer/index.js';import './PublicLayout.css';export default function PublicLayout({route,onSignIn,children}){return <><Navbar route={route} onSignIn={onSignIn}/><main className="public-main">{children}</main><Footer/></>}