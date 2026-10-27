// /** DashboardPage component.
//  * Edit this file when changing this component behavior or markup.
//  */
// import {useCallback,useEffect,useMemo,useState} from 'react';import {Menu,Sun,Moon} from 'lucide-react';import Sidebar from '../../features/dashboard/Sidebar/index.js';import ProfileHeader from '../../features/dashboard/ProfileHeader/index.js';import HealthTiles from '../../features/dashboard/HealthTiles/index.js';import MedicinesList from '../../features/dashboard/MedicinesList/index.js';import MemberForm from '../../features/dashboard/MemberForm/index.js';import ConfirmRemoveModal from '../../features/dashboard/ConfirmRemoveModal/index.js';import OnboardingEmpty from '../../features/dashboard/OnboardingEmpty/index.js';import Chat from '../../features/chat/Chat/index.js';import Spinner from '../../components/Spinner/index.js';import Banner from '../../components/Banner/index.js';import {getMembers,addMember,editMember,removeMember} from '../../services/api.js';import './DashboardPage.css';import TextScanner from '../../features/dashboard/TextScanner.jsx';
// export default function DashboardPage({email,onSignOut}){const [members,setMembers]=useState({}),[loading,setLoading]=useState(true),[loadError,setLoadError]=useState(''),[selected,setSelected]=useState(''),[form,setForm]=useState(null),[confirmRemove,setConfirmRemove]=useState(false),[drawer,setDrawer]=useState(false);const [theme,setTheme]=useState(()=>localStorage.getItem('medlife_theme')||document.documentElement.getAttribute('data-theme')||'dark');const [palette,setPalette]=useState(()=>localStorage.getItem('medlife_palette')||'red');useEffect(()=>{document.documentElement.setAttribute('data-palette',palette);localStorage.setItem('medlife_palette',palette)},[palette]);const toggleTheme=()=>{const next=theme==='dark'?'light':'dark';document.documentElement.setAttribute('data-theme',next);try{localStorage.setItem('medlife_theme',next)}catch{}setTheme(next)};const sorted=useMemo(()=>Object.fromEntries(Object.entries(members).sort((a,b)=>(Number(a[0].match(/\d+/)?.[0])||0)-(Number(b[0].match(/\d+/)?.[0])||0))),[members]);
// const reload=useCallback(async(preferred)=>{setLoading(true);setLoadError('');try{const data=await getMembers(email);setMembers(data||{});const keys=Object.keys(data||{}).sort((a,b)=>(Number(a.match(/\d+/)?.[0])||0)-(Number(b.match(/\d+/)?.[0])||0));setSelected(cur=>preferred&&data?.[preferred]?preferred:cur&&data?.[cur]?cur:keys[0]||'')}catch(e){setLoadError(e.message||'Unable to load profiles.')}finally{setLoading(false)}},[email]);
// useEffect(()=>{reload()},[reload]);const member=sorted[selected];
// async function saveForm(value){if(form.mode==='edit'){await editMember(email,form.name,value);await reload(form.name)}else{const result=await addMember(email,value);await reload(result?.key)}setForm(null)}
// async function doRemove(){try{await removeMember(email,selected);setConfirmRemove(false);setSelected('');await reload()}catch(e){setLoadError(e.message||'Unable to remove profile.');setConfirmRemove(false)}}
// const onTokens=useCallback((name,count)=>setMembers(p=>({...p,[name]:{...p[name],tokens:count}})),[]);
// return <div className="dashboard-layout"><Sidebar email={email} members={sorted} selected={selected} onSelect={setSelected} onAdd={()=>setForm({mode:'add'})} onSignOut={onSignOut} open={drawer} onClose={()=>setDrawer(false)}/><main className="dashboard-main"><div className="dashboard-topbar"><button className="dashboard-menu" aria-label="Open family profiles" onClick={()=>setDrawer(true)}><Menu/></button><h1>Health dashboard</h1><button className="theme-toggle" aria-label={theme==='dark'?'Switch to light mode':'Switch to dark mode'} title={theme==='dark'?'Switch to light mode':'Switch to dark mode'} onClick={toggleTheme}>{theme==='dark'?<Sun size={18}/>:<Moon size={18}/>}</button><select className="palette-select" aria-label="Choose accent colour" value={palette} onChange={e=>setPalette(e.target.value)}><option value="red">Red theme</option><option value="green">Medical green</option></select></div><div className="dashboard-content">{loadError&&<Banner variant="error">{loadError}</Banner>}{loading?<Spinner/>:!Object.keys(sorted).length?<OnboardingEmpty onAdd={()=>setForm({mode:'add'})}/>:member?<><ProfileHeader member={member} index={Number(selected.match(/\d+/)?.[0]||1)-1} onEdit={()=>setForm({mode:'edit',name:selected,member})} onRemove={()=>setConfirmRemove(true)}/><HealthTiles member={member}/><MedicinesList medicine={member.medicine}/><TextScanner memberName={selected}/><Chat key={selected} email={email} memberName={selected} member={member} onTokens={onTokens}/></>:null}</div></main>{form&&<MemberForm mode={form.mode} member={form.member||{}} onClose={()=>setForm(null)} onSave={saveForm}/ >}{confirmRemove&&member&&<ConfirmRemoveModal member={member} onClose={()=>setConfirmRemove(false)} onConfirm={doRemove}/>}</div>}





