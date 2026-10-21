/** Maps route IDs to page components.
 * Edit this file when changing the public route registry.
 */
import HomePage from '../pages/HomePage/index.js';
import FeaturesPage from '../pages/FeaturesPage/index.js';
import HowItWorksPage from '../pages/HowItWorksPage/index.js';
import PlansPage from '../pages/PlansPage/index.js';
import FaqPage from '../pages/FaqPage/index.js';
export const routes={'/':HomePage,features:FeaturesPage,'how-it-works':HowItWorksPage,plans:PlansPage,faq:FaqPage};