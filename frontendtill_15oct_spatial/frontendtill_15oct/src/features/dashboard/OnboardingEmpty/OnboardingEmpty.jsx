/** OnboardingEmpty component.
 * Edit this file when changing this component behavior or markup.
 */
import {Users,Plus} from 'lucide-react';import Button from '../../../components/Button/index.js';import './OnboardingEmpty.css';export default function OnboardingEmpty({onAdd}){return <div className="onboarding-empty"><span><Users size={30}/></span><h2>Create your first profile</h2><p>Add yourself or a family member to get health answers that fit your details.</p><Button onClick={onAdd}><Plus size={18}/> Add a profile</Button></div>}