/** DashboardPage component.
 * Edit this file when changing this component behavior or markup.
 */
import { useCallback, useEffect, useMemo, useState } from 'react';
import { Menu, Sun, Moon } from 'lucide-react';
import Sidebar from '../../features/dashboard/Sidebar/index.js';
import ProfileHeader from '../../features/dashboard/ProfileHeader/index.js';
import HealthTiles from '../../features/dashboard/HealthTiles/index.js';
import MedicinesList from '../../features/dashboard/MedicinesList/index.js';
import MemberForm from '../../features/dashboard/MemberForm/index.js';
import ConfirmRemoveModal from '../../features/dashboard/ConfirmRemoveModal/index.js';
import OnboardingEmpty from '../../features/dashboard/OnboardingEmpty/index.js';
import Chat from '../../features/chat/Chat/index.js';
import Spinner from '../../components/Spinner/index.js';
import Banner from '../../components/Banner/index.js';
import {
  getAccount,
  getMembers,
  addMember,
  editMember,
  removeMember,
  getMyDoctorApplication,
  getAdminApplications,
} from '../../services/api.js';
import PatientConsultationView from '../../features/doctor/PatientConsultationView.jsx';
import DoctorWorkspaceView from '../../features/doctor/DoctorWorkspaceView.jsx';
import AdminPortalView from '../../features/doctor/AdminPortalView.jsx';
import NotificationsDropdown from '../../features/doctor/NotificationsDropdown.jsx';
import './DashboardPage.css';
import TextScanner from '../../features/dashboard/TextScanner.jsx';

