import { useState, type FormEvent } from 'react'
import { Navigate, useNavigate } from 'react-router'

import { api } from '../api/client'
import { message } from '../components/message'
import { useAuth } from '../auth/useAuth'

export function SignupPage() {
  const { user, loading, login } = useAuth()
  const navigate = useNavigate()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  if (user) return <Navigate to="/" replace />

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await api('/users', {
        method: 'POST',
        body: JSON.stringify({ email, password, full_name: fullName }),
      })
      await login(email, password)
    } catch (err) {
      setError(message(err))
      setSubmitting(false)
    }
  }

  return (
    <div className="desktop">
      <form className="window login" onSubmit={handleSubmit}>
        <div className="titlebar">
          <span>Mini Jira</span>
          <span>Sign up</span>
        </div>
        <div className="client">
          {loading ? (
            <p>Restoring session…</p>
          ) : (
            <>
              <label className="field">
                Full name
                <input value={fullName} onChange={(e) => setFullName(e.target.value)} required />
              </label>
              <label className="field">
                Email
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </label>
              <label className="field">
                Password
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  minLength={8}
                  required
                />
              </label>
              {error && <p className="error">{error}</p>}
              <div className="buttons">
                <button type="button" onClick={() => navigate('/login')}>
                  Log on
                </button>
                <button type="submit" disabled={submitting}>
                  {submitting ? 'Wait' : 'OK'}
                </button>
              </div>
            </>
          )}
        </div>
      </form>
    </div>
  )
}
