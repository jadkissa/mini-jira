import { useEffect, useState, type FormEvent } from 'react'

import { api } from '../api/client'
import type { Activity, Comment, Label, Member, Task } from '../api/types'
import { Dialog } from '../components/Dialog'
import { message } from '../components/message'

export function TaskDialog({
  taskId,
  projectId,
  members,
  canManage,
  onSaved,
  onDeleted,
  onClose,
}: {
  taskId: number
  projectId: number
  members: Member[]
  canManage: boolean
  onSaved: (task: Task) => void
  onDeleted: (taskId: number) => void
  onClose: () => void
}) {
  const [task, setTask] = useState<Task | null>(null)
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [status, setStatus] = useState<Task['status']>('todo')
  const [priority, setPriority] = useState<Task['priority']>('medium')
  const [duration, setDuration] = useState('')
  const [assigneeId, setAssigneeId] = useState('')
  const [comments, setComments] = useState<Comment[]>([])
  const [comment, setComment] = useState('')
  const [labels, setLabels] = useState<Label[]>([])
  const [projectLabels, setProjectLabels] = useState<Label[]>([])
  const [labelId, setLabelId] = useState('')
  const [labelName, setLabelName] = useState('')
  const [activity, setActivity] = useState<Activity[]>([])
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    let active = true
    Promise.all([
      api<Task>(`/tasks/${taskId}`),
      api<Comment[]>(`/tasks/${taskId}/comments`),
      api<Label[]>(`/tasks/${taskId}/labels`),
      api<Label[]>(`/projects/${projectId}/labels`),
      api<Activity[]>(`/tasks/${taskId}/activity`),
    ])
      .then(([nextTask, nextComments, nextLabels, nextProjectLabels, nextActivity]) => {
        if (!active) return
        setTask(nextTask)
        setTitle(nextTask.title)
        setDescription(nextTask.description ?? '')
        setStatus(nextTask.status)
        setPriority(nextTask.priority)
        setDuration(nextTask.duration_days?.toString() ?? '')
        setAssigneeId(nextTask.assignee_id?.toString() ?? '')
        setComments(nextComments)
        setLabels(nextLabels)
        setProjectLabels(nextProjectLabels)
        setActivity(nextActivity)
      })
      .catch((err) => {
        if (active) setError(message(err))
      })
    return () => {
      active = false
    }
  }, [taskId, projectId])

  async function save(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    try {
      const saved = await api<Task>(`/tasks/${taskId}`, {
        method: 'PATCH',
        body: JSON.stringify({
          title,
          description: description || null,
          status,
          priority,
          duration_days: duration === '' ? null : Number(duration),
          assignee_id: assigneeId === '' ? null : Number(assigneeId),
        }),
      })
      onSaved(saved)
      onClose()
    } catch (err) {
      setError(message(err))
      setBusy(false)
    }
  }

  async function remove() {
    setBusy(true)
    setError(null)
    try {
      await api(`/tasks/${taskId}`, { method: 'DELETE' })
      onDeleted(taskId)
      onClose()
    } catch (err) {
      setError(message(err))
      setBusy(false)
    }
  }

  async function addComment(event: FormEvent) {
    event.preventDefault()
    setError(null)
    try {
      const created = await api<Comment>(`/tasks/${taskId}/comments`, {
        method: 'POST',
        body: JSON.stringify({ body: comment }),
      })
      setComments((rows) => [...rows, created])
      setComment('')
    } catch (err) {
      setError(message(err))
    }
  }

  async function attachLabel(event: FormEvent) {
    event.preventDefault()
    setError(null)
    try {
      const attached = await api<Label>(`/tasks/${taskId}/labels`, {
        method: 'POST',
        body: JSON.stringify({ label_id: Number(labelId) }),
      })
      setLabels((rows) => [...rows, attached])
      setLabelId('')
    } catch (err) {
      setError(message(err))
    }
  }

  async function createLabel(event: FormEvent) {
    event.preventDefault()
    setError(null)
    try {
      const created = await api<Label>(`/projects/${projectId}/labels`, {
        method: 'POST',
        body: JSON.stringify({ name: labelName }),
      })
      setProjectLabels((rows) => [...rows, created])
      setLabelName('')
    } catch (err) {
      setError(message(err))
    }
  }

  async function removeLabel(id: number) {
    setError(null)
    try {
      await api(`/tasks/${taskId}/labels/${id}`, { method: 'DELETE' })
      setLabels((rows) => rows.filter((label) => label.id !== id))
    } catch (err) {
      setError(message(err))
    }
  }

  return (
    <Dialog title={task ? `Task ${task.id}` : 'Task'}>
      {task === null && !error ? (
        <p>Loading…</p>
      ) : (
        <div className="stack-form">
          <form id="task-form" className="stack-form" onSubmit={save}>
          <label className="field">
            Title
            <input value={title} onChange={(e) => setTitle(e.target.value)} required />
          </label>
          <label className="field">
            Details
            <textarea value={description} onChange={(e) => setDescription(e.target.value)} />
          </label>
          <label className="field">
            Status
            <select value={status} onChange={(e) => setStatus(e.target.value as Task['status'])}>
              <option value="todo">To do</option>
              <option value="in_progress">In progress</option>
              <option value="done">Done</option>
            </select>
          </label>
          <label className="field">
            Priority
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value as Task['priority'])}
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </label>
          <label className="field">
            Days
            <input
              type="number"
              min={0}
              value={duration}
              onChange={(e) => setDuration(e.target.value)}
            />
          </label>
          <label className="field">
            Assignee
            <select value={assigneeId} onChange={(e) => setAssigneeId(e.target.value)}>
              <option value="">Nobody</option>
              {members.map((member) => (
                <option key={member.user_id} value={member.user_id}>
                  {member.user.full_name}
                </option>
              ))}
            </select>
          </label>
          </form>
          <p>
            Labels:{' '}
            {labels.length === 0
              ? 'none'
              : labels.map((label) => (
                  <button key={label.id} type="button" onClick={() => removeLabel(label.id)}>
                    {label.name} x
                  </button>
                ))}
          </p>
          <form className="toolbar" onSubmit={attachLabel}>
            <select value={labelId} onChange={(e) => setLabelId(e.target.value)} required>
              <option value="">Label</option>
              {projectLabels
                .filter((label) => !labels.some((attached) => attached.id === label.id))
                .map((label) => (
                  <option key={label.id} value={label.id}>
                    {label.name}
                  </option>
                ))}
            </select>
            <button type="submit">Attach</button>
          </form>
          {canManage && (
            <form className="toolbar" onSubmit={createLabel}>
              <input
                value={labelName}
                onChange={(e) => setLabelName(e.target.value)}
                placeholder="New label"
                required
              />
              <button type="submit">Create</button>
            </form>
          )}
          <div className="sunken" style={{ maxHeight: 80 }}>
            {comments.length === 0 ? (
              <p className="muted">No comments.</p>
            ) : (
              comments.map((item) => (
                <p key={item.id} className="muted">
                  {item.body}
                </p>
              ))
            )}
          </div>
          <form className="toolbar" onSubmit={addComment}>
            <input value={comment} onChange={(e) => setComment(e.target.value)} required />
            <button type="submit">Comment</button>
          </form>
          <div className="sunken" style={{ maxHeight: 80 }}>
            {activity.length === 0 ? (
              <p className="muted">No activity.</p>
            ) : (
              activity.map((item) => (
                <p key={item.id} className="muted">
                  {item.action}
                  {item.new_value ? `: ${item.new_value}` : ''}
                </p>
              ))
            )}
          </div>
          {error && <p className="error">{error}</p>}
          <div className="buttons">
            <button type="button" onClick={onClose}>
              Cancel
            </button>
            {canManage && (
              <button type="button" onClick={remove} disabled={busy}>
                Delete
              </button>
            )}
            <button type="submit" form="task-form" disabled={busy || task === null}>
              Save
            </button>
          </div>
        </div>
      )}
    </Dialog>
  )
}
