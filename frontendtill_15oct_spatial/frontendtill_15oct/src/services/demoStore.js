
/** Local-storage demo database for profiles and chats.
 * Edit this file when changing sample profile data or demo persistence.
 */

import { DEMO_KEY, MAX_MEMBERS, TOKEN_LIMIT } from '../data/siteConfig.js';
import { ApiError } from './api.js';

function db() {
  try {
    return JSON.parse(
      localStorage.getItem(DEMO_KEY) || '{"members":{},"chats":{}}'
    );
  } catch {
    return { members: {}, chats: {} };
  }
}

function put(data) {
  try {
    localStorage.setItem(DEMO_KEY, JSON.stringify(data));
  } catch (error) {
    console.error('Unable to save demo data:', error);
    throw error;
  }
}

// Initialize an empty member list without adding a default member.
function group(email) {
  const data = db();

  if (!data.members[email]) {
    data.members[email] = {};
    put(data);
  }

  return data;
}

export function demoGetMembers(email) {
  return { ...(group(email).members[email] || {}) };
}

export function demoAddMember(email, member) {
  const data = group(email);
  const members = data.members[email];

  if (Object.keys(members).length >= MAX_MEMBERS) {
    throw new ApiError(400, 'Maximum of 4 members allowed per email.');
  }

  let i = 1;

  while (members[`member${i}`]) {
    i++;
  }

  const key = `member${i}`;

  members[key] = {
    ...member,
    tokens: member.tokens ?? 0
  };

  put(data);

  return { key };
}

export function demoEditMember(email, name, member) {
  const data = group(email);

  if (!data.members[email]?.[name]) {
    throw new ApiError(404, 'Member not found');
  }

  data.members[email][name] = {
    ...member,
    tokens:
      member.tokens ??
      data.members[email][name].tokens ??
      0
  };

  put(data);

  return { ok: true };
}

export function demoRemoveMember(email, name) {
  const data = group(email);

  if (!data.members[email]?.[name]) {
    throw new ApiError(404, 'Member not found');
  }

  delete data.members[email][name];
  delete data.chats[`${email}|${name}`];

  put(data);

  return { ok: true };
}

export function demoConsumeToken(email, name) {
  const data = group(email);
  const member = data.members[email]?.[name];

  if (!member) {
    throw new ApiError(404, 'Member not found');
  }

  if ((member.tokens || 0) >= TOKEN_LIMIT) {
    throw new ApiError(400, 'Question limit exceeded.');
  }

  member.tokens = (member.tokens || 0) + 1;

  put(data);

  return member.tokens;
}

export function demoFetchChat(email, name) {
  return db().chats[`${email}|${name}`] || [];
}

export function demoSaveChat(email, name, chat) {
  const data = db();

  data.chats[`${email}|${name}`] = chat;

  put(data);

  return { ok: true };
}
