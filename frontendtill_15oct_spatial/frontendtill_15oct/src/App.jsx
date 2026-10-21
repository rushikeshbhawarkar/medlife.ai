// import {useCallback,useEffect,useState} from 'react';
// import {EMAIL_KEY} from './data/siteConfig.js';
// import {routes} from './router/routes.js';
// import {useHashRoute} from './router/useHashRoute.js';
// import PublicLayout from './layout/PublicLayout/index.js';
// import SignInModal from './features/auth/SignInModal/index.js';
// import DashboardPage from './pages/DashboardPage/index.js';
// import {setAccessToken} from './services/api.js';
// function readEmail(){try{return localStorage.getItem(EMAIL_KEY)||''}catch{return ''}}
// export default function App(){const route=useHashRoute();useEffect(()=>{const theme=localStorage.getItem('medlife_theme');if(theme)document.documentElement.setAttribute('data-theme',theme);const palette=localStorage.getItem('medlife_palette');if(palette)document.documentElement.setAttribute('data-palette',palette)},[]);const [email,setEmail]=useState(readEmail),[showSignIn,setShowSignIn]=useState(false);const signIn=useCallback(value=>{try{localStorage.setItem(EMAIL_KEY,value)}catch{}setEmail(value);setShowSignIn(false);window.scrollTo({top:0,behavior:'auto'})},[]);const signOut=useCallback(()=>{try{localStorage.removeItem(EMAIL_KEY)}catch{}setAccessToken('');setEmail('')},[]);if(email)return <DashboardPage email={email} onSignOut={signOut}/>;const Page=routes[route]||routes['/'];return <><PublicLayout route={route} onSignIn={()=>setShowSignIn(true)}><Page onSignIn={()=>setShowSignIn(true)}/></PublicLayout>{showSignIn&&<SignInModal onClose={()=>setShowSignIn(false)} onSignIn={signIn}/>}</>}



import { useCallback, useEffect, useState } from 'react';
import { EMAIL_KEY } from './data/siteConfig.js';
import { routes } from './router/routes.js';
import { useHashRoute } from './router/useHashRoute.js';
import PublicLayout from './layout/PublicLayout/index.js';
import SignInModal from './features/auth/SignInModal/index.js';
import ResetPasswordPage from './features/auth/ResetPasswordPage.jsx';
import RecoverTotpPage from './features/auth/RecoverTotpPage.jsx';
import DoctorInvitationPage from './features/doctor/DoctorInvitationPage.jsx';
import DoctorApplicationPage from './features/doctor/DoctorApplicationPage.jsx';
import DoctorActivationPage from './features/doctor/DoctorActivationPage.jsx';
import DashboardPage from './pages/DashboardPage/index.js';
import { setAccessToken } from './services/api.js';

function readEmail() {
  try {
    return localStorage.getItem(EMAIL_KEY) || '';
  } catch {
    return '';
  }
}

