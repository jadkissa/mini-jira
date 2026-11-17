import { useEffect, useState, type FormEvent } from 'react'

import { api } from '../api/client'
import type { Member, Project, Task, Team, TeamDetail } from '../api/types'
import { Dialog } from '../components/Dialog'
import { message } from '../components/message'
import { useAuth } from '../auth/useAuth'
import { TaskDialog } from './TaskDialog'

type OpenDialog = 'team' | 'project' | 'task' | 'members' | null

export function DeskPage() {
  const { user, logout } = useAuth()
  const [teams, setTeams] = useState<Team[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [tasks, setTasks] = useState<Task[]>([])
  const [members, setMembers] = useState<Member[]>([])
  const [membersTeamId, setMembersTeamId] = useState<number | null>(null)
  const [loadedProjectId, setLoadedProjectId] = useState<number | null>(null)
  const [pickedTeamId, setPickedTeamId] = useState<number | null>(null)
  const [pickedProjectId, setPickedProjectId] = useState<number | null>(null)
  const [openTaskId, setOpenTaskId] = useState<number | null>(null)
  const [dialog, setDialog] = useState<OpenDialog>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([api<Team[]>('/teams'), api<Project[]>('/projects')])
      .then(([nextTeams, nextProjects]) => {
        setTeams(nextTeams)
        setProjects(nextProjects)
      })
      .catch((err) => setError(message(err)))
  }, [])

  const teamId = teams.some((team) => team.id === pickedTeamId)
    ? pickedTeamId
    : (teams[0]?.id ?? null)
  const teamProjects = projects.filter((project) => project.team_id === teamId)
  const projectId = teamProjects.some((project) => project.id === pickedProjectId)
    ? pickedProjectId
    : (teamProjects[0]?.id ?? null)
  const loadingTasks = projectId !== null && loadedProjectId !== projectId
  const visibleTasks = loadedProjectId === projectId ? tasks : []
  const role = membersTeamId === teamId ? members.find((member) => member.user_id === user?.id)?.role : undefined
  const canManage = Boolean(user?.is_superuser || role === 'owner' || role === 'admin')
  const canDeleteTeam = Boolean(user?.is_superuser || role === 'owner')

  useEffect(() => {
    if (teamId === null) return
    let active = true
    api<TeamDetail>(`/teams/${teamId}`)
      .then((detail) => {
        if (!active) return
        setMembers(detail.members)
        setMembersTeamId(detail.id)
      })
      .catch((err) => {
        if (active) setError(message(err))
      })
    return () => {
      active = false
    }
  }, [teamId])

  useEffect(() => {
    if (projectId === null) return
    let active = true
    const requested = projectId
    api<Task[]>(`/projects/${requested}/tasks`)
      .then((rows) => {
        if (!active) return
        setTasks(rows)
        setLoadedProjectId(requested)
      })
      .catch((err) => {
        if (active) setError(message(err))
      })
    return () => {
      active = false
    }
  }, [projectId])

  async function removeTeam() {
    if (teamId === null) return
    setError(null)
    try {
      await api(`/teams/${teamId}`, { method: 'DELETE' })
      setTeams((rows) => rows.filter((team) => team.id !== teamId))
      setProjects((rows) => rows.filter((project) => project.team_id !== teamId))
    } catch (err) {
      setError(message(err))
    }
  }

  async function removeProject() {
    if (projectId === null) return
    setError(null)
    try {
      await api(`/projects/${projectId}`, { method: 'DELETE' })
      setProjects((rows) => rows.filter((project) => project.id !== projectId))
    } catch (err) {
      setError(message(err))
    }
  }

  const team = teams.find((item) => item.id === teamId)
  const project = projects.find((item) => item.id === projectId)

  return (
    <div className="desktop">
      <div className="window app">
        <div className="titlebar">
          <span>Mini Jira</span>
          <span>{user?.is_superuser ? 'Superuser' : 'User'}</span>
        </div>
        <div className="menubar">
          <button type="button" onClick={logout}>
            Log off
          </button>
        </div>
        <div className="client">
          {error && <p className="error">{error}</p>}
          <div className="panes">
            <div>
              <p className="pane-title">Teams</p>
              <div className="toolbar">
                <button type="button" onClick={() => setDialog('team')}>
                  New
                </button>
                <button type="button" onClick={() => setDialog('members')} disabled={teamId === null}>
                  Members
                </button>
                <button type="button" onClick={removeTeam} disabled={!canDeleteTeam || teamId === null}>
                  Delete
                </button>
              </div>
              <div className="sunken">
                {teams.length === 0 ? (
                  <p className="muted">No teams.</p>
                ) : (
                  <ul className="list">
                    {teams.map((item) => (
                      <li key={item.id}>
                        <button
                          type="button"
                          className={item.id === teamId ? 'selected' : undefined}
                          onClick={() => setPickedTeamId(item.id)}
                        >
                          {item.name}
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
            <div className="column">
              <div>
                <p className="pane-title">Projects{team ? ` — ${team.name}` : ''}</p>
                <div className="toolbar">
                  <button type="button" onClick={() => setDialog('project')} disabled={teamId === null}>
                    New
                  </button>
                  <button type="button" onClick={removeProject} disabled={!canManage || projectId === null}>
                    Delete
                  </button>
                </div>
                <div className="sunken projects">
                  {teamProjects.length === 0 ? (
                    <p className="muted">No projects.</p>
                  ) : (
                    <ul className="list">
                      {teamProjects.map((item) => (
                        <li key={item.id}>
                          <button
                            type="button"
                            className={item.id === projectId ? 'selected' : undefined}
                            onClick={() => setPickedProjectId(item.id)}
                          >
                            {item.name}
                          </button>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
              <div className="column">
                <p className="pane-title">Tasks{project ? ` — ${project.name}` : ''}</p>
                <div className="toolbar">
                  <button type="button" onClick={() => setDialog('task')} disabled={projectId === null}>
                    New
                  </button>
                </div>
                <div className="sunken">
                  {loadingTasks ? (
                    <p className="muted">Loading…</p>
                  ) : visibleTasks.length === 0 ? (
                    <p className="muted">No tasks.</p>
                  ) : (
                    <table className="grid">
                      <thead>
                        <tr>
                          <th>ID</th>
                          <th>Title</th>
                          <th>Status</th>
                          <th>Priority</th>
                          <th>Due</th>
                        </tr>
                      </thead>
                      <tbody>
                        {visibleTasks.map((task) => (
                          <tr key={task.id} onClick={() => setOpenTaskId(task.id)}>
                            <td>{task.id}</td>
                            <td>{task.title}</td>
                            <td>{task.status.replace('_', ' ')}</td>
                            <td>{task.priority}</td>
                            <td>{task.delivery_date ?? ''}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="statusbar">
          <span>
            {user?.full_name}
            {role ? ` — ${role}` : ''}
          </span>
          <span>
            {teams.length} teams, {visibleTasks.length} tasks
          </span>
        </div>
      </div>
      {dialog === 'team' && (
        <NameDialog
          title="New team"
          label="Name"
          onClose={() => setDialog(null)}
          onSubmit={async (name) => {
            const created = await api<Team>('/teams', {
              method: 'POST',
              body: JSON.stringify({ name }),
            })
            setTeams((rows) => [...rows, created])
            setPickedTeamId(created.id)
          }}
        />
      )}
      {dialog === 'project' && teamId !== null && (
        <NameDialog
          title="New project"
          label="Name"
          onClose={() => setDialog(null)}
          onSubmit={async (name) => {
            const created = await api<Project>(`/teams/${teamId}/projects`, {
              method: 'POST',
              body: JSON.stringify({ name }),
            })
            setProjects((rows) => [...rows, created])
            setPickedProjectId(created.id)
          }}
        />
      )}
      {dialog === 'task' && projectId !== null && (
        <NameDialog
          title="New task"
          label="Title"
          onClose={() => setDialog(null)}
          onSubmit={async (title) => {
            const created = await api<Task>(`/projects/${projectId}/tasks`, {
              method: 'POST',
              body: JSON.stringify({ title }),
            })
            setTasks((rows) => [...rows, created])
            setLoadedProjectId(projectId)
          }}
        />
      )}
      {dialog === 'members' && teamId !== null && (
        <MembersDialog
          teamId={teamId}
          members={members}
          canManage={canManage}
          canInviteAdmin={Boolean(user?.is_superuser || role === 'owner')}
          onChange={(next) => setMembers(next)}
          onClose={() => setDialog(null)}
        />
      )}
      {openTaskId !== null && projectId !== null && (
        <TaskDialog
          taskId={openTaskId}
          projectId={projectId}
          members={members}
          canManage={canManage}
          onSaved={(saved) => setTasks((rows) => rows.map((task) => (task.id === saved.id ? saved : task)))}
          onDeleted={(id) => setTasks((rows) => rows.filter((task) => task.id !== id))}
          onClose={() => setOpenTaskId(null)}
        />
      )}
    </div>
  )
}

function NameDialog({
  title,
  label,
  onSubmit,
  onClose,
}: {
  title: string
  label: string
  onSubmit: (value: string) => Promise<void>
  onClose: () => void
}) {
  const [value, setValue] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function submit(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await onSubmit(value)
      onClose()
    } catch (err) {
      setError(message(err))
      setBusy(false)
    }
  }

  return (
    <Dialog title={title}>
      <form className="stack-form" onSubmit={submit}>
        <label className="field">
          {label}
          <input value={value} onChange={(e) => setValue(e.target.value)} required />
        </label>
        {error && <p className="error">{error}</p>}
        <div className="buttons">
          <button type="button" onClick={onClose}>
            Cancel
          </button>
          <button type="submit" disabled={busy}>
            OK
          </button>
        </div>
      </form>
    </Dialog>
  )
}

function MembersDialog({
  teamId,
  members,
  canManage,
  canInviteAdmin,
  onChange,
  onClose,
}: {
  teamId: number
  members: Member[]
  canManage: boolean
  canInviteAdmin: boolean
  onChange: (members: Member[]) => void
  onClose: () => void
}) {
  const [email, setEmail] = useState('')
  const [role, setRole] = useState<'member' | 'admin'>('member')
  const [error, setError] = useState<string | null>(null)

  async function invite(event: FormEvent) {
    event.preventDefault()
    setError(null)
    try {
      const found = await api<Array<{ id: number }>>(`/users?email=${encodeURIComponent(email)}`)
      if (found.length === 0) {
        setError('No user with that email')
        return
      }
      const created = await api<Member>(`/teams/${teamId}/members`, {
        method: 'POST',
        body: JSON.stringify({ user_id: found[0].id, role }),
      })
      onChange([...members, created])
      setEmail('')
    } catch (err) {
      setError(message(err))
    }
  }

  async function remove(userId: number) {
    setError(null)
    try {
      await api(`/teams/${teamId}/members/${userId}`, { method: 'DELETE' })
      onChange(members.filter((member) => member.user_id !== userId))
    } catch (err) {
      setError(message(err))
    }
  }

  return (
    <Dialog title="Members">
      <div className="sunken" style={{ maxHeight: 160 }}>
        <table className="grid">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {members.map((member) => (
              <tr key={member.user_id}>
                <td>{member.user.full_name}</td>
                <td>{member.user.email}</td>
                <td>{member.role}</td>
                <td>
                  {canManage && member.role !== 'owner' && (
                    <button type="button" onClick={() => remove(member.user_id)}>
                      Remove
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {canManage && (
        <form className="stack-form" onSubmit={invite}>
          <label className="field">
            Email
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </label>
          <label className="field">
            Role
            <select value={role} onChange={(e) => setRole(e.target.value as 'member' | 'admin')}>
              <option value="member">Member</option>
              {canInviteAdmin && <option value="admin">Admin</option>}
            </select>
          </label>
          {error && <p className="error">{error}</p>}
          <div className="buttons">
            <button type="button" onClick={onClose}>
              Close
            </button>
            <button type="submit">Invite</button>
          </div>
        </form>
      )}
      {!canManage && (
        <div className="buttons">
          <button type="button" onClick={onClose}>
            Close
          </button>
        </div>
      )}
    </Dialog>
  )
}
