/** Production API client for the Medlife Django backend.
 * Configure VITE_API_BASE in .env (example: http://localhost:8000/medlife).
 * No demo fallback: backend/network errors are shown to the user.
 */
const BASE=((typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_BASE)||'http://localhost:8000/medlife').replace(/\/+$/,'');
let token=localStorage.getItem('medlife_access_token')||'';
let consentCache=null;
let inFlightConsent=null;
export const clearConsentCache=()=>{consentCache=null;inFlightConsent=null;};
export const setAccessToken=value=>{token=value||'';if(!value)clearConsentCache();try{value?localStorage.setItem('medlife_access_token',value):localStorage.removeItem('medlife_access_token')}catch{}};
export const getAccessToken=()=>token;
export class ApiError extends Error{constructor(status,message){super(message);this.name='ApiError';this.status=status}}
async function call(path,{method='GET',params={},body,formData=false,auth=true,timeout=120000}={}){
 const url=new URL(BASE+path,window.location.href);Object.entries(params).forEach(([k,v])=>{if(v!==undefined&&v!==null)url.searchParams.set(k,v)});
 const ctrl=new AbortController(),timer=setTimeout(()=>ctrl.abort(),timeout);
 try{
  const headers={};if(auth&&token)headers.Authorization=`Bearer ${token}`;if(body&&!formData)headers['Content-Type']='application/json';
  let r;try{r=await fetch(url,{method,signal:ctrl.signal,headers,body:body?(formData?body:JSON.stringify(body)):undefined})}catch(e){throw new Error(e.name==='AbortError'?'The server took too long to respond.':'Cannot reach the backend. Check VITE_API_BASE and that the backend is running.')};
  const raw=await r.text();let data;try{data=raw?JSON.parse(raw):{}}catch{data=raw}
  if(!r.ok){
   if(r.status===401&&auth){try{window.dispatchEvent(new CustomEvent('medlife:unauthorized'))}catch{}}
   let message=data?.detail||data?.error||data?.message;if(!message&&typeof data==='object')message=Object.entries(data).map(([k,v])=>`${k}: ${Array.isArray(v)?v.join(', '):typeof v==='string'?v:JSON.stringify(v)}`).join(' | ');throw new ApiError(r.status,message||`Request failed (${r.status}).`)
  }
  return data
 }finally{clearTimeout(timer)}
}
export const checkHealth=()=>call('/health/',{auth:false});
export const signUp=(email,password)=>call('/signup',{method:'POST',body:{email,password},auth:false});
export const signIn=(email,password)=>call('/signin',{method:'POST',body:{email,password},auth:false});
export const googleSignIn=id_token=>call('/google/signin',{method:'POST',body:{id_token},auth:false});
export const verifyTotpSetup=(setup_token,code)=>call('/totp/verify-setup',{method:'POST',body:{setup_token,code},auth:false});
export const verifyTotpLogin=(challenge_token,code)=>call('/totp/verify-login',{method:'POST',body:{challenge_token,code},auth:false});
export const restartTotpSetup=(email,password)=>call('/totp/setup',{method:'POST',body:{email,password},auth:false});
export const forgotPassword=email=>call('/password/forgot',{method:'POST',body:{email},auth:false});
export const googlePasswordSetup=(setup_token,new_password,confirm_password)=>
 call('/google/password-setup',{method:'POST',body:{setup_token,new_password,confirm_password},auth:false});
export const requestTotpRecovery=email=>
 call('/totp/recovery/request',{method:'POST',body:{email},auth:false});
export const setupTotpRecovery=recovery_token=>
 call('/totp/recovery/setup',{method:'POST',body:{recovery_token},auth:false});
export const verifyTotpRecovery=(recovery_token,code)=>
 call('/totp/recovery/verify',{method:'POST',body:{recovery_token,code},auth:false});
//export const resetPassword=(token,new_password)=>call('/password/reset',{method:'POST',body:{token,new_password},auth:false});

export const resetPassword = (token, new_password, confirm_password) =>
  call('/password/reset', {
    method: 'POST',
    body: { token, new_password, confirm_password },
    auth: false,
  });

export const changePassword = (current_password, new_password, confirm_password) =>
  call('/password/change', {
    method: 'POST',
    body: { current_password: current_password || '', new_password, confirm_password },
  }).then(r => {
    if (r.access_token) setAccessToken(r.access_token);
    return r;
  });

