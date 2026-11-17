import type { Tokens } from './types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const ACCESS_KEY = 'mini-jira.access_token'
const REFRESH_KEY = 'mini-jira.refresh_token'

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

export function saveTokens(tokens: Pick<Tokens, 'access_token'> & Partial<Tokens>) {
  localStorage.setItem(ACCESS_KEY, tokens.access_token)
  if (tokens.refresh_token) localStorage.setItem(REFRESH_KEY, tokens.refresh_token)
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_KEY)
  localStorage.removeItem(REFRESH_KEY)
}

export function hasTokens() {
  return localStorage.getItem(REFRESH_KEY) !== null
}

// Login failing is a wrong password, not an expired session.
function keepsSession(path: string) {
  return path !== '/auth/login'
}

let onSessionExpired = () => {}

/** AuthProvider registers this so a dead session leaves the signed-in screen. */
export function setSessionExpiredHandler(handler: () => void) {
  onSessionExpired = handler
}

// Several requests can expire at once; they all wait on the same refresh call.
let refreshing: Promise<boolean> | null = null

function refreshAccessToken(): Promise<boolean> {
  const refreshToken = localStorage.getItem(REFRESH_KEY)
  if (!refreshToken) return Promise.resolve(false)
  refreshing ??= fetch(`${API_URL}/api/v1/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken }),
  })
    .then(async (response) => {
      if (!response.ok) return false
      saveTokens(await response.json())
      return true
    })
    .catch(() => false)
    .finally(() => {
      refreshing = null
    })
  return refreshing
}

async function errorMessage(response: Response): Promise<string> {
  try {
    const body = await response.json()
    if (typeof body.detail === 'string') return body.detail
    if (Array.isArray(body.detail)) return body.detail.map((e: { msg: string }) => e.msg).join(', ')
  } catch {
    // Body was not JSON; fall back to the status text.
  }
  return response.statusText || `Request failed (${response.status})`
}

/** Call `/api/v1{path}` with the access token, refreshing it once on a 401. */
export async function api<T>(path: string, init: RequestInit = {}, retry = true): Promise<T> {
  const headers = new Headers(init.headers)
  const token = localStorage.getItem(ACCESS_KEY)
  if (token) headers.set('Authorization', `Bearer ${token}`)
  if (init.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json')

  const response = await fetch(`${API_URL}/api/v1${path}`, { ...init, headers })

  if (response.status === 401 && retry && keepsSession(path) && (await refreshAccessToken())) {
    return api<T>(path, init, false)
  }
  if (!response.ok) {
    if (response.status === 401 && keepsSession(path)) {
      clearTokens()
      onSessionExpired()
    }
    throw new ApiError(response.status, await errorMessage(response))
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}
