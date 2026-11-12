async function request(path, options = {}) {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText}`)
  }
  return res.json()
}

export const api = {
  rooms: () => request('/api/rooms'),
  readings: (minutes = 10) => request(`/api/readings?minutes=${minutes}`),
  alarms: (activeOnly = false) => request(`/api/alarms?active_only=${activeOnly}`),
  acknowledge: (id) => request(`/api/alarms/${id}/acknowledge`, { method: 'POST' }),
  setHeater: (roomId, on) =>
    request(`/api/rooms/${roomId}/heater`, { method: 'POST', body: JSON.stringify({ on }) }),
  simulate: (roomId, changes) =>
    request(`/api/rooms/${roomId}/simulate`, { method: 'POST', body: JSON.stringify(changes) }),
}