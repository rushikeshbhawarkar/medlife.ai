import {Pill,Info,FileText} from 'lucide-react';
import {splitMedicines} from '../../../utils/person.js';
import './MedicinesList.css';

export default function MedicinesList({medicine,medicalDescription}){
 const items=splitMedicines(medicine);
 return (
  <section className="medicines-card">
   <h3><Pill size={19}/> Medicines &amp; conditions</h3>
   {items.length?(
    <div className="medicine-chips">
     {items.map(x=><span key={x}>{x}</span>)}
    </div>
   ):(
    <i className="muted">None listed</i>
   )}

   {medicalDescription&&(
    <div className="medical-desc-section">
     <h4><FileText size={16}/> Clinical notes &amp; history</h4>
     <p>{medicalDescription}</p>
    </div>
   )}

   <p className="medicine-note">
    <Info size={15}/> Status labels use general reference ranges for guidance only, not a diagnosis.
   </p>
  </section>
 );
}