import { useState } from 'react'
import { api, setToken } from './api'

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      const data = await api.login(username, password)
      setToken(data.access_token)
      onLogin()
      } catch (err) {
      setError(
        err.message.startsWith('429')
          ? 'Too many failed attempts. Please wait 5 minutes.'
          : 'Invalid username or password',
      )
    }
  }

  return (
    <div className="login-page">
      <form className="panel login" onSubmit={handleSubmit}>
        <h1>Night Care Room Monitor</h1>
        <label>
          Username
          <input value={username} onChange={(e) => setUsername(e.target.value)}
            autoComplete="username" required />
        </label>
        <label>
          Password
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password" required />
        </label>
        {error && <p className="form-error">{error}</p>}
        <button type="submit" disabled={busy}>{busy ? 'Signing in...' : 'Sign in'}</button>
      </form>
    </div>
  )
}