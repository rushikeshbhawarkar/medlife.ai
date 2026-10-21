/** Member name, age, avatar colour, and medicine helpers.
 * Edit this file when changing member display helpers.
 */
export function initials(m){const a=(m?.firstName||'').trim()[0]||'',b=(m?.lastName||'').trim()[0]||'';return (a+b).toUpperCase()||'?'}
export function fullName(m){return `${m?.firstName||''} ${m?.lastName||''}`.trim()||'Unnamed'}
export function ageFromDob(dob){if(!dob)return null;const d=new Date(dob);if(Number.isNaN(d.getTime()))return null;const now=new Date();let age=now.getFullYear()-d.getFullYear();if(now.getMonth()<d.getMonth()||(now.getMonth()===d.getMonth()&&now.getDate()<d.getDate()))age--;return age>=0&&age<=129?age:null}
export function avatarColors(i=0){return [['#ff1a3c','#be123c'],['#e11d48','#0a0b0e'],['#ff4765','#991b1b'],['#374151','#0a0b0e']][i%4]}
export function splitMedicines(text){return String(text||'').split(',').map(x=>x.trim()).filter(Boolean)}