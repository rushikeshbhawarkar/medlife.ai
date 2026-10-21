/** Tiny hash router hook.
 * Edit this file when changing route parsing or route-change behavior.

import {useEffect,useState} from 'react';
export function useHashRoute(){const read=()=>{const raw=window.location.hash.replace(/^#\/?/,'');return raw||'/'};const [route,setRoute]=useState(read);useEffect(()=>{const change=()=>{setRoute(read());window.scrollTo({top:0,behavior:'auto'})};window.addEventListener('hashchange',change);if(!window.location.hash)window.location.hash='#/';return()=>window.removeEventListener('hashchange',change)},[]);return route}
 */


import { useEffect, useState } from 'react';

export function useHashRoute() {
  const read = () => {
    const raw = window.location.hash.replace(/^#\/?/, '');
    const route = raw.split('#')[0].split('?')[0];
    return route || '/';
  };

  const [route, setRoute] = useState(read);

  useEffect(() => {
    const change = () => {
      setRoute(read());
      window.scrollTo({ top: 0, behavior: 'auto' });
    };

    window.addEventListener('hashchange', change);

    if (!window.location.hash) {
      window.location.hash = '#/';
    }

    return () => window.removeEventListener('hashchange', change);
  }, []);

  return route;
}