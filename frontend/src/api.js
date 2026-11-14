const API_BASE = import.meta.env.VITE_API_URL ?? ''
const TOKEN_KEY = 'nightcare_token'

export const getToken = () => sessionStorage.getItem(TOKEN_KEY)
export const setToken = (token) => sessionStorage.setItem(TOKEN_KEY, token)
export const clearToken = () => sessionStorage.removeItem(TOKEN_KEY)

export class AuthError extends Error {}

async function request(path, options = {}) {
  const token = getToken()
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  })
  if (res.status === 401) {
    clearToken()
    throw new AuthError('Please sign in')
  }
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText}`)
  }
  return res.json()
}

export const api = {
  login: (username, password) =>
    request('/api/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) }),
  rooms: () => request('/api/rooms'),
  readings: (minutes = 10) => request(`/api/readings?minutes=${minutes}`),
  alarms: (activeOnly = false) => request(`/api/alarms?active_only=${activeOnly}`),
  acknowledge: (id) => request(`/api/alarms/${id}/acknowledge`, { method: 'POST' }),
  setHeater: (roomId, on) =>
    request(`/api/rooms/${roomId}/heater`, { method: 'POST', body: JSON.stringify({ on }) }),
  simulate: (roomId, changes) =>
    request(`/api/rooms/${roomId}/simulate`, { method: 'POST', body: JSON.stringify(changes) }),
}