// Mirrors the backend's Pydantic response schemas (backend/app/schemas).

export interface User {
  id: number
  email: string
  full_name: string
  is_active: boolean
  is_superuser: boolean
  created_at: string
}

export interface Tokens {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface Team {
  id: number
  name: string
  owner_id: number
  created_at: string
}

export interface Project {
  id: number
  name: string
  description: string | null
  team_id: number
  created_at: string
  updated_at: string
}

export interface Member {
  user_id: number
  role: string
  user: { id: number; email: string; full_name: string }
}

export interface TeamDetail extends Team {
  members: Member[]
}

export interface Task {
  id: number
  title: string
  description: string | null
  status: 'todo' | 'in_progress' | 'done'
  priority: 'low' | 'medium' | 'high'
  duration_days: number | null
  project_id: number
  assignee_id: number | null
  delivery_date: string | null
}

export interface Comment {
  id: number
  task_id: number
  author_id: number | null
  body: string
  created_at: string
}

export interface Label {
  id: number
  project_id: number
  name: string
  color: string | null
}

export interface Activity {
  id: number
  action: string
  old_value: string | null
  new_value: string | null
  created_at: string
}
