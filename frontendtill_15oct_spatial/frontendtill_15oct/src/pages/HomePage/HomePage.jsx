/** HomePage component.
 * Edit this file when changing this component behavior or markup.
 */
import Hero from '../../features/home/Hero/index.js';import CtaBanner from '../../features/home/CtaBanner/index.js';export default function HomePage({onSignIn}){return <><Hero/><CtaBanner onSignIn={onSignIn}/></>}