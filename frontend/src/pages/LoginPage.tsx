import { useState, type FormEvent } from 'react'
import { Navigate, useNavigate } from 'react-router'

import { ApiError } from '../api/client'
import { useAuth } from '../auth/useAuth'

export function LoginPage() {
  const { user, loading, login } = useAuth()
  const navigate = useNavigate()
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
      await login(email, password)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not reach the API')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="desktop">
      <form className="window login" onSubmit={handleSubmit}>
        <div className="titlebar">
          <span>Mini Jira</span>
          <span>Log on</span>
        </div>
        <div className="client">
          {loading ? (
            <p>Restoring session…</p>
          ) : (
            <>
              <label className="field">
                User name
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
                <button type="button" onClick={() => navigate('/signup')}>
                  Sign up
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
