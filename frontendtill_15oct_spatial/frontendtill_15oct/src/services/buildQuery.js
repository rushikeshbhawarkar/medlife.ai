/** Builds the patient context sent to the AI endpoint.
 * Edit this file when changing which profile details are sent with a question.
 */
export function buildQuery(m,q){return [`Patient details: Name: ${m.firstName||''} ${m.lastName||''}`.trim(),`Date of birth: ${m.dob||'n/a'}`,`Gender: ${m.gender||'n/a'}`,`Race: ${m.race||'n/a'}`,`Height: ${m.height||'n/a'}`,`Weight: ${m.weight||'n/a'}`,`A1C: ${m.a1c||'n/a'}`,`Blood pressure: ${m.bloodPressure||'n/a'}`,`Current medicines / conditions: ${m.medicine||'none listed'}`,`Patient's question: ${q}`].join('. ')}