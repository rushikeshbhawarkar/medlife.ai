/** FeatureCard component.
 * Edit this file when changing this component behavior or markup.
 */
import * as Icons from 'lucide-react';import './FeatureCard.css';export default function FeatureCard({item}){const I=Icons[item.icon]||Icons.Sparkles;return <article className="feature-card"><span className="feature-icon"><I size={24}/></span><h3>{item.title}</h3><p>{item.text}</p></article>}