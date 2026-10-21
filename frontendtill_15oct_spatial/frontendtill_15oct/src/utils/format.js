/** Chat timestamp formatting.
 * Edit this file when changing how message times appear.
 */
export function formatTime(ts){const d=new Date(ts);return Number.isNaN(d.getTime())?'':d.toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})}