export default function DashboardPage({ email, onSignOut }) {
  const [members, setMembers] = useState({});
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState('');
  const [selected, setSelected] = useState('');
  const [form, setForm] = useState(null);
  const [confirmRemove, setConfirmRemove] = useState(false);
  const [drawer, setDrawer] = useState(false);

  // User identity & role state: 'super_admin' | 'doctor' | 'patient'
  const [accountRole, setAccountRole] = useState('patient');
  const [adminTab, setAdminTab] = useState('overview');
  const [doctorTab, setDoctorTab] = useState('overview');

  // View state: 'health' | 'consultation' | 'doctor_workspace' | 'admin_portal'
  const [currentView, setCurrentView] = useState('health');
  const [hasDoctorProfile, setHasDoctorProfile] = useState(false);
  const [isStaff, setIsStaff] = useState(false);
  const [applicationStatus, setApplicationStatus] = useState(null);

  // Targets from notifications
  const [targetAppointmentId, setTargetAppointmentId] = useState(null);
  const [targetChatId, setTargetChatId] = useState(null);

  const [theme, setTheme] = useState(
    () => localStorage.getItem('medlife_theme') || document.documentElement.getAttribute('data-theme') || 'dark'
  );
  const [palette, setPalette] = useState(
    () => localStorage.getItem('medlife_palette') || document.documentElement.getAttribute('data-palette') || 'red'
  );

  useEffect(() => {
    document.documentElement.setAttribute('data-palette', palette);
    try {
      localStorage.setItem('medlife_palette', palette);
    } catch {}
  }, [palette]);

  const toggleTheme = () => {
    const next = theme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    try {
      localStorage.setItem('medlife_theme', next);
    } catch {}
    setTheme(next);
  };

  const sorted = useMemo(
    () =>
      Object.fromEntries(
        Object.entries(members).sort(
          (a, b) => (Number(a[0].match(/\d+/)?.[0]) || 0) - (Number(b[0].match(/\d+/)?.[0]) || 0)
        )
      ),
    [members]
  );

  // Reload family members (patient-only)
  const reloadMembers = useCallback(async (preferred) => {
    setLoading(true);
    setLoadError('');
    try {
      const data = await getMembers();
      setMembers(data || {});
      const keys = Object.keys(data || {}).sort(
        (a, b) => (Number(a.match(/\d+/)?.[0]) || 0) - (Number(b.match(/\d+/)?.[0]) || 0)
      );
      setSelected((cur) => (preferred && data?.[preferred] ? preferred : cur && data?.[cur] ? cur : keys[0] || ''));
    } catch (e) {
      setLoadError(e.message || 'Unable to load profiles.');
    } finally {
      setLoading(false);
    }
  }, []);

  // Initialize current user identity from backend
  const initUser = useCallback(async () => {
    setLoading(true);
    setLoadError('');
    try {
      const acc = await getAccount();
      const role = acc?.role || 'patient';
      const dash = acc?.dashboard || 'patient';
      setAccountRole(role);

      if (dash === 'admin' || role === 'super_admin') {
        setCurrentView('admin_portal');
        setIsStaff(true);
        setHasDoctorProfile(false);
        setLoading(false);
      } else if (dash === 'doctor' || role === 'doctor') {
        setCurrentView('doctor_workspace');
        setHasDoctorProfile(true);
        setIsStaff(false);
        setLoading(false);
      } else {
        // Patient role
        setIsStaff(false);
        setHasDoctorProfile(false);
        if (acc?.doctor_status) {
          setApplicationStatus(acc.doctor_status);
        }
        // Load members strictly for patients
        try {
          const data = await getMembers();
          setMembers(data || {});
          const keys = Object.keys(data || {}).sort(
            (a, b) => (Number(a.match(/\d+/)?.[0]) || 0) - (Number(b.match(/\d+/)?.[0]) || 0)
          );
          setSelected((cur) => (cur && data?.[cur] ? cur : keys[0] || ''));
        } catch (memErr) {
          setLoadError(memErr.message || 'Unable to load profiles.');
        } finally {
          setLoading(false);
        }
      }
    } catch (e) {
      if (e?.status === 401) return;
      setLoadError(e.message || 'Unable to load account identity.');
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    initUser();
  }, [initUser]);

  const member = sorted[selected];

  async function saveForm(value) {
    if (form.mode === 'edit') {
      await editMember(email, form.name, value);
      await reloadMembers(form.name);
    } else {
      const result = await addMember(email, value);
      await reloadMembers(result?.key);
    }
    setForm(null);
  }

  async function doRemove() {
    try {
      await removeMember(email, selected);
      setConfirmRemove(false);
      setSelected('');
      await reloadMembers();
    } catch (e) {
      setLoadError(e.message || 'Unable to remove profile.');
      setConfirmRemove(false);
    }
  }

  const onTokens = useCallback(
    (name, count) => setMembers((p) => ({ ...p, [name]: { ...p[name], tokens: count } })),
    []
  );

  const handleSelectNotification = (notif) => {
    if (notif.appointment_id) {
      setTargetAppointmentId(notif.appointment_id);
      if (hasDoctorProfile && currentView === 'doctor_workspace') {
        setCurrentView('doctor_workspace');
      } else {
        setCurrentView('consultation');
      }
    } else if (notif.chat_request_id) {
      setTargetChatId(notif.chat_request_id);
      if (hasDoctorProfile && currentView === 'doctor_workspace') {
        setCurrentView('doctor_workspace');
      } else {
        setCurrentView('consultation');
      }
    }
  };

  const viewTitle =
    currentView === 'consultation'
      ? 'Doctor Consultation'
      : currentView === 'doctor_workspace'
      ? 'Doctor Clinical Workspace'
      : currentView === 'admin_portal'
      ? 'Medical Administration'
      : 'Health dashboard';

  return (
    <div className="dashboard-layout">
      <Sidebar
        email={email}
        userRole={accountRole}
        members={sorted}
        selected={selected}
        onSelect={(key) => {
          setSelected(key);
          setCurrentView('health');
        }}
        onAdd={() => setForm({ mode: 'add' })}
        onSignOut={onSignOut}
        open={drawer}
        onClose={() => setDrawer(false)}
        currentView={currentView}
        onSelectView={setCurrentView}
        adminTab={adminTab}
        onSelectAdminTab={(tab) => {
          setAdminTab(tab);
          setCurrentView('admin_portal');
        }}
        doctorTab={doctorTab}
        onSelectDoctorTab={(tab) => {
          setDoctorTab(tab);
          setCurrentView('doctor_workspace');
        }}
        hasDoctorProfile={hasDoctorProfile}
        isStaff={isStaff}
        applicationStatus={applicationStatus}
        onOpenDoctorApp={() => setShowDoctorAppModal(true)}
      />

      <main className="dashboard-main">
        <div className="dashboard-topbar">
          <button className="dashboard-menu" aria-label="Open family profiles" onClick={() => setDrawer(true)}>
            <Menu />
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: 0, flexWrap: 'wrap' }}>
            <h1>{viewTitle}</h1>
            {accountRole && (
              <span className={`role-badge role-badge-${accountRole}`}>
                {accountRole === 'super_admin' ? 'Super Admin' : accountRole === 'doctor' ? 'Doctor' : 'Patient'}
              </span>
            )}
          </div>

          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <NotificationsDropdown onSelectNotification={handleSelectNotification} />

            <button
              className="theme-toggle"
              aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
              title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
              onClick={toggleTheme}
            >
              {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
            </button>

            <select
              className="palette-select"
              aria-label="Choose accent colour"
              value={palette}
              onChange={(e) => setPalette(e.target.value)}
            >
              <option value="red">Red theme</option>
              <option value="green">Medical green</option>
            </select>
          </div>
        </div>

        <div className="dashboard-content">
          {loadError && <Banner variant="error">{loadError}</Banner>}

          {/* VIEW: CONSULT A DOCTOR (Patient) */}
          {currentView === 'consultation' && (
            <PatientConsultationView
              email={email}
              members={sorted}
              selectedMemberKey={selected}
              targetAppointmentId={targetAppointmentId}
              targetChatId={targetChatId}
            />
          )}

          {/* VIEW: DOCTOR WORKSPACE (Doctor) */}
          {currentView === 'doctor_workspace' && (
            <DoctorWorkspaceView email={email} initialTab={doctorTab} />
          )}

          {/* VIEW: ADMIN PORTAL (Staff) */}
          {currentView === 'admin_portal' && (
            <AdminPortalView email={email} initialTab={adminTab} onTabChange={setAdminTab} />
          )}

          {/* VIEW: FAMILY HEALTH DASHBOARD (Default) */}
          {currentView === 'health' && (
            loading ? (
              <Spinner />
            ) : !Object.keys(sorted).length ? (
              <OnboardingEmpty onAdd={() => setForm({ mode: 'add' })} />
            ) : member ? (
              <>
                <ProfileHeader
                  member={member}
                  index={Number(selected.match(/\d+/)?.[0] || 1) - 1}
                  onEdit={() => setForm({ mode: 'edit', name: selected, member })}
                  onRemove={() => setConfirmRemove(true)}
                />
                <HealthTiles member={member} />
                <MedicinesList medicine={member.medicine} medicalDescription={member.medicalDescription} />
                <TextScanner memberName={selected} />
                <Chat
                  key={selected}
                  email={email}
                  memberName={selected}
                  member={member}
                  onTokens={onTokens}
                />
              </>
            ) : null
          )}
        </div>
      </main>

      {form && (
        <MemberForm
          mode={form.mode}
          member={form.member || {}}
          onClose={() => setForm(null)}
          onSave={saveForm}
        />
      )}

      {confirmRemove && member && (
        <ConfirmRemoveModal
          member={member}
          onClose={() => setConfirmRemove(false)}
          onConfirm={doRemove}
        />
      )}
    </div>
  );
}