export const getAccount=()=>call('/account/');
export const getMembers=()=>call('/getmember');
export const addMember=(_email,member)=>call('/addmember',{method:'POST',body:member});
export const editMember=(_email,name,member)=>call('/editmember',{method:'POST',params:{member_name:name},body:member});
export const removeMember=(_email,name)=>call('/removemember',{method:'POST',params:{member_name:name}});
export const consumeToken=(_email,name)=>call('/tokens/',{params:{member_name:name}}).then(d=>Number(d.message));
export const fetchChat=(_email,name)=>call('/fetchChat/',{params:{member_name:name}}).then(d=>Array.isArray(d.chat)?d.chat:Array.isArray(d)?d:[]);
export const saveChat=(_email,name,chat)=>call('/saveChat/',{method:'POST',params:{member_name:name},body:{chat}});
export const askMemberAI = (member_name, query, provider, model) =>
  call('/chat/ask/', {
    method: 'POST',
    body: {
      member_name,
      query,
      ...(provider ? { provider } : {}),
      ...(model ? { model, local_model: model } : {}),
    },
  });
export const askAI = async (query, provider, model) => {
  const params = {
    query,
    ...(provider ? { provider } : {}),
    ...(model ? { model, local_model: model } : {}),
  };
  const d = await call('/prompt/', { params });
  return typeof d === 'string' ? d : (d.answer || d.response || JSON.stringify(d));
};
export const getAIProviders = () => call('/providers/');
export const isCloudAiProvider = (providerId) => {
  const p = (providerId || '').toLowerCase().trim();
  return ['gemini', 'claude', 'openai', 'chatgpt', 'openai_compatible'].includes(p);
};
export const getCloudAiConsent = async ({ force = false } = {}) => {
  if (!force && consentCache !== null) {
    return consentCache;
  }
  if (inFlightConsent) {
    return inFlightConsent;
  }
  inFlightConsent = (async () => {
    try {
      const data = await call('/account/cloud-ai-consent');
      consentCache = {
        consent: Boolean(data?.cloud_ai_consent),
        consentAt: data?.cloud_ai_consent_at || null,
      };
      return consentCache;
    } finally {
      inFlightConsent = null;
    }
  })();
  return inFlightConsent;
};
export const setCloudAiConsent = async (consent) => {
  const data = await call('/account/cloud-ai-consent', {
    method: 'POST',
    body: { consent: Boolean(consent) },
  });
  consentCache = {
    consent: Boolean(data?.cloud_ai_consent),
    consentAt: data?.cloud_ai_consent_at || null,
  };
  return consentCache;
};
export const scanDocument = (image, documentType, member_name) => {
  const body = new FormData();
  body.append('image', image);
  body.append('documentType', documentType);
  body.append('member_name', member_name);
  return call('/documents/scan/', { method: 'POST', body, formData: true });
};
export const listDocuments = (member_name) => call('/documents/', { params: { member_name } });
export const getDocument = (id) => call(`/documents/${id}/`);
export const updateDocument = (id, body) => call(`/documents/${id}/`, { method: 'PATCH', body });
export const deleteDocument = (id) => call(`/documents/${id}/`, { method: 'DELETE' });

// Doctor System API methods
export const getPublicDoctors = (specialty) =>
  call('/doctors/', { params: specialty ? { specialty } : {}, auth: false });

export const getDoctorProfile = () => call('/doctor/profile/');

export const updateDoctorProfile = (data) =>
  call('/doctor/profile/', { method: 'PATCH', body: data });

export const submitDoctorApplication = (data) => {
  const isFormData = typeof FormData !== 'undefined' && data instanceof FormData;
  return call('/doctor/applications/', {
    method: 'POST',
    body: data,
    formData: isFormData,
    auth: false,
  });
};

export const activateDoctorAccount = ({ token, action = 'setup', password, confirm_password, code }) =>
  call('/doctor/activate-account/', {
    method: 'POST',
    body: {
      token,
      action,
      ...(password !== undefined ? { password } : {}),
      ...(confirm_password !== undefined ? { confirm_password } : {}),
      ...(code !== undefined ? { code } : {}),
    },
    auth: false,
  });