export default function App() {
  const route = useHashRoute();

  useEffect(() => {
    const theme = localStorage.getItem('medlife_theme');
    if (theme) document.documentElement.setAttribute('data-theme', theme);

    const palette = localStorage.getItem('medlife_palette');
    if (palette) document.documentElement.setAttribute('data-palette', palette);
  }, []);

  const [email, setEmail] = useState(readEmail);
  const [showSignIn, setShowSignIn] = useState(false);

  const signIn = useCallback(value => {
    try {
      localStorage.setItem(EMAIL_KEY, value);
    } catch {}

    setEmail(value);
    setShowSignIn(false);
    window.scrollTo({ top: 0, behavior: 'auto' });
  }, []);

  const signOut = useCallback(() => {
    try {
      localStorage.removeItem(EMAIL_KEY);
    } catch {}

    setAccessToken('');
    setEmail('');
  }, []);

  useEffect(() => {
    const handleUnauthorized = () => {
      signOut();
    };
    window.addEventListener('medlife:unauthorized', handleUnauthorized);
    return () => window.removeEventListener('medlife:unauthorized', handleUnauthorized);
  }, [signOut]);

  const isSignInRoute = route === 'signin' || route === 'login';
  const isDoctorApplyRoute =
    !isSignInRoute &&
    (window.location.pathname.replace(/\/+$/, '') === '/apply-doctor' ||
      route === 'apply-doctor' ||
      route === 'doctor-apply' ||
      decodeURIComponent(window.location.hash).includes('apply-doctor') ||
      decodeURIComponent(window.location.hash).includes('doctor-apply'));

  if (isDoctorApplyRoute) {
    return (
      <DoctorApplicationPage
        onReturnToSignIn={() => {
          window.location.hash = '#/signin';
          setShowSignIn(true);
        }}
      />
    );
  }

  // Doctor account activation page after admin approval (#/doctor-activate#token=...)
  const isDoctorActivationRoute =
    !isSignInRoute &&
    (window.location.pathname.replace(/\/+$/, '') === '/doctor-activate' ||
      route === 'doctor-activate' ||
      decodeURIComponent(window.location.hash).includes('doctor-activate') ||
      decodeURIComponent(window.location.hash).startsWith('#/doctor-activate'));

  if (isDoctorActivationRoute) {
    return (
      <DoctorActivationPage
        onReturnToSignIn={() => {
          window.location.hash = '#/signin';
          setShowSignIn(true);
        }}
      />
    );
  }

  // Password-reset links must work even if a previous session exists.
  const isResetPasswordRoute =
    !isSignInRoute &&
    (window.location.pathname.replace(/\/+$/, '') === '/reset-password' ||
      route === 'reset-password' ||
      decodeURIComponent(window.location.hash).startsWith('#/reset-password#token='));

  if (isResetPasswordRoute) {
    return (
      <ResetPasswordPage
        onReturnToSignIn={() => {
          window.location.hash = '#/signin';
          setShowSignIn(true);
        }}
      />
    );
  }

  // Authenticator recovery links must work even if a previous session exists.
  const isRecoverTotpRoute =
    !isSignInRoute &&
    (window.location.pathname.replace(/\/+$/, '') === '/recover-totp' ||
      route === 'recover-totp' ||
      decodeURIComponent(window.location.hash).includes('recover-totp') ||
      decodeURIComponent(window.location.hash).startsWith('#/recover-totp'));

  if (isRecoverTotpRoute) {
    return (
      <RecoverTotpPage
        onReturnToSignIn={() => {
          window.location.hash = '#/signin';
          setShowSignIn(true);
        }}
      />
    );
  }

  // Doctor onboarding invitation links
  const isDoctorInvitationRoute =
    !isSignInRoute &&
    (window.location.pathname.replace(/\/+$/, '') === '/doctor-invitation' ||
      route === 'doctor-invitation' ||
      decodeURIComponent(window.location.hash).includes('doctor-invitation') ||
      decodeURIComponent(window.location.hash).startsWith('#/doctor-invitation'));

  if (isDoctorInvitationRoute) {
    return (
      <DoctorInvitationPage
        email={email}
        onReturnToSignIn={() => {
          window.location.hash = '#/signin';
          setShowSignIn(true);
        }}
      />
    );
  }

  if (email) {
    return <DashboardPage email={email} onSignOut={signOut} />;
  }

  const Page = routes[route] || routes['/'];

  return (
    <>
      <PublicLayout
        route={route}
        onSignIn={() => setShowSignIn(true)}
      >
        <Page onSignIn={() => setShowSignIn(true)} />
      </PublicLayout>

      {(showSignIn || isSignInRoute) && (
        <SignInModal
          onClose={() => {
            setShowSignIn(false);
            if (isSignInRoute) {
              window.location.hash = '#/';
            }
          }}
          onSignIn={signIn}
        />
      )}
    </>
  );
}