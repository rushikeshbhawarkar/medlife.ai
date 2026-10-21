import {useState} from 'react';
import {Eye,EyeOff,KeyRound} from 'lucide-react';
import Modal from '../../../components/Modal/index.js';
import Button from '../../../components/Button/index.js';
import {changePassword} from '../../../services/api.js';
import './ChangePasswordModal.css';

export default function ChangePasswordModal({onClose,email}){
 const [newPassword,setNewPassword]=useState('');
 const [confirmPassword,setConfirmPassword]=useState('');
 const [showNew,setShowNew]=useState(false);
 const [error,setError]=useState('');
 const [success,setSuccess]=useState('');
 const [busy,setBusy]=useState(false);

 async function submit(e){
  e.preventDefault();
  setError('');
  setSuccess('');

  if(newPassword.length<6){
   setError('New password must be at least 6 characters.');
   return;
  }
  if(newPassword!==confirmPassword){
   setError('New passwords do not match.');
   return;
  }

  setBusy(true);
  try{
   const r=await changePassword('',newPassword,confirmPassword);
   setSuccess(r.detail||'Password updated successfully.');
   setTimeout(()=>{
    onClose();
   },1800);
  }catch(err){
   setError(err.message||'Unable to update password.');
  }finally{
   setBusy(false);
  }
 }

 return (
  <Modal
   title="Password & Security"
   subtitle="Change your password or set a password for your MedLife account."
   onClose={onClose}
  >
   <form className="change-password-form" onSubmit={submit}>
    <label>New password</label>
    <div className="email-input">
     <input
      type={showNew?'text':'password'}
      required
      minLength={6}
      value={newPassword}
      onChange={e=>setNewPassword(e.target.value)}
      placeholder="At least 6 characters"
      autoComplete="new-password"
     />
     <button
      type="button"
      className="password-toggle"
      aria-label={showNew?'Hide password':'Show password'}
      onClick={()=>setShowNew(v=>!v)}
     >
      {showNew?<EyeOff size={18}/>:<Eye size={18}/>}
     </button>
    </div>

    <label>Confirm new password</label>
    <div className="email-input">
     <input
      type={showNew?'text':'password'}
      required
      minLength={6}
      value={confirmPassword}
      onChange={e=>setConfirmPassword(e.target.value)}
      placeholder="Re-enter new password"
      autoComplete="new-password"
     />
    </div>

    {error&&<p className="field-error" role="alert">{error}</p>}
    {success&&<p className="field-success" role="status">{success}</p>}

    <div className="form-actions">
     <Button variant="ghost" type="button" onClick={onClose} disabled={busy}>
      Cancel
     </Button>
     <Button type="submit" disabled={busy}>
      <KeyRound size={17}/>
      {busy?'Saving...':'Update password'}
     </Button>
    </div>
   </form>
  </Modal>
 );
}