export const downloadAdminApplicationDocument = async (documentId, suggestedFilename = 'document') => {
  const token = getAccessToken();
  const res = await fetch(`${BASE}/doctor/admin/applications/documents/${documentId}/`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!res.ok) {
    let msg = 'Failed to download document.';
    try {
      const errJson = await res.json();
      msg = errJson.detail || errJson.error || msg;
    } catch {}
    throw new Error(msg);
  }
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  const disp = res.headers.get('Content-Disposition') || '';
  const match = disp.match(/filename="?([^";]+)"?/);
  link.download = match ? match[1] : suggestedFilename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

export const getMyDoctorApplication = () =>
  call('/doctor/applications/me/');

export const getAdminApplications = (status = 'pending') =>
  call('/doctor/admin/applications/', { params: status && status !== 'all' ? { status } : (status === 'all' ? { status: 'all' } : {}) });

export const reviewDoctorApplication = (applicationId, decision, review_note = '') =>
  call(`/doctor/admin/applications/${applicationId}/review/`, {
    method: 'POST',
    body: { decision, review_note },
  });

export const getAdminDashboardOverview = () =>
  call('/doctor/admin/dashboard/');

export const getAdminDoctors = (params = {}) =>
  call('/doctor/admin/doctors/', { params });

export const manageAdminDoctor = (doctor_id, action, reason = '') =>
  call('/doctor/admin/doctors/', {
    method: 'POST',
    body: { doctor_id, action, reason },
  });

export const getAdminAvailability = (params = {}) =>
  call('/doctor/admin/availability/', { params });

export const setAdminDoctorAvailability = (doctor_id, is_available, reason = '') =>
  call('/doctor/admin/availability/', {
    method: 'POST',
    body: {
      action: 'set_doctor_availability',
      doctor_id: Number(doctor_id),
      is_available: Boolean(is_available),
      ...(reason ? { reason } : {}),
    },
  });

export const setAdminSlotActive = (doctor_id, slot_id, is_active, reason = '') =>
  call('/doctor/admin/availability/', {
    method: 'POST',
    body: {
      action: 'set_slot_active',
      doctor_id: Number(doctor_id),
      slot_id: Number(slot_id),
      is_active: Boolean(is_active),
      ...(reason ? { reason } : {}),
    },
  });

export const getAdminPatients = (params = {}) =>
  call('/doctor/admin/patients/', { params });

export const getAdminAnalytics = () =>
  call('/doctor/admin/analytics/');

export const getAdminAuditLog = (params = {}) =>
  call('/doctor/admin/audit-log/', { params });

export const getAdminAppointmentHistory = (appointmentId) =>
  call(`/doctor/admin/appointments/${appointmentId}/history/`);

export const getAdminAppointments = (params = {}) =>
  call('/doctor/appointments/', {
    params: { role: 'admin', ...params },
  });

export const bookAdminAppointment = (data) =>
  call('/doctor/appointments/', { method: 'POST', body: data });

export const getAdminInvitations = () =>
  call('/doctor/admin/invitations/');

export const sendDoctorInvitation = (email) =>
  call('/doctor/admin/invitations/', { method: 'POST', body: { email } });

export const acceptDoctorInvitation = (data) =>
  call('/doctor/invitations/accept/', { method: 'POST', body: data, auth: false });

export const getAccessGrants = () =>
  call('/doctor/access-grants/');

export const createAccessGrant = (member_id, doctor_id, scopes) =>
  call('/doctor/access-grants/', {
    method: 'POST',
    body: { member_id, doctor_id, scopes },
  });

export const revokeAccessGrant = (grantId) =>
  call(`/doctor/access-grants/${grantId}/revoke/`, { method: 'POST' });

export const getSharedRecords = (memberId) =>
  call(`/doctor/shared-records/${memberId}/`);

export const getDoctorDashboardOverview = () =>
  call('/doctor/dashboard/');

export const getDoctorPatients = () =>
  call('/doctor/patients/');

export const getDoctorAvailability = () =>
  call('/doctor/availability/');

export const createDoctorAvailabilitySlot = ({ weekday, start_time, end_time }) =>
  call('/doctor/availability/', {
    method: 'POST',
    body: { weekday: Number(weekday), start_time, end_time },
  });

export const deleteDoctorAvailabilitySlot = (slotId) =>
  call('/doctor/availability/', {
    method: 'DELETE',
    params: { slot_id: slotId },
  });

