/** General reference range classification helpers.
 * Edit this file when changing A1C or blood-pressure status thresholds.
 */
export function classifyA1c(v){if(v===null||v===undefined||String(v).trim()===''||!Number.isFinite(Number(v)))return null;const n=Number(v);return n>=6.5?{label:'High',tone:'high'}:n>=5.7?{label:'Elevated',tone:'mid'}:{label:'Normal',tone:'ok'}}
export function classifyBp(v){const m=String(v||'').match(/^\s*(\d{2,3})\s*\/\s*(\d{2,3})\s*$/);if(!m)return null;const s=+m[1],d=+m[2];return s>=140||d>=90?{label:'High',tone:'high'}:s>=130||d>=80?{label:'Elevated',tone:'mid'}:{label:'Normal',tone:'ok'}}