export const getAppointments = (role = 'patient', status = '', params = {}) =>
  call('/doctor/appointments/', {
    params: { role, ...(status ? { status } : {}), ...params },
  });

export const requestAppointment = (data) =>
  call('/doctor/appointments/', { method: 'POST', body: data });

export const decideAppointment = (appointmentId, decision, scheduled_at, doctor_response = '') =>
  call(`/doctor/appointments/${appointmentId}/decision/`, {
    method: 'POST',
    body: { decision, scheduled_at, doctor_response },
  });

export const cancelAppointment = (appointmentId, reason = '') =>
  call(`/doctor/appointments/${appointmentId}/cancel/`, {
    method: 'POST',
    body: reason ? { reason } : {},
  });

export const completeAppointment = (appointmentId) =>
  call(`/doctor/appointments/${appointmentId}/complete/`, { method: 'POST' });

export const requestAppointmentReschedule = (appointmentId, proposed_at, reason = '') =>
  call(`/doctor/appointments/${appointmentId}/reschedule/`, {
    method: 'POST',
    body: { proposed_at, reason },
  });

export const getRescheduleRequests = (role = 'doctor', status = '') =>
  call('/doctor/reschedule-requests/', {
    params: { role, ...(status ? { status } : {}) },
  });

export const decideRescheduleRequest = (requestId, decision) =>
  call(`/doctor/reschedule-requests/${requestId}/decision/`, {
    method: 'POST',
    body: { decision },
  });

export const getConsultationNote = (appointmentId) =>
  call(`/doctor/appointments/${appointmentId}/notes/`);

export const saveConsultationNote = (appointmentId, payload) => {
  const body = typeof payload === 'string' ? { content: payload, action: 'save' } : payload;
  return call(`/doctor/appointments/${appointmentId}/notes/`, {
    method: 'POST',
    body,
  });
};

export const getConsultationNoteRevisions = (appointmentId) =>
  call(`/doctor/appointments/${appointmentId}/notes/revisions/`);

export const downloadConsultationSummary = async (
  appointmentId,
  suggestedFilename = `medlife-consultation-${appointmentId}.txt`
) => {
  const token = getAccessToken();
  const endpointUrl = new URL(
    `${BASE}/doctor/appointments/${appointmentId}/summary/`,
    window.location.href
  );
  const res = await fetch(endpointUrl, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!res.ok) {
    let msg = 'Failed to download consultation summary.';
    try {
      const errJson = await res.json();
      msg = errJson.detail || errJson.error || msg;
    } catch {}
    throw new Error(msg);
  }
  const blob = await res.blob();
  const blobUrl = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = blobUrl;
  const disp = res.headers.get('Content-Disposition') || '';
  const match = disp.match(/filename="?([^";]+)"?/);
  link.download = match ? match[1] : suggestedFilename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(blobUrl);
};

export const getChatRequests = (role = 'patient', status = '') =>
  call('/doctor/chat-requests/', {
    params: { role, ...(status ? { status } : {}) },
  });

export const requestChat = (data) =>
  call('/doctor/chat-requests/', { method: 'POST', body: data });

export const decideChatRequest = (chatRequestId, decision) =>
  call(`/doctor/chat-requests/${chatRequestId}/decision/`, {
    method: 'POST',
    body: { decision },
  });

export const cancelChatRequest = (chatRequestId) =>
  call(`/doctor/chat-requests/${chatRequestId}/cancel/`, { method: 'POST' });

export const closeChatRequest = (chatRequestId) =>
  call(`/doctor/chat-requests/${chatRequestId}/close/`, { method: 'POST' });

export const getChatMessages = (chatRequestId) =>
  call(`/doctor/chat-requests/${chatRequestId}/messages/`);

export const sendChatMessage = (chatRequestId, text) =>
  call(`/doctor/chat-requests/${chatRequestId}/messages/`, {
    method: 'POST',
    body: { text },
  });

export const getDoctorNotifications = (unreadOnly = false) =>
  call('/doctor/notifications/', {
    params: unreadOnly ? { unread: 'true' } : {},
  });

export const markDoctorNotificationRead = (notificationId) =>
  call(`/doctor/notifications/${notificationId}/read/`, { method: 'POST' });

